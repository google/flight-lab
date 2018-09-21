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
import win32api
import win32con
import win32gui
import win32process

from common import pattern
from utils import app

_SW_SHOW = 5
_SW_MINIMIZE = 6


class WindowNotFoundException(Exception):
  pass


class Window(pattern.EventEmitter, pattern.Worker, pattern.Logger):
  """Class to represent a given window.

  Events:
    "created": when window is found to be created
    "destroyed": when window is found to be destroyed
  """

  def __init__(self,
               name,
               class_name=None,
               window_name=None,
               pid=None,
               *args,
               **kwargs):
    """Creates a Window instance.

    Args:
      name: name of the window.
      class_name: classname attribute of the window on Windows.
      window_name: title of the window.
      pid: id of the process which owns the window.
    """
    super(Window, self).__init__(
        worker_name='Window ({0})'.format(name), *args, **kwargs)
    self._name = name
    self._class_name = class_name
    self._window_name = window_name
    self._pid = pid
    self._found = False

  @property
  def name(self):
    """Gets name of the window."""
    return self._name

  def _get_hwnd_by_pid(self, pid):
    """Gets handle of the window that belongs to a process.

    Args:
      pid: process id.
    Returns:
      Window handle.
    """

    def callback(hwnd, hwnds):
      if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid == pid:
          hwnds.append(hwnd)
      return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None

  def exists(self):
    """Checks if the window exists."""
    try:
      self.get_hwnd()
      return True
    except:
      return False

  def get_hwnd(self):
    """Gets handle of the window."""
    if self._class_name or self._window_name:
      hwnd = win32gui.FindWindow(self._class_name, self._window_name)
    elif self._pid:
      hwnd = self._get_hwnd_by_pid(self._pid)
    if not hwnd:
      raise WindowNotFoundException(
          'Window (class name={0}, window name={1}) is not found.'.format(
              self._class_name, self._window_name))
    return hwnd

  def bring_to_foreground(self):
    """Brings the window to foreground."""
    hwnd = self.get_hwnd()
    win32gui.SetForegroundWindow(hwnd)

  def set_style(self, add=None, remove=None):
    """Changes window style.

    Args:
      add: styles to add.
      remove: styles to remove.
    Returns:
      Self.
    """
    hwnd = self.get_hwnd()
    styles = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    if add:
      styles |= add
    if remove:
      styles &= ~remove
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, styles)
    return self

  def set_position(self, left, top, width, height):
    """Changes window position."""
    hwnd = self.get_hwnd()
    win32gui.SetWindowPos(hwnd, 0, left, top, width, height,
                          win32con.SWP_NOZORDER)
    return self

  def set_size(self, width, height):
    """Changes window size.

    Args:
      width: new width of the window.
      height: new height of the window.
    Returns:
      Self.
    """
    hwnd = self.get_hwnd()
    win32gui.SetWindowPos(hwnd, 0, 0, 0, width, height,
                          win32con.SWP_NOZORDER | win32con.SWP_NOMOVE)
    return self

  def minimize(self):
    """Minimizes the window."""
    hwnd = self.get_hwnd()
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    return self

  def post_message(self, message, wparam, lparam):
    """Posts Windows message to the window.

    Args:
      message: a defined Windows message.
      wparam: parameter of the message.
      lparam: parameter of the message.
    Returns:
      Self.
    """
    hwnd = self.get_hwnd()
    win32api.PostMessage(hwnd, message, wparam, lparam)
    return self

  def _on_start(self):
    self._found = False

  def _on_run(self):
    now_found = self.exists()
    if not self._found and now_found:
      self.logger.debug('[Window - {0}] Created.'.format(self.name))
      self.emit('created', self)
    elif self._found and not now_found:
      self.logger.debug('[Window - {0}] Closed.'.format(self.name))
      self.emit('destroyed', self)
    self._found = now_found

    self._sleep(1)


class WindowsApplication(app.Application):
  """Class to represent a Windows application.

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
               start_minimized=False,
               *args,
               **kwargs):
    """Creates an Application instance.

    Args:
      name: name of the application.
      bin_path: the path of the application executable.
      arguments: list of arguments.
      restart_on_crash: if True, restarts the application if it exited
                        unexpectedly.
      start_minimized: if True, the application window will be minimized after
                       start.
    """
    super(WindowsApplication,
          self).__init__(name, bin_path, arguments, working_dir,
                         restart_on_crash, *args, **kwargs)
    self._start_minimized = start_minimized

  def _launch_app(self):
    args = [self._bin_path] + self._arguments
    self.logger.debug('[App - {0}] Executing "{1}"...'.format(
        self._name, ' '.join(args)))

    self.emit('starting', self)

    proc = None
    info = subprocess.STARTUPINFO()
    if self._start_minimized:
      info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
      info.wShowWindow = _SW_MINIMIZE

    try:
      proc = subprocess.Popen(
          args,
          cwd=self._working_dir,
          creationflags=subprocess.CREATE_NEW_CONSOLE,
          close_fds=True,
          startupinfo=info)
    except Exception as e:
      self.logger.debug('[App - {0}] Failed to launch. {1}'.format(
          self._name, e))
      return None

    self.emit('started', self)
    return proc