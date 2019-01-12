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

import os

from utils import display

try:
  raw_input          # Python 2
except NameError:
  raw_input = input  # Python 3


def test():
  test_message = 'Hello World!'
  test_image_path = os.path.join(
      os.path.dirname(os.path.realpath(__file__)), '../data/logo.png')
  d = display.Display(
      chrome_path='c:/Program Files (x86)/Google/Chrome/Application/chrome.exe')
  d.show_message(test_message)
  raw_input('Press any key to exit.')
  d.show_image(test_image_path)
  raw_input('Press any key to exit.')
  d.close()


if __name__ == '__main__':
  test()
