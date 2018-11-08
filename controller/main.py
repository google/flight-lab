# Copyright 2018 Flight Lab authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Controller server and client app."""

import gflags
import logging
import sys
import threading
import api
import cherrypy

from common import pattern
from common import net
from components import factory
from concurrent import futures
import controller
import flask
import flask_cors
import grpc
from protos import controller_pb2
from services import client
from google.apputils import appcommands
from google.protobuf import text_format

FLAGS = gflags.FLAGS

_CONTROL_SERVICE_GRPC_PORT = 9000
_CLIENT_SERVICE_GRPC_PORT = 9001

gflags.DEFINE_string('config', 'config.protoascii',
                     'Path to system configuration file.')


class ControllerApp(pattern.Logger, appcommands.Cmd):
  """Base class for server and client app.

  The base class provides common infrastructure, including component factory and
  configuration protobuf.
  """

  def __init__(self, *args, **kwargs):
    super(ControllerApp, self).__init__(*args, **kwargs)
    self._factory = factory.ComponentFactory()
    self._stop_event = threading.Event()
    self._machine_config = None
    self._master_machine_config = None

    self._system_config = controller_pb2.System()
    with open(FLAGS.config, 'r') as f:
      config_text = f.read()
      text_format.Merge(config_text, self._system_config)

  @property
  def factory(self):
    """Gets factory for creating all components."""
    return self._factory

  @property
  def system_config(self):
    """Gets configuration protobuf for entire system.

    Returns:
      flightlab.System protobuf.
    """
    return self._system_config

  @property
  def machine_config(self):
    """Gets configuration protobuf for current machine.

    Returns:
      flightlab.Machine protobuf.
    Raises:
      Exception: if configuration for current machine doesn't exist.
    """
    if not self._machine_config:
      ip = net.get_ip()
      self._machine_config = next(
          (x for x in self.system_config.machines if x.ip == ip), None)
      if not self._machine_config:
        raise Exception('No config found for this machine.')
    return self._machine_config

  @property
  def master_machine_config(self):
    """Gets configuration protobuf for master machine.

    Returns:
      flightlab.Machine protobuf.
    Raises:
      Exception: if configuration for master machine doesn't exist.
    """
    if not self._master_machine_config:
      self._master_machine_config = next(
          (x for x in self.system_config.machines
           if x.name == self.system_config.master_machine_name))
      if not self._master_machine_config:
        raise Exception('Master machine config not found.')
    return self._master_machine_config

  @property
  def is_master(self):
    """Whether current machine is master machine."""
    return self.machine_config.name == self.system_config.master_machine_name

  def Run(self, argv):
    """Runs the app."""
    self._initialize()
    self.logger.info('Running...')
    try:
      while not self._stop_event.is_set():
        self._stop_event.wait(1)
    except KeyboardInterrupt:
      self.logger.info('Aborting by user.')
    finally:
      self.close()

  def close(self):
    pass

  def exit(self):
    self._stop_event.set()

  def _initialize(self):
    pass


class ControllerServerApp(ControllerApp):
  """Controller server app.

  The server app provides gRPC service for clients to connect and receive
  commands.
  It also starts a web server to provide HTTP GET APIs for frontend. See api.py
  for more details.
  """

  def __init__(self, *args, **kwargs):
    super(ControllerServerApp, self).__init__(*args, **kwargs)
    self._grpc_server = None
    self._control_service = None
    self._web = None
    self._api_service = None

  def close(self):
    self._server.stop(None)
    self._control_service.stop()
    cherrypy.engine.exit()
    super(ControllerServerApp, self).close()

  def _initialize(self):
    super(ControllerServerApp, self)._initialize()

    # Start control service
    self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=50))
    self._control_service = controller.ControlService(
        server=self._server, system_config=self.system_config)
    self._control_service.on('status_changed', self._on_status_changed)
    self._server.add_insecure_port(
        '[::]:{0}'.format(_CONTROL_SERVICE_GRPC_PORT))
    self._server.start()

    # Start web server
    self._web = flask.Flask('FlightLab')
    flask_cors.CORS(self._web)
    self._api_service = api.ApiService(
        web=self._web,
        system_config=self.system_config,
        control_service=self._control_service)
    cherrypy.tree.graft(self._web, '/')
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.config.update({
        'global': {
            'environment': 'production'
        },
    })
    cherrypy.engine.start()

  def _on_status_changed(self):
    counter = {
        controller_pb2.Component.UNKNOWN: 0,
        controller_pb2.Component.OFF: 0,
        controller_pb2.Component.TRANSIENT: 0,
        controller_pb2.Component.ON: 0,
    }
    for machine in self.system_config.machines:
      for component in machine.components:
        if component.status != controller_pb2.Component.NOT_APPLICABLE:
          counter[component.status] += 1

    if counter[controller_pb2.Component.UNKNOWN] > 0:
      self.system_config.state = controller_pb2.System.UNKNOWN
    elif counter[controller_pb2.Component.TRANSIENT] > 0:
      self.system_config.state = controller_pb2.System.TRANSIENT
    else:
      if (counter[controller_pb2.Component.ON] > 0 and
          counter[controller_pb2.Component.OFF] > 0):
        self.system_config.state = controller_pb2.System.TRANSIENT
      elif counter[controller_pb2.Component.ON] > 0:
        self.system_config.state = controller_pb2.System.ON
      else:
        self.system_config.state = controller_pb2.System.OFF


class ControllerClientApp(ControllerApp):
  """Controller client app.

  The client app loads components per configuration and runs per commands
  received from server app.
  """

  def __init__(self, *args, **kwargs):
    super(ControllerClientApp, self).__init__(*args, **kwargs)
    self._control_client = None
    self._components = []

  def close(self):
    self.logger.info('Closing app...')

    self._server.stop(None)
    self._client_service.close()

    self._control_client.stop()

    for component in self._components:
      if isinstance(component, pattern.Closable):
        component.close()
    self._components = []

    super(ControllerClientApp, self).close()

  def _initialize(self):
    super(ControllerClientApp, self)._initialize()
    self._initialize_client()
    self._initialize_components()

  def _initialize_components(self):
    for component_config in self.machine_config.components:
      component = self.factory.create_component(component_config)
      component.on('status_changed', self._on_component_status_changed)
      self._components.append(component)

  def _initialize_client(self):
    # Start remote service
    self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    self._client_service = client.ClientService(
        server=self._server, machine_config=self.machine_config)
    self._server.add_insecure_port(
        '[::]:{0}'.format(_CLIENT_SERVICE_GRPC_PORT))
    self._server.start()

    # Start control client
    target = '{0}:{1}'.format(self.master_machine_config.ip,
                              _CONTROL_SERVICE_GRPC_PORT)
    grpc_channel = grpc.insecure_channel(target)
    self._control_client = controller.ControlClient(
        machine_config=self.machine_config,
        grpc_channel=grpc_channel,
        command_callback=self._on_command)
    self._control_client.start()

  def _on_command(self, command):
    if command == controller_pb2.SystemCommand.EXIT:
      self.exit()
      return

    if command == controller_pb2.SystemCommand.DEBUG:
      self.logger.debug('{0} threads are alive.'.format(
          threading.active_count()))
      for thread in threading.enumerate():
        self.logger.debug('Thread (name="{0}")'.format(thread.name))
      return

    for component in self._components:
      pattern.run_as_thread(
          name='{0}.on_command({1})'.format(component.name, command),
          target=component.on_command,
          kwargs={'command': command})

  def _on_component_status_changed(self, component):
    self._control_client.update_status(component.proto)


def init_log():
  """Initializes logging settings."""
  logger = logging.getLogger('')
  logger.setLevel('DEBUG')
  console_handler = logging.StreamHandler()
  console_handler.setFormatter(
      logging.Formatter('%(levelname)-8s %(name)-12s: %(message)s'))
  logger.addHandler(console_handler)


def main(argv):
  init_log()
  appcommands.AddCmd(
      'server', ControllerServerApp, help_full='Runs controller server.')
  appcommands.AddCmd(
      'client', ControllerClientApp, help_full='Runs controller client.')


if __name__ == '__main__':
  appcommands.Run()
