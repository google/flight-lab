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

#ifndef TOGGLES_H
#define TOGGLES_H

#include <Arduino.h>

/**
 * Manages a group of toggle switches.
 * The class keeps track of current position of each switch, and after each
 * poll, keeps track of what changed since the last poll.
 */
class Toggles {
 public:
  /**
   * @param n Number of pins.
   * @param pins Pointer to the ids of the pins.
   */
  Toggles(int n, const int* pins);
  ~Toggles();

  /**
   * Update the status by reading position of all switches.
   */
  void poll();

  // Iterate over changed switches.
  /** Whether the current switch has changed. */
  bool has_changed_toggle();
  /** Advance to next switch. */
  int next_changed_toggle();

  // Directly read the status of a switch.
  /** Read status of a specific switch. */
  bool is_on(int toggle);
  /** Whether a specific switch has changed status. */
  bool is_changed(int toggle);
  
  /** Reset changed status of all switches. */
  void clear_changed();

 private:
  const int n_;
  const int* const pins_;
  // Bit 1 (lsb) is current status.
  // Bit 2 is set when change was detected.
  // Bits 3-8 are wasted.
  uint8_t* status_;
  int next_iter_;
};

#endif // TOGGLES_H
