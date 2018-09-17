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

import win32con
import subprocess
import threading

from components import base
from protos import controller_pb2
from utils import windows


class WindowsAppComponent(base.Component):
  """Component to manage execution of app on Windows platform.

  This component can launch app, alter window position and styles, restart app
  upon crash, and stop app.

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
    super(WindowsAppComponent, self).__init__(proto, *args, **kwargs)

    if self.settings.run_option == controller_pb2.WindowsApp.NORMAL:
      self._status_mapping = {
          controller_pb2.WindowsApp.UNKNOWN: controller_pb2.Component.UNKNOWN,
          controller_pb2.WindowsApp.RUNNING: controller_pb2.Component.ON,
          controller_pb2.WindowsApp.NOT_RUNNING: controller_pb2.Component.OFF,
      }
    else:
      self._status_mapping = {
          controller_pb2.WindowsApp.UNKNOWN:
          controller_pb2.Component.NOT_APPLICABLE,
          controller_pb2.WindowsApp.RUNNING:
          controller_pb2.Component.NOT_APPLICABLE,
          controller_pb2.WindowsApp.NOT_RUNNING:
          controller_pb2.Component.NOT_APPLICABLE,
      }

    self._app = windows.WindowsApplication(
        name=self.name,
        bin_path=self.settings.executable_path,
        arguments=(list(self.settings.arguments)
                   if self.settings.arguments else []),
        working_dir=self.settings.working_dir,
        restart_on_crash=(self.settings.restart_on_crash
                          if self.settings.restart_on_crash else False),
        start_minimized=(self.settings.start_minimized
                         if self.settings.start_minimized else False))
    self._app.on('started', self._on_app_started)
    self._app.on('stopped', self._on_app_stopped)

    self._windows = []
    for window_config in self.settings.windows:
      window = windows.Window(
          name=window_config.name,
          class_name=window_config.class_name
          if window_config.class_name else None,
          window_name=window_config.window_name
          if window_config.window_name else None)
      self._windows.append((window, window_config))
      window.on('created', self._adjust_window)

    self._monitor = threading.Timer(1, self._check_status)
    self._monitor.start()

    if self.settings.run_option == controller_pb2.WindowsApp.RUN_ALWAYS:
      self._start_app()

  def close(self):
    if self._monitor:
      self._monitor.cancel()
      self._monitor = None
    self._stop_app()

    super(WindowsAppComponent, self).close()

  def _check_status(self):
    if self._app.has_running_instance():
      new_status = controller_pb2.WindowsApp.RUNNING
    else:
      new_status = controller_pb2.WindowsApp.NOT_RUNNING
    if self.settings.status != new_status:
      self.settings.status = new_status
      self.proto.status = self._status_mapping[new_status]
      self.emit('status_changed', self)

  def _start(self):
    if self.settings.run_option == controller_pb2.WindowsApp.RUN_WHEN_OFF:
      self._stop_app()
    elif self.settings.run_option == controller_pb2.WindowsApp.STOP_ONLY:
      pass
    elif self.settings.run_option == controller_pb2.WindowsApp.RUN_ALWAYS:
      pass
    else:
      self._start_app()

  def _stop(self):
    if self.settings.run_option == controller_pb2.WindowsApp.RUN_WHEN_OFF:
      self._start_app()
    elif self.settings.run_option == controller_pb2.WindowsApp.STOP_ONLY:
      self._stop_app()
    elif self.settings.run_option == controller_pb2.WindowsApp.RUN_ALWAYS:
      pass
    else:
      self._stop_app()

  def _restart(self):
    if self.settings.run_option == controller_pb2.WindowsApp.RUN_WHEN_OFF:
      pass
    elif self.settings.run_option == controller_pb2.WindowsApp.STOP_ONLY:
      pass
    elif self.settings.run_option == controller_pb2.WindowsApp.RUN_ALWAYS:
      pass
    else:
      self._stop_app()
      self._start_app()

  def _start_app(self):
    self.logger.info('[App - {0}] Starting...'.format(self.name))

    for (window, _) in self._windows:
      window.start()
    self._app.start()

  def _stop_app(self):
    self.logger.info('[App - {0}] Stopping...'.format(self.name))

    self._app.stop()
    for (window, _) in self._windows:
      window.stop()

  def _adjust_window(self, window):
    self.logger.info('[App - {0}] [Window - {1}] Adjusting...'.format(
        self.name, window.name))

    config = next((x[1] for x in self._windows if x[0] == window), None)
    assert config
    if config.borderless:
      self.logger.info('[App - {0}] [Window - {1}] Removing border...'.format(
          self.name, window.name))
      window.set_style(remove=win32con.WS_BORDER | win32con.WS_THICKFRAME
                       | win32con.WS_DLGFRAME)
    if (config.left is not None and config.top is not None and
        config.width is not None and config.height is not None):
      self.logger.info('[App - {0}] [Window - {1}] Repositioning...'.format(
          self.name, window.name))
      window.set_position(
          left=config.left,
          top=config.top,
          width=config.width,
          height=config.height)

  def _on_app_started(self, app):
    self.settings.status = controller_pb2.WindowsApp.RUNNING
    self.proto.status = self._status_mapping[controller_pb2.WindowsApp.RUNNING]
    self.emit('status_changed', self)

  def _on_app_stopped(self, app):
    self.settings.status = controller_pb2.WindowsApp.NOT_RUNNING
    self.proto.status = self._status_mapping[
        controller_pb2.WindowsApp.NOT_RUNNING]
    self.emit('status_changed', self)
