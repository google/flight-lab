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
"""Service handler for controller client."""

from common import pattern
from protos import client_pb2
from protos import client_pb2_grpc
from utils import display


class ClientService(client_pb2_grpc.ClientServiceServicer, pattern.Closable):
  """Provider for flightlab.ClientService."""

  def __init__(self, server, machine_config, *args, **kwargs):
    """Creates ClientService instance.

    Args:
      server: gRPC server.
      machine_config: Configuration protobuf of current machine.
    """
    super(ClientService, self).__init__(*args, **kwargs)
    client_pb2_grpc.add_ClientServiceServicer_to_server(self, server)
    self._display = display.Display(
        chrome_path=machine_config.chrome_executable_path)

  def close(self):
    """Stops client service."""
    self._display.close()

  def DisplayMessage(self, message, context):
    """Displays a text message on client machine.

    Args:
      message: flightlab.Message protobuf.
      context: gRPC context.
    Returns:
      flightlab.GeneralResponse.
    """
    self._display.show_message(message.message)
    return client_pb2.GeneralResponse(succeed=True)

  def DisplayImage(self, image, context):
    """Displays an image on client machine.

    Args:
      image: flightlab.Image protobuf.
      context: gRPC context.
    Returns:
      flightlab.GeneralResponse.
    """
    self._display.show_image(image.image_path)
    return client_pb2.GeneralResponse(succeed=True)

  def DisplayOff(self, request, context):
    """Turns display off.

    Args:
      request: google.protobuf.Empty.
      context: gRPC context.
    Returns:
      flightlab.GeneralResponse.
    """
    self._display.close()
    return client_pb2.GeneralResponse(succeed=True)
