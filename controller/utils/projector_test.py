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
"""Test-cases for utils.Projector."""
from __future__ import print_function

import logging
import sys

import projector

try:
  raw_input          # Python 2
except NameError:
  raw_input = input  # Python 3


def test(argv):
  ip = argv[1]
  p = projector.Projector(name='test', address=ip)
  p.on('state_changed', on_state_changed)
  p.start()
  while True:
    cmd = raw_input('Command>')
    if cmd == 'on':
      try:
        p.power_on()
      except Exception as e:
        print(e)
    elif cmd == 'off':
      try:
        p.power_off()
      except Exception as e:
        print(e)
    elif cmd == 'exit':
      break
  p.stop()


def on_state_changed(old_state, new_state):
  print('State changed: "{0}" => "{1}"'.format(old_state, new_state))


if __name__ == '__main__':
  logger = logging.getLogger('')
  logger.setLevel('DEBUG')
  console_handler = logging.StreamHandler()
  console_handler.setFormatter(
      logging.Formatter('%(levelname)-8s %(name)-12s: %(message)s'))
  logger.addHandler(console_handler)
  test(sys.argv)
