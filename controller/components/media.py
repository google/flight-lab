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
"""Library for components related to media control."""

import playsound

from components import base


class SoundComponent(base.Component):
  """Component to play effect sound."""

  def _start(self):
    self.logger.info('[Sound] Playing startup sound...')
    playsound.playsound(self.settings.media_path, block=False)