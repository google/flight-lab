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

#ifndef SERIAL_RX_FLIGHTSIM
#define SERIAL_RX_FLIGHTSIM

#define MAX_SERIAL 200
class SerialRx {
 public:
  SerialRx(const char *id_);

  bool read_until_newline();

  // Override to provide custom reset behavior.  Called when we recieve an ID?
  // query.
  virtual void reset() {}

  // Override to provide a custom data handler.
  // When this is called, the last newline terminated string recieved is in
  // read_buffer.
  virtual void line_rx() {}

  void process();

 protected:
  char read_buffer[MAX_SERIAL];

 private:
  int pos;
  int last_read;
  char id[10];
  bool overflow;
};

#endif
