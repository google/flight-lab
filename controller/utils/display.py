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
"""Utility library for displaying arbitrary content on a machine."""

import jinja2
import tempfile

from common import pattern
from utils import app


class Display(pattern.Closable):
  """Class for displaying arbitrary content on a machine.

  The implementation assumes Chrome browser is available on given machine and
  use it to display generated html content in kiosk mode so it appears as an app
  and works on any platform.
  """

  def __init__(self, chrome_path, *args, **kwargs):
    """Creates Display instance.

    Args:
      chrome_path: path to chrome executable.
    """
    super(Display, self).__init__(*args, **kwargs)
    self._chrome_path = chrome_path
    self._temp_path = tempfile.gettempdir()
    self._index_file = tempfile.mktemp(suffix='.html')
    self._chrome_app = app.Application(
        name='Browser',
        bin_path=chrome_path,
        arguments=[
            '--kiosk', self._index_file, '--new-window', '--incognito',
            '--noerrordialogs', '--user-data-dir={0}'.format(self._temp_path)
        ],
        restart_on_crash=True)

  def close(self):
    """Closes Chrome browser."""
    self._chrome_app.stop()

  def show_message(self, message, template_path='./data/display_message.html'):
    """Shows a text message in full screen.

    Args:
      message: text to show.
      template_path: a html template to use. It should contain "{{ message }}".
    """
    self._generate_page(
        template_path=template_path, kwargs={
            'message': message
        })
    self._relaunch()

  def show_image(self,
                 image_path,
                 template_path='./data/display_image_default.html'):
    """Shows an image in full screen.

    Current implementation only displays the image at (0,0) and at its original
    size. If image is smaller than screen size, the rest area will be white. If
    image is larger than screen size, it will be clipped and scrollbar will
    appear.

    Args:
      image_path: a locally accessible path to image file.
      template_path: a html template to use. It should contain
                     "{{ image_path }}".
    """
    self._generate_page(
        template_path=template_path, kwargs={
            'image_path': image_path
        })
    self._relaunch()

  def _generate_page(self, template_path, kwargs={}):
    with open(template_path, 'r') as f:
      template = jinja2.Template(f.read())

    with open(self._index_file, 'w') as f:
      f.write(template.render(**kwargs))

  def _relaunch(self):
    self._chrome_app.stop()
    self._chrome_app.start()
