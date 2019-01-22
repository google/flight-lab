/* Copyright 2018 Flight Lab authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include "toggles.h"

Toggles::Toggles(int n, const int* pins):
  n_(n),
  pins_(pins),
  next_iter_(0)
{
  status_ = new uint8_t[n_]();
  for (int i = 0; i < n_; ++i) {
    status_[i] = 0;
    pinMode(pins[i], INPUT_PULLUP);
  }
}

Toggles::~Toggles() {
  delete[] status_;
  status_ = nullptr;
}

bool Toggles::has_changed_toggle() {
  while (next_iter_ < n_) {
    if (is_changed(next_iter_++)) {
      return true;
    }
  }
  clear_changed();
  return false;
}

int Toggles::next_changed_toggle() {
  return next_iter_ - 1;
}

void Toggles::poll() {
  for (int i = 0; i < n_; ++i) {
    bool is_now_on = digitalRead(pins_[i]) == LOW;
    if (is_on(i) != is_now_on) {
      status_[i] |= 0x2; // set bit 2, signifying change.
      status_[i] ^= 0x1; // status changed, so flip bit 1.
    }
  }
  next_iter_ = 0;
}

bool Toggles::is_on(int toggle) {
  return status_[toggle] & 0x1;
}

bool Toggles::is_changed(int toggle) {
  return status_[toggle] & 0x2;
}

void Toggles::clear_changed() {
  for (int i = 0; i < n_; ++i) {
    status_[i] &= 0x1;
  }
}
