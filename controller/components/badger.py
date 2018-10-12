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
"""Library for badge reader component."""

import threading
import time

from components import base
from protos import controller_pb2
from utils import badger

class BadgeReaderComponent(base.Component):
  """Component to authorize USB badges.

  Events:
    "status_changed": when badge scan is authorized or authorization has expired.
  """

  _AUTH_TIMEOUT_SEC = 10

  def __init__(self, proto, *args, **kwargs):
    """Create a BadgeReaderComponent instance.

    Args:
      proto: flightlab.BadgeReader protobuf.
    """
    super(BadgeReaderComponent, self).__init__(proto, *args, **kwargs)
    self._deauth = None
    self._validator = badger.BadgeValidator(self.settings.url, self.settings.key_param)
    self._reader = badger.BadgeReader(usb_vendor_id=self.settings.usb_vendor_id, usb_product_id=self.settings.usb_product_id)
    self._reader.on('read_success', self._on_read_success)
    self._reader.start()


  def _on_read_success(self, reader, badge_id):
    self.logger.info("Badge %s Read Successfully", badge_id)
    if self._validator.validate(badge_id):
      self.logger.info("Badge Validated")
      self.settings.status = controller_pb2.Badger.AUTHORIZED
      self.emit('status_changed', self)
    else:
      self.logger.info("Invalid Badge")
      self.settings.status = controller_pb2.Badger.UNAUTHORIZED
      self.emit('status_changed', self)

    if self._deauth:
      self._deauth.cancel()
    self._deauth = threading.Timer(self._AUTH_TIMEOUT_SEC, self._deauthorize)
    self._deauth.start()

  def _deauthorize(self):
      self.logger.info("Deauthorizing")
      """Ensures status is changed to UNKNOWN, which is the default state.

      Emits:
          status_changed
      """
      self.settings.status = controller_pb2.Badger.UNKNOWN
      self.emit('status_changed', self)

  def close(self):
    """Stops the badge reader and deauthorization thread."""
    if self._deauth:
      self._deauth.cancel()
    super(BadgeReaderComponent, self).close()

