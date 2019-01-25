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
"""Library for components related to running apps."""

import subprocess
import threading

from components import base
from protos import controller_pb2
from utils import app


class AppComponent(base.Component):
  """Component to run command-line based app on any platform.

  This component can start app, restart app upon crash, and stop app.

  Events:
    "status_changed": when status of the app is changed.
      Args:
        app_component: instance of this class.
  """

  def __init__(self, proto, *args, **kwargs):
    """Initializes the component.

    Args:
      proto: flightlab.App proto defining app details and options.
    """
    super(AppComponent, self).__init__(proto, *args, **kwargs)

    self._app = app.Application(
        name=self.name,
        bin_path=self.settings.executable_path,
        arguments=(list(self.settings.arguments)
                   if self.settings.arguments else []),
        working_dir=self.settings.working_dir,
        restart_on_crash=(self.settings.restart_on_crash
                          if self.settings.restart_on_crash else False),
        env=(self.settings.env if self.settings.env else None))
    self._app.on('started', self._on_app_started)
    self._app.on('stopped', self._on_app_stopped)

    self._monitor = threading.Timer(1, self._check_status)
    self._monitor.start()

  def close(self):
    if self._monitor:
      self._monitor.cancel()
      self._monitor = None
    self._app.stop()

  def _check_status(self):
    if self._app.has_running_instance():
      component_status = controller_pb2.Component.ON
      app_status = controller_pb2.App.RUNNING
    else:
      component_status = controller_pb2.Component.OFF
      app_status = controller_pb2.App.NOT_RUNNING

    if (self.proto.status != component_status or
        self.settings.status != app_status):
      self.proto.status = component_status
      self.settings.status = app_status
      self.emit('status_changed', self)

  def _start(self):
    self.logger.info('[App - {0}] Starting...'.format(self.name))
    self._app.start()

  def _stop(self):
    self.logger.info('[App - {0}] Stopping...'.format(self.name))
    self._app.stop()

  def _restart(self):
    self._stop()
    self._start()

  def _on_app_started(self, app):
    self.logger.info('[App - {0}] Started.'.format(self.name))
    self.settings.status = controller_pb2.App.RUNNING
    self.proto.status = controller_pb2.Component.ON
    self.emit('status_changed', self)

  def _on_app_stopped(self, app):
    self.logger.info('[App - {0}] Stopped.'.format(self.name))
    self.settings.status = controller_pb2.App.NOT_RUNNING
    self.proto.status = controller_pb2.Component.OFF
    self.emit('status_changed', self)


class CommandLineComponent(base.Component):
  """Component to run command-line based apps on any platform."""

  def _start(self):
    for cmd in self.settings.when_on:
      self.logger.info('[{0}] Running: {1}'.format(self.name, cmd))
      ret = subprocess.call(cmd)
      self.logger.info('[{0}] Done (return code={1})'.format(self.name, ret))

  def _stop(self):
    for cmd in self.settings.when_off:
      self.logger.info('[{0}] Running: {1}'.format(self.name, cmd))
      ret = subprocess.call(cmd)
      self.logger.info('[{0}] Done (return code={1})'.format(self.name, ret))