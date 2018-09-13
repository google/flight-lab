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
"""Test-cases for utils.light.Dmx and utils.light.SimLightEffect."""

import time

import light


def test():
  channels = [1, 17, 33, 49]
  dmx = light.Dmx()
  effects = [light.SimLightEffect(dmx=dmx, channel=ch) for ch in channels]
  for effect in effects:
    effect.start()

  time.sleep(10)
  for effect in effects:
    effect.on()
  time.sleep(10)
  for effect in effects:
    effect.off()
  time.sleep(10)


if __name__ == '__main__':
  test()
