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
"""Testcases for services.client.ClientService."""

import grpc
import sys

from google.protobuf import empty_pb2

from protos import client_pb2
from protos import client_pb2_grpc

try:
  raw_input          # Python 2
except NameError:
  raw_input = input  # Python 3


def test_image_display(argv):
  """Test image display on client machine.

  Usage: python client_service_test.py [host:port] [image file path]
    host: IP address of client machine.
    port: gRPC service port. (see _CLIENT_SERVICE_GRPC_PORT in main.py)
    image file path: a local path to an image file.
  """

  target = argv[1]
  image_path = argv[2]
  grpc_channel = grpc.insecure_channel(target)
  stub = client_pb2_grpc.RemoteServiceStub(grpc_channel)
  stub.DisplayImage(client_pb2.Image(image_path=image_path))
  raw_input('Press ENTER to continue.')
  stub.DisplayOff(empty_pb2.Empty())


if __name__ == '__main__':
  test_image_display(sys.argv)
