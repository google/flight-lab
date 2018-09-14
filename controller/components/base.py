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
"""Base class for all components."""

from common import pattern
from protos import controller_pb2


class Component(pattern.Logger, pattern.EventEmitter):
  """Base class for all components.

  This base class provides:
    * name: name of the component
    * proto: configuration protobuf of this component.
    * settings: settings protobuf for sub-class.
    * logger (logging.Logger): single point of logging.
    * emit(): to emit event.

  Subclasses shall implement:
    * _start(): start the component.
    * _stop(): stop the component.
    * _restart(): restart the component.

  Subclasses may also emit the following events:
    * 'status_changed': when status of component is changed.
  """

  def __init__(self, proto, *args, **kwargs):
    super(Component, self).__init__(self, *args, **kwargs)
    self._proto = proto

  @property
  def name(self):
    return self._proto.name

  @property
  def proto(self):
    return self._proto

  @property
  def settings(self):
    kind = self._proto.WhichOneof('kind')
    return getattr(self._proto, kind)

  def on_command(self, command):
    if command == controller_pb2.SystemCommand.START:
      self._start()
    elif command == controller_pb2.SystemCommand.STOP:
      self._stop()
    elif command == controller_pb2.SystemCommand.RESTART:
      self._restart()

  def close(self):
    pass

  def _start(self):
    pass

  def _stop(self):
    pass

  def _restart(self):
    pass
