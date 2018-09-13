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
"""Library for lighting components."""

from components import base
from utils import light


class DMXLightComponent(base.Component):
  """Component to control DMX lighting."""

  _CHANNELS = [1, 17, 33, 49]

  def __init__(self, proto, *args, **kwargs):
    """Creates DMXLightComponent instance.

    Args:
      proto: flightlab.DMXLight protobuf.
    """
    super(DMXLightComponent, self).__init__(proto, *args, **kwargs)
    self._dmx = light.Dmx(port=self.settings.com)
    self._effects = [
        light.SimLightEffect(dmx=self._dmx, channel=ch) for ch in self._CHANNELS
    ]
    for effect in self._effects:
      effect.start()

  def close(self):
    """Stops effects and turns off lights."""
    for effect in self._effects:
      effect.stop()
    self._effects = []
    if self._dmx:
      self._dmx.close()
      self._dmx = None
    super(DMXLightComponent, self).close()

  def _start(self):
    for effect in self._effects:
      effect.on()

  def _stop(self):
    for effect in self._effects:
      effect.off()
