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
#ifndef POTS_H
#define POTS_H

#include <Arduino.h>

// Arduino's 10 bit DAC => range is 0,1023.
#define POT_MAX 1023

struct PotStatus;

/**
 * Manages analog potentiometers.
 * Detects changes by comparing to a simple threshold.
 */
class Pots {
 public:
  /**
   * @param n Number of pins.
   * @param pins Pointer to the ids of the pins.
   */
  Pots(int n, const int* pins);
  ~Pots();

  /** Poll the pins for the pot status. */
  void poll(void);

  // Iterate over changed pots.
  /** Whether the current pot has changed. */
  bool has_changed_pot();
  /** Advance to next pot. */
  int next_changed_pot();

  // Directly read the status of a pot.
  /** Read status of a specific pot. */
  int get_value(int pot);
  /** Whether a specific pot has changed status. */
  bool is_changed(int pot);

  /** Reset changed status of all pots. */
  void clear_changed(void);

 private:
   const int n_;
   const int* const pins_;
   PotStatus* status_;
   int next_val_;
   int next_iter_;
};

#endif // POTS_H
