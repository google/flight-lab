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
"""Windows automation library.

This library provides classes to control Windows application and UI.
"""

import os
import psutil
import subprocess
import time

from common import pattern


class Application(pattern.EventEmitter, pattern.Worker, pattern.Logger):
  """Class to represent an application.

  Events:
    "starting": right before the application is about to start.
    "started": right after the application started.
    "stopping": right before the application is about to be terminated.
    "stopped": right after the application is terminated.
  """

  def __init__(self,
               name,
               bin_path,
               arguments=[],
               working_dir=None,
               restart_on_crash=False,
               env=None,
               *args,
               **kwargs):
    """Creates an Application instance.

    Args:
      name: name of the application.
      bin_path: the path of the application executable.
      arguments: list of arguments.
      restart_on_crash: if True, restarts the application if it exited
                        unexpectedly.
      env: dictionary of environment variables.
    """
    super(Application, self).__init__(
        worker_name='Application ({0})'.format(name), *args, **kwargs)
    self._name = name
    self._bin_path = bin_path.lower()
    self._arguments = arguments
    self._working_dir = working_dir or os.path.dirname(self._bin_path)
    self._restart_on_crash = restart_on_crash
    if env:
      self._env = os.environ.copy()
      self._env.update(env)
    else:
      self._env = None

    self._app_proc = None

  @property
  def name(self):
    """Gets name of the application."""
    return self._name

  def stop(self):
    """Stops the application."""
    super(Application, self).stop()
    self.kill()

  def has_running_instance(self):
    """Checks if any instance of the application is running."""
    return self._get_proc() is not None

  def kill(self):
    """Terminates all the applications of the same executable."""
    while True:
      proc = self._get_proc()
      if not proc:
        return

      self.logger.debug('[App - {0}] Terminating instance (pid={1})...'.format(
          self._name, proc.pid))
      try:
        proc.kill()
      except psutil.NoSuchProcess:
        self.logger.debug('[App - {0}] Instance exited.'.format(self._name))
        return

      self.logger.debug('[App - {0}] Waiting for instance to exit...'.format(
          self._name))
      while proc:
        proc = self._get_proc()
        if proc:
          time.sleep(0.1)
      self.logger.debug('[App - {0}] Instance exited.'.format(self._name))

  def _on_start(self):
    # Kill instance(s) that are not started here.
    self.kill()
    self._app_proc = self._launch_app()

  def _on_run(self):
    if self._app_proc:
      if self._app_proc.poll() is not None:
        self.logger.info('[App - {0}] Exited unexpectedly.'.format(self._name))
        self._app_proc = None
        self.emit('stopped', self)

    if not self._app_proc:
      if self._restart_on_crash:
        self._app_proc = self._launch_app()

    self._sleep(1)

  def _on_stop(self):
    if self._app_proc:
      self.emit('stopping', self)
      self._app_proc.kill()
      self._app_proc = None
      self.emit('stopped', self)

  def _launch_app(self):
    args = [self._bin_path] + self._arguments
    self.logger.debug('[App - {0}] Executing "{1}"...'.format(
        self._name, ' '.join(args)))

    self.emit('starting', self)

    proc = None
    try:
      proc = subprocess.Popen(
          args, cwd=self._working_dir, close_fds=True, env=self._env)
    except Exception as e:
      self.logger.debug('[App - {0}] Failed to launch. {1}'.format(
          self._name, e))
      return None

    self.emit('started', self)
    return proc

  def _get_proc(self):
    target_cmd = (' '.join([self._bin_path] + self._arguments)).lower()
    for proc in psutil.process_iter():
      cmd = ''
      try:
        cmd = (' '.join(proc.cmdline())).lower()
      except:
        pass
      if cmd == target_cmd:
        return proc
    return None