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
"""gRPC service handler and client warapper for server-client communications."""

import grpc
import Queue
import threading
from google.protobuf import empty_pb2

from common import pattern
from protos import controller_pb2
from protos import controller_pb2_grpc


class ControlService(controller_pb2_grpc.ControlServiceServicer,
                     pattern.Logger, pattern.EventEmitter):
  """Provider for flightlab.ControlService.

  Events:
    "status_changed": when status of any component from any machine is changed.
  """

  def __init__(self, server, system_config, *args, **kwargs):
    """Creates a ControlService instance.

    Args:
      server: gRPC server.
      system_config: configuration protobuf for the entire system.
      *args: additional unnamed arguments.
      **kwargs: additional named arguments.
    """
    super(ControlService, self).__init__(*args, **kwargs)
    self._system_config = system_config
    self._stopped = False
    controller_pb2_grpc.add_ControlServiceServicer_to_server(self, server)

    self._command = None
    self._command_changed_events = []
    self._notification_queues = []

  def send_command(self, command):
    """Sends command to all clients.

    Args:
      command: flightlab.SystemCommand.
    """
    self._command = command
    for event in self._command_changed_events:
      event.set()

  def stop(self):
    """Stops the service and all on-going streaming calls."""
    self._stopped = True
    for event in self._command_changed_events:
      event.set()

  def GetConfig(self, _, context):
    """Handler for GetConfig gRPC call.

    This handler returns the entire system configuration.

    Args:
      context: gRPC context.
    Returns:
      flightlab.System protobuf.
    """
    return self._system_config

  def WatchConfig(self, _, context):
    self.logger.info('New client starts to watch config...')
    queue = Queue.Queue(maxsize=100)
    self._notification_queues.append(queue)
    try:
      while not self._stopped:
        try:
          queue.get(block=True, timeout=1)
          self.logger.info('Notifying client config change...')
          yield self._system_config
        except Queue.Empty:
          pass
    finally:
      self._notification_queues.remove(queue)

  def UpdateStatus(self, machine_status, context):
    """Handler for UpdateStatus gRPC call.

    This handler receives status update of one or more components from a client,
    updates to system configuration, and triggers "status_changed" event.

    Args:
      machine_status: flightlab.MachineStatus protobuf.
      context: gRPC context.
    Returns:
      google.protobuf.Empty.
    """
    machine = next((x for x in self._system_config.machines
                    if x.name == machine_status.name), None)
    if not machine:
      self.logger.warn('Machine %s not found.', machine_status.name)
      return

    for component_status in machine_status.component_status:
      component = next((x for x in machine.components
                        if x.name == component_status.name), None)
      if not component:
        self.logger.warn('Component %s not found.', component_status.name)
        continue

      self.logger.info('Status update: {0}/{1} => {2}'.format(
          machine.name, component.name,
          controller_pb2.Component.Status.Name(component_status.status)))

      kind = component_status.WhichOneof('kind')
      status = getattr(component_status, kind)
      kind = component.WhichOneof('kind')
      settings = getattr(component, kind)
      settings.status = status
      component.status = component_status.status

    for queue in self._notification_queues:
      self.logger.info('Notifying clients watching for status...')
      try:
        queue.put(machine_status, block=False)
      except Queue.Full:
        pass

    self.emit('status_changed')

    return empty_pb2.Empty()

  def WatchStatus(self, _, context):
    """Handler for WatchStatus gRPC call.

    This handler streams component status update from server to client.

    Args:
      context: gRPC context.
    Yields:
      flightlab.MachineStatus.
    """
    self.logger.info('New client starts to watch status...')
    queue = Queue.Queue(maxsize=100)
    self._notification_queues.append(queue)
    try:
      while not self._stopped:
        try:
          status = queue.get(block=True, timeout=1)
          self.logger.info('Notifying client status change...')
          yield status
        except Queue.Empty:
          pass
    finally:
      self._notification_queues.remove(queue)

  def WatchCommand(self, machine_id, context):
    """Handler for WatchCommand gRPC call.

    This handler streams commands from server to client.

    Args:
      machine_id: a flightlab.MachineId protobuf identifying the client.
      context: gRPC context.
    Yields:
      flightlab.SystemCommand.
    """
    self.logger.info('"{0}" is listening to commands...'.format(
        machine_id.name))
    event = threading.Event()
    self._command_changed_events.append(event)
    try:
      while not self._stopped:
        if event.wait(1):
          if self._command:
            name = controller_pb2.SystemCommand.Command.Name(self._command)
            self.logger.info('{0} => {1}'.format(name, machine_id.name))
            yield controller_pb2.SystemCommand(command=self._command)
          event.clear()
    finally:
      self.logger.info('"{0}" stopped listening to command.'.format(
          machine_id.name))
      self._command_changed_events.remove(event)


class ControlClient(pattern.Logger):
  """Wrapper for client to use flightlab.ControlService.

  This wrapper listens to commands from server and passes to a callback.
  It also updates component status to server.
  """
  _GRPC_RECONNECT_INTERVAL = 5  # sec

  def __init__(self, machine_config, grpc_channel, command_callback, *args,
               **kwargs):
    """Creates ControlClient instance.

    Args:
      machine_config: configuration protobuf for current machine.
      grpc_channel: a channel for gRPC connection.
      command_callback: a function to callback when command is received.
      *args: additional unnamed arguments.
      **kwargs: additional named arguments.
    """
    super(ControlClient, self).__init__(*args, **kwargs)
    self._machine_config = machine_config
    self._command_callback = command_callback
    self._grpc_channel = grpc_channel
    self._stub = controller_pb2_grpc.ControlServiceStub(self._grpc_channel)
    self._thread = None
    self._stopped = False

  def start(self):
    """Starts the connection to server.

    Whenever connection is interrupted, it will repeatedly attempt to reconnect.
    """
    if self._thread:
      self.logger.warn('Already started.')
      return

    self._stopped = False
    self._restart()

  def stop(self):
    """Stops the connection to server."""
    if not self._thread:
      self.logger.warn('Already stopped.')
      return

    self._stopped = True
    self._grpc_channel.close()
    self._thread.join()
    self._thread = None

  def update_status(self, component_proto):
    """Updates component status to server.

    Args:
      component_proto: a flightlab.Component protobuf.
    """
    component_status = controller_pb2.ComponentStatus(
        name=component_proto.name, status=component_proto.status)
    kind = component_proto.WhichOneof('kind')
    if kind == 'projector':
      component_status.projector_status = component_proto.projector.status
    elif kind == 'app':
      component_status.app_status = component_proto.app.status
    elif kind == 'windows_app':
      component_status.windows_app_status = component_proto.windows_app.status
    elif kind == 'badger':
      component_status.badger_status = component_proto.badger.status
    else:
      self.logger.warn('%s is not a supported component status', kind)

    machine_status = controller_pb2.MachineStatus(
        name=self._machine_config.name, component_status=[component_status])
    try:
      self._stub.UpdateStatus(machine_status)
    except grpc.RpcError as e:
      self.logger.warn('Failed to update status: %s', e)

  def update_all_status(self):
    """Updates status of all components to server."""
    machine_status = controller_pb2.MachineStatus(
        name=self._machine_config.name)
    for component in self._machine_config.components:
      kind = component.WhichOneof('kind')
      if kind == 'projector':
        component_status = machine_status.component_status.add(
            name=component.name, status=component.status)
        component_status.projector_status = component.projector.status
      elif kind == 'app':
        component_status = machine_status.component_status.add(
            name=component.name, status=component.status)
        component_status.app_status = component.app.status
      elif kind == 'windows_app':
        component_status = machine_status.component_status.add(
            name=component.name, status=component.status)
        component_status.windows_app_status = component.windows_app.status

    try:
      self._stub.UpdateStatus(machine_status)
    except grpc.RpcError as e:
      self.logger.warn('Failed to update status: %s', e)

  def _watch(self, response):
    """Listens to command from server and passes to callback.

    Args:
      response: an iterable containing flightlab.SystemCommand.
    """
    try:
      for system_command in response:
        self.logger.info('Received system command {0}.'.format(
            controller_pb2.SystemCommand.Command.Name(system_command.command)))
        self._command_callback(system_command.command)
    except grpc.RpcError:
      if not self._stopped:
        self._restart()

  def _restart(self):
    """Attempt to reconnect to server and retry after an interval if fails."""
    self._thread = None
    try:
      response = self._stub.WatchCommand(
          controller_pb2.MachineId(name=self._machine_config.name))
      self._thread = threading.Thread(
          target=self._watch, kwargs={
              'response': response
          })
      self._thread.start()

      self.update_all_status()
    except grpc.RpcError:
      if not self._stopped:
        threading.Timer(self._GRPC_RECONNECT_INTERVAL, self._restart).start()
