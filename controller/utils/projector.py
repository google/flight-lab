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
"""Utility to control projectors that support pjlink protocol."""

import datetime
import enum
import hashlib
import socket
import sys
import threading

from common import pattern


class Status(enum.Enum):
  OFF = '0'
  ON = '1'
  COOL_DOWN = '2'
  WARM_UP = '3'


class ProjectorException(Exception):
  pass


class Projector(pattern.EventEmitter, pattern.Worker):
  """Class to control projector that supports pjlink protocol.

  This is a partial implementation for basic power on/off operation. More can
  be added.
  """

  def __init__(self, name, address, port=4352, password=None, *args, **kwargs):
    """Creates a Projector instance.

    Args:
      name: name of the projector.
      address: ip address of the projector.
      port: port of the projector.
      password: password for initial authentication.
    """
    super(Projector, self).__init__(
        worker_name='Projector ({0})'.format(name), *args, **kwargs)
    self._name = name
    self._controller = ProjectorController(
        address=address, port=port, password=password)
    self._last_status = None

  def get_status(self):
    """Gets current status of the projector.

    Returns:
      Status.
    """
    result = self._controller.get('POWR')
    return Status(result)

  def power_on(self):
    """Powers on the projector.

    Raises:
      ProjectorException: if projector is in a state that cannot be turned on.
    """
    status = self.get_status()
    if status == Status.ON or status == Status.WARM_UP:
      return
    elif status == Status.OFF:
      self._controller.set(cmd='POWR', param='1', reset=True)
      self.emit('status_changed', self._last_status, Status.WARM_UP)
      self._last_status = Status.WARM_UP
    else:
      raise ProjectorException(
          'Projector is cooling down now. Unable to power on.')

  def power_off(self):
    """Powers off the projector.

    Raises:
      ProjectorException: if projector is in a state that cannot be turned off.
    """
    status = self.get_status()
    if status == Status.OFF or status == Status.COOL_DOWN:
      return
    elif status == Status.ON:
      self._controller.set(cmd='POWR', param='0', expectation='OK')
    else:
      raise ProjectorException(
          'Projector is warming up now. Unable to power off.')

  def _on_run(self):
    status = self.get_status()
    if self._last_status != status:
      self.emit('status_changed', self._last_status, status)
      self._last_status = status
    self._sleep(1)


class ProjectorController(object):
  """Class to implement pjlink protocol."""

  _ERRORS = {
      b'ERR1': 'undefined command',
      b'ERR2': 'out of parameter',
      b'ERR3': 'unavailable time',
      b'ERR4': 'projector failure',
  }

  # pjlink protocol states an idle connection will be terminated by projector
  # after 30 seconds. So we timeout sooner and reconnect.
  _TIMEOUT = datetime.timedelta(seconds=20)

  def __init__(self, address, port=4352, password=None):
    self._address = address
    self._port = port
    self._password = password
    self._expiration = datetime.datetime.now()
    self._controller = None
    self._lock = threading.RLock()

  def reconnect(self):
    """Reconnects to projector.

    Raises:
      ProjectorException: if unable to connect to projector.
    """
    with self._lock:
      try:
        sock = socket.create_connection((self._address, self._port), timeout=5)
      except socket.error:
        raise ProjectorException('Projector is not available.')

      if sys.version_info.major == 2:
        self._controller = sock.makefile()
      else:
        self._controller = sock.makefile(mode='rw', newline='\r')
      try:
        self._authenticate()
      except:
        self._controller = None

  def _authenticate(self):
    header = self._read(7)
    if header != 'PJLINK ':
      raise ProjectorException('Invalid header: {0}'.format(header))
    security = self._read(1)
    if security not in ['0', '1']:
      raise ProjectorException('Invalid security option: {0}'.format(security))
    sep = self._read(1)

    if security == '1':
      salt = self._read_util()

      if self._password is None:
        raise ProjectorException('Projector requires a password.')

      pass_data = (salt + self._password).encode('utf-8')
      pass_data_md5 = hashlib.md5(pass_data).hexdigest()

      self._send_command(cmd='POWR', param='?', prefix=pass_data_md5)
      data = self._read_util()
      if data == 'PJLINK ERRA':
        raise ProjectorException('Authentication failed.')

    self._expiration = datetime.datetime.now() + self._TIMEOUT

  def get(self, cmd, expectation=None):
    """Inquiries projector for response.

    Args:
      cmd: a pjlink command.
      expectation: if set, response will be validated against.
    Returns:
      Response string.
    Raises:
      ProjectorException: if response is not as expected.
    """
    return self.set(cmd=cmd, param='?', expectation=expectation)

  def set(self, cmd, param='?', expectation=None, reset=False):
    """Sends command and receives response.

    Args:
      cmd: a pjlink command.
      param: parameter of the command.
      expectation: if set, response will be validated against.
      reset: if True, connection will be reset after sending the command.
    Returns:
      Response string.
    Raises:
      ProjectorException: if response is not as expected.
    """
    with self._lock:
      if not self._controller or datetime.datetime.now() > self._expiration:
        self.reconnect()

      self._send_command(cmd, param)

      if reset:
        self._controller = None
        return

      try:
        response_cmd, result = self._get_response()
      except Exception as e:
        self._controller = None
        raise

      if cmd != response_cmd:
        raise ProjectorException(
            'Unexpected command in response: {0}'.format(response_cmd))
      if result in self._ERRORS:
        raise ProjectorException(self._ERRORS[result])

      if expectation and expectation != result:
        raise ProjectorException('Unexpected response: {0}'.format(result))

      return result

  def _send_command(self, cmd, param, prefix=b'%1', sep=b' ', term=b'\r'):
    assert cmd.isupper()
    assert len(cmd) <= 4
    assert len(param) <= 128

    binary = prefix + cmd + sep + param + term
    self._controller.write(binary)
    self._controller.flush()

  def _get_response(self):
    header = self._read(1)
    if header != b'%':
      raise ProjectorException('Invalid header: {0}'.format(header))

    version = self._read(1)
    if version != b'1':
      raise ProjectorException('Invalid version: {0}'.format(version))

    cmd = self._read(4).upper()

    sep = self._read(1)
    if sep != b'=':
      raise ProjectorException('Invalid separator: {0}'.format(sep))

    result = self._read_until()
    self._expiration = datetime.datetime.now() + self._TIMEOUT

    return (cmd, result)

  def _read(self, n):
    try:
      if sys.version_info.major == 2:
        return self._controller.read(n).decode('utf-8')
      else:
        return self._controller.read(n)
    except Exception as e:
      raise ProjectorException('Failed to read {0} bytes: {1}'.format(n, e))

  def _read_until(self, term=b'\r'):
    data = []
    try:
      c = self._read(1)
      while c and c != term:
        data.append(c)
        c = self._read(1)
    except Exception as e:
      raise ProjectorException('Failed to read until "{0}": {1}'.format(
          term, e))
    return b''.join(data)
