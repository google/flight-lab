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

// Arduino driver for the Lights Switch Panel, which contains various lights
// and other toggles (e.g. fuel pump) in the 172, plus four potentiometers.
// This also manages the ignition switch, and expects an original Cessna
// switch.
// Toggles and ignition information is transmitted using the custom serial_rx
// protocol.
// Potentiometer values are transmitted using the custom dimmer_box protocol.

#include "dimmer_box.h"
#include "poll_cycle.h"
#include "pots.h"
#include "toggles.h"
#include "serial_rx.h"

// Dimmer Constants
#define DIMMER_CLOCK 10
#define DIMMER_DATA 6
#define DIMMER_LATCH 5

// Enabling SERIAL_DEBUG disables normal serial_rx protocol bahavior, so use it
// only for standalone testing (that said, serial_rx is 
// When enabled, we print all events as they happen, in human-friendly form,
// to the serial output. This includes toggle changes and pot changes.
//#define SERIAL_DEBUG

#define ARRAY_LEN(x) (sizeof(x) / sizeof((x)[0]))
#define DELAY_MS 20

// Toggle positions are transmitted this way:
// TGLa:1 TGLb:0
// Toggle names are max 5 chars, followed by colon and one char, totaling 8
// chars per changed toggle. Worst case, all toggles changed and the string
// is 8 * number_of_toggles. Carefully check this next value for correctness.
// We add 13 for the longest ignition string ("IGNITION:OFF ").
// Last "+1" is for the null character.
#define BUFFER_SZ (8 * ARRAY_LEN(toggle_pins) + 13 + 1)

// Pot Arrangement:
//   Pin:             A0        A1         A2           A3
//   Dimmer channel:  0         1          2            3
//   Position:        top-left  top-right  bottom-left  bottom-right
//   Legend:          SW/CB     STBY IND   PEDESTAL     AVIONICS
static const int pot_pins[] =     {A0, A1, A2, A3};
static const int pot_channels[] = { 0,  1,  2,  3};

// Toggle pins and names have to correspond to each other positionally.
static const int toggle_pins[] = {
  22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46};

// Max supported length is 5. Adjust BUFFER_SZ if needed, but confirm first
// that serial would support transmitting all toggles at once.
static const char* toggle_names[] = {
  "SBARM",
  "SBTST",
  "ALT",
  "BAT",
  "BUS2",
  "BUS1",
  "STROB",
  "FPUMP",
  "LAND",
  "BCN",
  "TAXI",
  "NAV",
  "PITOT"
};

// Connect the ignition switch as follows:
//  * terminals BAT and GND (the one in the center) go to Arduino GND pins.
//  * terminals L, R and S go to the following Arduino pins, respectively:
static const int ignition_pins[] = {31, 33, 35};

// This class reports toggles that have changed state since last request, or
// full status depending on the command received.
// In the case of pots, all are reported always (currently only for testing,
// since the sim has no need to know their position and therefore never
// asks for them as of now).
class SerialHandler: public SerialRx {
 public:
  SerialHandler(Toggles* toggles, Toggles* ignition, Pots* pots):
    SerialRx("LIGHTS"),
    toggles_(toggles),
    ignition_(ignition),
    pots_(pots)
  {}

  void line_rx() {
    buffer_[0] = '\0';
    if (strcmp(read_buffer, "TOGGLES?") == 0) {
      do_toggles();
      do_ignition();
    } else if (strcmp(read_buffer, "STATUS?") == 0) {
      do_status();
    } else if (strcmp(read_buffer, "POTS?") == 0) {
      do_pots();
    } else {
      return;
    }
    Serial.println(buffer_);
  }

 private:
  char buffer_[BUFFER_SZ];
  Toggles* toggles_;
  Toggles* ignition_;
  Pots* pots_;
  const int L=0, R=1, S=2;
  
  void do_toggles() {
    toggles_->poll();
    while (toggles_->has_changed_toggle()) {
      int tgl = toggles_->next_changed_toggle();
      strcat(buffer_, toggle_names[tgl]);
      strcat(buffer_, toggles_->is_on(tgl)? ":1 " : ":0 ");
    }
  }
  
  void do_status() {
    toggles_->poll();
    unsigned int i;
    for (i = 0; i < ARRAY_LEN(toggle_pins); ++i) {
      buffer_[i] = (toggles_->is_on(i)? '1' : '0');
    }
    ignition_->poll();
    buffer_[i++] = get_ignition_status();
    buffer_[i++] = '\0';
  }
  
  char get_ignition_status() {
    if (ignition_->is_on(S)) {
      // S closed means start (S-BAT in the switch, and we have BAT-GND)
      return 'S';
    } else if (!ignition_->is_on(L) && !ignition_->is_on(R)) {
      // Floating L and R means both magnetos on.
      return 'B';
    } else if (!ignition_->is_on(L)) {
      // Floating L means left magneto on.
      return 'L';
    } else if (!ignition_->is_on(R)) {
      // Floating R means right magneto on.
      return 'R';
    }
    // This should mean L and R are closed, and that means ignition off.
    return 'O';
  }
  
  void do_ignition() {
    ignition_->poll();
    if (ignition_->has_changed_toggle()) {
      sprintf(buffer_ + strlen(buffer_), "IGNITION:%c", get_ignition_status());
      ignition_->clear_changed();
    }
  }
  
  void do_pots() {
    sprintf(buffer_, "A0:%d A1:%d A2:%d A3:%d",
            pots_->get_value(0),
            pots_->get_value(1),
            pots_->get_value(2),
            pots_->get_value(3));
  }
};

DimmerBox dimmer(DIMMER_CLOCK, DIMMER_DATA, DIMMER_LATCH);
Pots pots(ARRAY_LEN(pot_pins), pot_pins);
Toggles toggles(ARRAY_LEN(toggle_pins), toggle_pins);
Toggles ignition(ARRAY_LEN(ignition_pins), ignition_pins);
PollCycle switch_cycle(10); // poll switches every 10 loops
SerialHandler handler(&toggles, &ignition, &pots);

#ifdef SERIAL_DEBUG
void print_pot(int pot) {
  Serial.print("Pot "); Serial.print(pot);
  Serial.print(" is now ");
  Serial.println(pots.get_value(pot));
}

void print_toggle(int toggle) {
  Serial.print("Tgl "); Serial.print(toggle_names[toggle]);
  Serial.print(": ");
  Serial.println(toggles.is_on(toggle)? "ON" : "OFF");
}

void process_events() {
  if (switch_cycle.next_turn()) {
    toggles.poll();
    while (toggles.has_changed_toggle()) {
      int tgl = toggles.next_changed_toggle();
      print_toggle(tgl);
    }
  }
}

#else
// Make this one a no-op.
# define print_pot(x)
// Make this one react to serial events
void process_events() {
  handler.process();
}
#endif // SERIAL_DEBUG



void setup() {
  dimmer.connect();
  Serial.begin(9600);
}

void loop() {
  process_events();
  
  pots.poll();
  while (pots.has_changed_pot()) {
    int pot = pots.next_changed_pot();
    print_pot(pot);
    // Assumption: dimmer values are 12bit, pot values are 10bit.
    dimmer.set(pot_channels[pot],
               map(pots.get_value(pot), 0, 1023, 0, 4095));
    dimmer.update();
  }
  delay(DELAY_MS);
}
