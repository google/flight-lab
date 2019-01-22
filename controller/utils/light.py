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
"""Utility for light control."""

import colorsys
import random
import serial
import struct

from common import pattern

try:
  xrange  # Python 2
except NameError:
  xrange = range  # Python 3


class Dmx(pattern.Closable, pattern.Logger):
  """Class for controlling DMX lights.

  Dmx lights uses COM port for communication. Each light fixture uses 5 channels
  for RGB and brightness settings.
  """

  def __init__(self, port='COM4', *args, **kwargs):
    """Creates DMX instance.

    Args:
      port: COM port to communicate to DMX controller.
    """
    super(Dmx, self).__init__(*args, **kwargs)
    self._data = [0] * 512
    self._max_reg = -1
    for i in xrange(255):
      self._set(i, 0)
    self._com = serial.Serial(port)

  def close(self):
    """Closes the communication."""
    if self._com:
      self.logger.info('Shutting down light controller')
      self._com.close()
      self._com = None
    super(Dmx, self).close()

  def set_rgb(self, channel, r, g, b, w=0):
    """Sets a single light fixture.

    Call render() afterwards to make settings effective.

    Args:
      channel: channel number for the light fixture.
      r: red value (0-255)
      g: green value (0-255)
      b: blue value (0-255)
      w: brightness value (0-255)
    """
    self._set(channel, 255)
    self._set(channel + 1, r)
    self._set(channel + 2, g)
    self._set(channel + 3, b)
    self._set(channel + 4, w)

  def set_hsv(self, channel, h, s=1.0, v=1.0, w=0.0):
    """Sets a single light fixture.

    Call render() afterwards to make settings effective.

    Args:
      channel: channel number for the light fixture.
      h: hue (0-1.0)
      s: saturation (0-1.0)
      v: value (0-1.0)
      w: brightness (0-1.0)
    """
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    self.set_rgb(channel,
                 int(255 * r), int(255 * g), int(255 * b), int(255 * w))

  def render(self):
    """Send DMX data string to the Enttec."""
    dmx_data = ''.join([chr(self._data[i]) for i in xrange(self._max_reg + 1)])
    dmx_len = len(dmx_data)

    # Here we simply forward the raw data to the serial port, with a two-byte
    # header that tells the Entec box that this is a normal DMX message.
    entec_msg = struct.pack(
        '<BBH %ds B' % dmx_len,
        0x7e,  # Start of message delimiter
        6,  # type: Output Only Send DMX Packet Request
        dmx_len,  # Length of DMX message
        dmx_data,
        0xe7)  # End of message delimiter
    self._com.write(entec_msg)

  def _set(self, addr, value, auto_render=False):
    self._data[addr] = value
    self._max_reg = max(self._max_reg, addr)
    if auto_render:
      self.render()


class SimLightEffect(pattern.Worker):
  """Produces gradual color shifting effect."""

  _IDLE_RATE = 360.0
  _IDLE_LEVEL = 0.1
  _PHASE = [0, 0, 0.33, 0.66]
  _CLOCK_RATE = 0.1

  def __init__(self, dmx, channel, *args, **kwargs):
    """Creates SimLightEffect instance.

    Args:
      dmx: Dmx instance.
      channel: channel number of the light fixture to apply the effect.
    """
    super(SimLightEffect, self).__init__(
        worker_name='SimLightEffect (channel {0})'.format(channel),
        *args,
        **kwargs)
    self._dmx = dmx
    self._channel = channel
    self._color = 0
    self._white = 0
    self._level = self._IDLE_LEVEL
    self._new_color = 0
    self._new_white = 0
    self._new_level = self._IDLE_LEVEL
    self._count = 0
    self._phase = random.random()

  def on(self):
    self._new_level = 0.0
    self._new_white = 0.0

  def off(self):
    self._new_level = self._IDLE_LEVEL
    self._new_white = 0.0

  def _on_run(self):
    self._count += 1
    rate = self._CLOCK_RATE / 5.0
    self._new_color = self._count / self._IDLE_RATE + self._phase

    self._color = self._ramp(self._color, self._new_color % 1.0, rate)
    self._level = self._ramp(self._level, self._new_level, rate)
    self._white = self._ramp(self._white, self._new_white, rate)
    self._dmx.set_hsv(
        self._channel, h=self._color, v=self._level, w=self._white)
    self._dmx.render()
    self._sleep(self._CLOCK_RATE)

  def _ramp(self, value, goal, inc):
    diff = goal - value
    if abs(diff) <= inc:
      return goal
    if diff > 0:
      return value + inc
    else:
      return value - inc