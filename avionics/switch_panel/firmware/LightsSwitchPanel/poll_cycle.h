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
#ifndef POLL_CYCLE_H
#define POLL_CYCLE_H

#include <Arduino.h>

/**
 * Just a cyclic counter that returns true once every
 * _period_ times it's called.
 */
class PollCycle {
 public:
  /**
   * @param period How many cycles per poll period.
   */
  PollCycle(uint16_t period): cycle_(0), period_(period) {}
  /** Advance to the next cycle and return true if period has completed. */
  bool next_turn() {
    ++cycle_ %= period_;
    return cycle_ == 0;
  }
  
 private:
  uint16_t cycle_;
  const uint16_t period_;
};

#endif // POLL_CYCLE_H
