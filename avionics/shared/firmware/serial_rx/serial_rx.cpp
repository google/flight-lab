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

#include "serial_rx.h"
#include "Arduino.h"

SerialRx::SerialRx(const char *id_) : pos(0), last_read(0), overflow(false) {
  strcpy(id, "ID:");
  strncpy(id + 3, id_, 7);
  id[9] = '\0';
}

bool SerialRx::read_until_newline() {
  if (overflow) {
    overflow = false;
  }
  while (Serial.available() > 0 && pos < MAX_SERIAL) {
    read_buffer[pos] = Serial.read();
    if (read_buffer[pos] == '\n' || pos == MAX_SERIAL - 1) {
      read_buffer[pos] = '\0';
      pos = 0;
      overflow = pos == MAX_SERIAL - 1;
      return true;
    }
    pos++;
  }
  return false;
}

void SerialRx::process() {
  if (millis() - last_read <= 10) {
    return;
  }
  last_read = millis();

  if (read_until_newline() && !overflow) {
    if (strncmp(read_buffer, "ID?", MAX_SERIAL) == 0) {
      Serial.println(id);
      reset();
    } else {
      line_rx();
    }
  }
}
