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
"""Library for all display related components."""

from components import base
from protos import controller_pb2
from utils import projector


class ProjectorComponent(base.Component):
  """Component to control projector."""

  _STATUS_MAPPING = {
      projector.Status.ON: controller_pb2.Projector.ON,
      projector.Status.OFF: controller_pb2.Projector.OFF,
      projector.Status.WARM_UP: controller_pb2.Projector.WARM_UP,
      projector.Status.COOL_DOWN: controller_pb2.Projector.COOL_DOWN,
  }
  _COMPONENT_STATUS_MAPPING = {
      controller_pb2.Projector.UNKNOWN: controller_pb2.Component.UNKNOWN,
      controller_pb2.Projector.ON: controller_pb2.Component.ON,
      controller_pb2.Projector.OFF: controller_pb2.Component.OFF,
      controller_pb2.Projector.WARM_UP: controller_pb2.Component.TRANSIENT,
      controller_pb2.Projector.COOL_DOWN: controller_pb2.Component.TRANSIENT,
  }

  def __init__(self, proto, *args, **kwargs):
    """Creates ProjectorComponent instance.

    Args:
      proto: flightlab.Projector protobuf.
    """
    super(ProjectorComponent, self).__init__(proto, *args, **kwargs)
    self._projector = projector.Projector(
        name=self.name, address=self.settings.ip)
    self._projector.on('status_changed', self._on_status_changed)
    self._projector.start()

  @property
  def projector(self):
    """Gets underlaying projector instance.

    Returns:
      utils.projector.Projector.
    """
    return self._projector

  def close(self):
    """Closes underlaying projector instance.

    This method doesn't turn off projector.
    """
    if self._projector:
      self._projector.stop()
      self._projector = None
    super(ProjectorComponent, self).close()

  def _start(self):
    self.logger.info('[Projector - {0}] Powering on...'.format(self.name))
    try:
      self._projector.power_on()
    except projector.ProjectorException as e:
      self.logger.error('[Projector - {0}] Error: {1}'.format(self.name, e))

  def _stop(self):
    self.logger.info('[Projector - {0}] Powering off...'.format(self.name))
    try:
      self._projector.power_off()
    except projector.ProjectorException as e:
      self.logger.error('[Projector - {0}] Error: {1}'.format(self.name, e))

  def _on_status_changed(self, old_status, new_status):
    self.logger.info('[Projector - {0}] {1} => {2}'.format(
        self.name, old_status, new_status))

    new_status = self._STATUS_MAPPING[new_status]
    self.settings.status = new_status
    self.proto.status = self._COMPONENT_STATUS_MAPPING[new_status]
    self.emit('status_changed', self)
