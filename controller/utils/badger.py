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
""" Utility for reading USB badge scanners with authorization via HTTP APIs."""

import requests
import time

from common import pattern
from evdev import InputDevice, ecodes, list_devices

class BadgeReaderException(Exception):
  pass

class BadgeValidator(pattern.EventEmitter):
  """Class for badge authorization via HTTP API."""

  def __init__(self, url, key_param, *args, **kwargs):
    """Creates a BadgeValidator instance for validating badges.

    The URL parameter will be appended with the customer key_param
    as the parameter name and badge_id as the value when called.
    ie:  ?myCustomKeyParam=<badge_id>

    Args:
      url: Authorization server URL
      key_param: Name of badge parameter to add to the URL
    """
    super(BadgeValidator, self).__init__(*args, **kwargs)
    self._url = url
    self._key_param = key_param

  def close(self):
    """Closes the communication."""
    super(BadgeReader, self).close()

  def validate(self, badge_id):
    """Validates the badge ID with a HTTP service. Any 2xx is considered success.

    Args:
      badge_id: String containing the badge identifier to authorize.
    Returns:
      Response boolean.
    """
    try:
      r = requests.get(url = self._url, params = {self._key_param: badge_id})
      return r.status_code >= 200 and r.status_code < 300
    except requests.ConnectionError:
      return False

class BadgeReader(pattern.Worker, pattern.EventEmitter):
  """Worker that monitors the badge reader and emits the badge ID on success.

  This class supports Google's USB pcProx RFID Reader configured to support Google
  employee badges.  However, it may support other USB HID based readers given
  the proper vendor and product codes. It currently only supports reading the
  0-9 and : ASCII characters.
  """
  def __init__(self, usb_vendor_id, usb_product_id,  *args, **kwargs):
    """Creates a BadgeReader instance.

    Args:
      usb_vendor_id: USB Vendor ID of the device.
      usb_product_id: USB Product ID of the device.
    """
    super(BadgeReader, self).__init__(worker_name='BadgeReader', *args, **kwargs)
    self._device = None
    self._usb_vendor_id = usb_vendor_id
    self._usb_product_id = usb_product_id
    self._key_codes = {
            2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6',
            8: u'7', 9: u'8', 10: u'9', 11: u'0', 39: u':'}

  def _on_start(self):
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
      if device.info.vendor == int(self._usb_vendor_id, 16) and device.info.product == int(self._usb_product_id, 16):
        self._device = device
        self.logger.info("Badge reader device found.")
        break
    if self._device == None:
      self.logger.warn("Device may be disconnected. Attempting to reconnect...")
      time.sleep(10)
      self._on_start()

  def _on_run(self):
    """Read and format an RFID badge ID

    Raises:
      BadgeReaderException: When device is unavailable, or reading fails.
    Emits:
      read_success: A badge was successfully read.
    """
    try:
      self._device.grab()
      badge_id = ""
      for event in self._device.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
          if event.code in (self._key_codes):
            badge_id += self._key_codes[event.code]
            continue
          if event.code is ecodes.KEY_ENTER:
            self.emit('read_success', self, badge_id)
            badge_id = ""
      self._device.ungrab()
      return True
    except:
      self.logger.warn("Device may be disconnected. Attempting to reconnect...")
      time.sleep(10)
      self._on_start()

