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
#include "pots.h"

#define HIST_SZ 5
#define EPSILON 5

struct PotStatus {
  int values[HIST_SZ];
  int sum;
  int adj;
  void print() {
    Serial.print("sum=");Serial.print(sum);
    Serial.print(" adj=");Serial.print(adj);
    Serial.print(" v0=");Serial.print(values[0]);
    Serial.print(" v1=");Serial.print(values[1]);
    Serial.print(" v2=");Serial.print(values[2]);
    Serial.print(" v3=");Serial.print(values[3]);
    Serial.print(" v4=");Serial.print(values[4]);
    Serial.println();
  }
};

Pots::Pots(int n, const int* pins):
  n_(n),
  pins_(pins),
  next_val_(0),
  next_iter_(0)
{
  status_ = new PotStatus[n_]();
  memset(status_, 0, n * sizeof(PotStatus));
}

Pots::~Pots() {
  delete status_;
  status_ = nullptr;
}

bool Pots::has_changed_pot() {
  while (next_iter_ < n_) {
    if (is_changed(next_iter_++)) {
      return true;
    }
  }
  clear_changed();
  return false;
}

int Pots::next_changed_pot() {
  return next_iter_ - 1;
}

void Pots::poll() {
  for (int i = 0; i < n_; ++i) {
    int* valptr = &status_[i].values[next_val_]; 
    int oldval = *valptr;
    *valptr = analogRead(pins_[i]);
    int delta = *valptr - oldval;
    status_[i].sum += delta;
    status_[i].adj += delta;
  }
  // rotate place for reading next value
  next_val_ = (next_val_ + 1) % HIST_SZ;
  // reset iteration
  next_iter_ = 0;
}

int Pots::get_value(int pot) {
  return status_[pot].sum / HIST_SZ;
}

bool Pots::is_changed(int pot) {
  return status_[pot].adj > EPSILON || status_[pot].adj < -EPSILON;
}

void Pots::clear_changed() {
  for (int i = 0; i < n_; ++i) {
    status_[i].adj = 0;
  }
}
