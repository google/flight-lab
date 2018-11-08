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
"""Factories for creating components."""

import sys

from common import pattern
from components import app
from components import display
from components import light
from components import media


class ComponentFactory(pattern.Logger):
  """Factory for creating components."""

  def __init__(self, *args, **kwargs):
    super(ComponentFactory, self).__init__(*args, **kwargs)
    self._mapping = {
        'app': app.AppComponent,
        'light': light.DMXLightComponent,
        'projector': display.ProjectorComponent,
        'sound': media.SoundComponent,
        'commandline': app.CommandLineComponent,
    }

    if sys.platform.startswith('win'):
      import windows
      self._mapping['windows_app'] = windows.WindowsAppComponent
    else:
      from components import badger
      self._mapping['badger'] = badger.BadgeReaderComponent

  def get_settings(self, component_proto):
    """Gets component-specific configuration protobuf.

    Args:
      component_proto: flightlab.Component protobuf.
    Returns:
      Component-specific configuration protobuf inside "kind" oneof.
    """
    kind = component_proto.WhichOneof('kind')
    return getattr(component_proto, kind)

  def get_component_class(self, component_proto):
    """Gets corresponding class per component configuration protobuf.

    Args:
      component_proto: flightlab.Component protobuf.
    Returns:
      Component class.
    Raises:
      UnknownComponentException: if no known component class for given component
      specifc configuration.
    """
    kind = component_proto.WhichOneof('kind')
    if kind not in self._mapping:
      raise UnknownComponentException(
          'Unknown component kind {0}'.format(kind))
    return self._mapping[kind]

  def create_component(self, component_proto):
    """Creates corrsponding instance per component configuration protobuf.

    Args:
      component_proto: flightlab.Component protobuf.
    Returns:
      Component instance.
    """
    kind = component_proto.WhichOneof('kind')
    self.logger.info('Creating component {0}...'.format(kind))

    cls = self.get_component_class(component_proto)
    return cls(proto=component_proto)


class UnknownComponentException(Exception):
  pass
