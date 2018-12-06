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

#include "../../shared/firmware/serial_rx/serial_rx.h"

#define PFD
// #define MFD

#define GFC700

#define MAX_OUT 16
#ifdef GFC700
#define MATRIX_COLS 10
#else
#define MATRIX_COLS 8
#endif
#define MATRIX_ROWS 8
#define MAX_COMMAND_LENGTH 32
#define KEY_ENTER 176

// Mapping from physical pins to matrix column and row indices.
#ifdef GFC700
//                                 0   1   2   3   4   5   6   7  8  9
const PROGMEM int kRowPins[] =    {22, 20, 21, 5,  6,  10, 11, 12};
const PROGMEM int kColumnPins[] = {23, 24, 19, 18, 17, 16, 1,  0, 9, 13};
#else
//                                 0   1   2   3   4   5   6   7
const PROGMEM int kRowPins[] =    {22, 20, 21, 5,  6,  10, 11, 12};
const PROGMEM int kColumnPins[] = {23, 24, 19, 18, 17, 16, 1,  0};
#endif

#ifdef PFD
#define IDENTIFIER "PFD"
#endif
#ifdef MFD
#define IDENTIFIER "MFD"
#endif

const PROGMEM char NAV_ID_TOGGLE[] = "NAV_ID_TOGGLE";
const PROGMEM char HDG_INCR[] = "HDG_INCR";
const PROGMEM char HDG_DECR[] = "HDG_DECR";
const PROGMEM char HDG_PRESS[] = "HDG_PRESS";
const PROGMEM char LARGE_ALT_INCR[] = "LARGE_ALT_INCR";
const PROGMEM char LARGE_ALT_DECR[] = "LARGE_ALT_DECR";
const PROGMEM char SMALL_ALT_INCR[] = "SMALL_ALT_INCR";
const PROGMEM char SMALL_ALT_DECR[] = "SMALL_ALT_DECR";
const PROGMEM char SMALL_ALT_PRESS[] = "SMALL_ALT_PRESS";
const PROGMEM char CRS_INCR[] = "CRS_INCR";
const PROGMEM char CRS_DECR[] = "CRS_DECR";
const PROGMEM char CRS_PRESS[] = "CRS_PRESS";
#ifdef PFD
const PROGMEM char NAV_FREQ_TOGGLE[] = "NAV_FREQ_TOGGLE";
const PROGMEM char LARGE_NAV_INCR[] = "LARGE_NAV_INCR";
const PROGMEM char LARGE_NAV_DECR[] = "LARGE_NAV_DECR";
const PROGMEM char SMALL_NAV_INCR[] = "SMALL_NAV_INCR";
const PROGMEM char SMALL_NAV_DECR[] = "SMALL_NAV_DECR";
const PROGMEM char SMALL_NAV_PRESS[] = "SMALL_NAV_PRESS";
const PROGMEM char COM_FREQ_TOGGLE[] = "COM_FREQ_TOGGLE";
const PROGMEM char COM_FREQ_TOGGLE_HOLD[] = "COM_FREQ_TOGGLE_HOLD";
const PROGMEM char LARGE_COM_INCR[] = "LARGE_COM_INCR";
const PROGMEM char LARGE_COM_DECR[] = "LARGE_COM_DECR";
const PROGMEM char SMALL_COM_INCR[] = "SMALL_COM_INCR";
const PROGMEM char SMALL_COM_DECR[] = "SMALL_COM_DECR";
const PROGMEM char SMALL_COM_PRESS[] = "SMALL_COM_PRESS";
const PROGMEM char BARO_INCR[] = "BARO_INCR";
const PROGMEM char BARO_DECR[] = "BARO_DECR";
const PROGMEM char RANGE_INCR[] = "PFD_RANGE_INCR";
const PROGMEM char RANGE_DECR[] = "PFD_RANGE_DECR";
const PROGMEM char RANGE_PRESS[] = "PFD_RANGE_PRESS";
const PROGMEM char RANGE_PAN_UP[] = "PFD_RANGE_PAN_UP";
const PROGMEM char RANGE_PAN_DOWN[] = "PFD_RANGE_PAN_DOWN";
const PROGMEM char RANGE_PAN_LEFT[] = "PFD_RANGE_PAN_LEFT";
const PROGMEM char RANGE_PAN_RIGHT[] = "PFD_RANGE_PAN_RIGHT";
const PROGMEM char DIRECT_TO[] = "PFD_DIRECT_TO";
const PROGMEM char MENU[] = "PFD_MENU";
const PROGMEM char FPL[] = "PFD_FPL";
const PROGMEM char PROC[] = "PFD_PROC";
const PROGMEM char CLR[] = "PFD_CLR";
const PROGMEM char ENT[] = "PFD_ENT";
const PROGMEM char LARGE_FMS_INCR[] = "PFD_LARGE_FMS_INCR";
const PROGMEM char LARGE_FMS_DECR[] = "PFD_LARGE_FMS_DECR";
const PROGMEM char SMALL_FMS_INCR[] = "PFD_SMALL_FMS_INCR";
const PROGMEM char SMALL_FMS_DECR[] = "PFD_SMALL_FMS_DECR";
const PROGMEM char SMALL_FMS_PRESS[] = "PFD_SMALL_FMS_PRESS";
const PROGMEM char SOFTKEY_1[] = "PFD_SOFTKEY_1";
const PROGMEM char SOFTKEY_2[] = "PFD_SOFTKEY_2";
const PROGMEM char SOFTKEY_3[] = "PFD_SOFTKEY_3";
const PROGMEM char SOFTKEY_4[] = "PFD_SOFTKEY_4";
const PROGMEM char SOFTKEY_5[] = "PFD_SOFTKEY_5";
const PROGMEM char SOFTKEY_6[] = "PFD_SOFTKEY_6";
const PROGMEM char SOFTKEY_7[] = "PFD_SOFTKEY_7";
const PROGMEM char SOFTKEY_8[] = "PFD_SOFTKEY_8";
const PROGMEM char SOFTKEY_9[] = "PFD_SOFTKEY_9";
const PROGMEM char SOFTKEY_10[] = "PFD_SOFTKEY_10";
const PROGMEM char SOFTKEY_11[] = "PFD_SOFTKEY_11";
const PROGMEM char SOFTKEY_12[] = "PFD_SOFTKEY_12";
#endif  // PFD
#ifdef MFD
const PROGMEM char NAV_FREQ_TOGGLE[] = "MFD_NAV_FREQ_TOGGLE";
const PROGMEM char LARGE_NAV_INCR[] = "MFD_LARGE_NAV_INCR";
const PROGMEM char LARGE_NAV_DECR[] = "MFD_LARGE_NAV_DECR";
const PROGMEM char SMALL_NAV_INCR[] = "MFD_SMALL_NAV_INCR";
const PROGMEM char SMALL_NAV_DECR[] = "MFD_SMALL_NAV_DECR";
const PROGMEM char SMALL_NAV_PRESS[] = "MFD_SMALL_NAV_PRESS";
const PROGMEM char COM_FREQ_TOGGLE[] = "MFD_COM_FREQ_TOGGLE";
const PROGMEM char COM_FREQ_TOGGLE_HOLD[] = "MFD_COM_FREQ_TOGGLE_HOLD";
const PROGMEM char LARGE_COM_INCR[] = "MFD_LARGE_COM_INCR";
const PROGMEM char LARGE_COM_DECR[] = "MFD_LARGE_COM_DECR";
const PROGMEM char SMALL_COM_INCR[] = "MFD_SMALL_COM_INCR";
const PROGMEM char SMALL_COM_DECR[] = "MFD_SMALL_COM_DECR";
const PROGMEM char SMALL_COM_PRESS[] = "MFD_SMALL_COM_PRESS";
const PROGMEM char BARO_INCR[] = "MFD_BARO_INCR";
const PROGMEM char BARO_DECR[] = "MFD_BARO_DECR";
const PROGMEM char RANGE_INCR[] = "MFD_RANGE_INCR";
const PROGMEM char RANGE_DECR[] = "MFD_RANGE_DECR";
const PROGMEM char RANGE_PRESS[] = "MFD_RANGE_PRESS";
const PROGMEM char RANGE_PAN_UP[] = "MFD_RANGE_PAN_UP";
const PROGMEM char RANGE_PAN_DOWN[] = "MFD_RANGE_PAN_DOWN";
const PROGMEM char RANGE_PAN_LEFT[] = "MFD_RANGE_PAN_LEFT";
const PROGMEM char RANGE_PAN_RIGHT[] = "MFD_RANGE_PAN_RIGHT";
const PROGMEM char DIRECT_TO[] = "MFD_DIRECT_TO";
const PROGMEM char MENU[] = "MFD_MENU";
const PROGMEM char FPL[] = "MFD_FPL";
const PROGMEM char PROC[] = "MFD_PROC";
const PROGMEM char CLR[] = "MFD_CLR";
const PROGMEM char ENT[] = "MFD_ENT";
const PROGMEM char LARGE_FMS_INCR[] = "MFD_LARGE_FMS_INCR";
const PROGMEM char LARGE_FMS_DECR[] = "MFD_LARGE_FMS_DECR";
const PROGMEM char SMALL_FMS_INCR[] = "MFD_SMALL_FMS_INCR";
const PROGMEM char SMALL_FMS_DECR[] = "MFD_SMALL_FMS_DECR";
const PROGMEM char SMALL_FMS_PRESS[] = "MFD_SMALL_FMS_PRESS";
const PROGMEM char SOFTKEY_1[] = "MFD_SOFTKEY_1";
const PROGMEM char SOFTKEY_2[] = "MFD_SOFTKEY_2";
const PROGMEM char SOFTKEY_3[] = "MFD_SOFTKEY_3";
const PROGMEM char SOFTKEY_4[] = "MFD_SOFTKEY_4";
const PROGMEM char SOFTKEY_5[] = "MFD_SOFTKEY_5";
const PROGMEM char SOFTKEY_6[] = "MFD_SOFTKEY_6";
const PROGMEM char SOFTKEY_7[] = "MFD_SOFTKEY_7";
const PROGMEM char SOFTKEY_8[] = "MFD_SOFTKEY_8";
const PROGMEM char SOFTKEY_9[] = "MFD_SOFTKEY_9";
const PROGMEM char SOFTKEY_10[] = "MFD_SOFTKEY_10";
const PROGMEM char SOFTKEY_11[] = "MFD_SOFTKEY_11";
const PROGMEM char SOFTKEY_12[] = "MFD_SOFTKEY_12";
#endif  // MFD

#ifdef GFC700
const char AFCS_AP[] = "AFCS_AP";
const char AFCS_HDG[] = "AFCS_HDG";
const char AFCS_NAV[] = "AFCS_NAV";
const char AFCS_APR[] = "AFCS_APR";
const char AFCS_VS[] = "AFCS_VS";
const char AFCS_FLC[] = "AFCS_FLC";
const char AFCS_FD[] = "AFCS_FD";
const char AFCS_ALT[] = "AFCS_ALT";
const char AFCS_VNV[] = "AFCS_VNV";
const char AFCS_BC[] = "AFCS_BC";
const char AFCS_UP[] = "AFCS_UP";
const char AFCS_DN[] = "AFCS_DN";
#endif  // GFC700

/*
 * TODO: Add support for these features:
 *
 * MFD_RANGE_PAN_HOLD
 * MFD_RANGE_PAN_RELEASE
 * COM_FREQ_TOGGLE_HOLD
 * MFD_CLR_HOLD
 * PFD Reversionary mode
 */

typedef const char *Control;

// Pure virtual base class for input handlers.
class InputHandler {
 public:
  // row_index and pin_a_index are required and must be valid indices into
  // kRowPins and kColumnPins.  pin_b_index is optional.
  InputHandler(int row_index, int pin_a_index, int pin_b_index = -1) :
      row_index_(row_index),
      pin_a_index_(pin_a_index),
      pin_b_index_(pin_b_index),
      row_pin_(kRowPins[row_index]),
      pin_a_(kColumnPins[pin_a_index]),
      pin_b_(pin_b_index > 0 ? kColumnPins[pin_b_index]: -1) {

  }

  // Return NULL if no event should be generated.  Otherwise return
  // event string.  All strings returned must be global constants.
  virtual Control trigger(int pin, int val) = 0;

  // Get the row and columns for associated pins.  Return -1 if the pin
  // is not populated.  A given input handler may not span multiple rows.
  int get_row() { return row_index_; }
  int get_pin_a_column() { return pin_a_index_; }
  int get_pin_b_column() { return pin_b_index_; }

 protected:
  int row_index_;
  int pin_a_index_;
  int pin_b_index_;
  int row_pin_;
  int pin_a_;
  int pin_b_;
};

// Input matrix handler.  Scans the matrix row by row looking for changes in
// pin states.  Triggers associated handlers when pin states change.
class InputMatrix {
 public:
  InputMatrix() : current_row_(0) {
    // Row pins are pulled low when being scanned.  Set them all high to
    // disable all rows on startup.
    for (int i = 0; i < MATRIX_ROWS; ++i) {
      pinMode(kRowPins[i], OUTPUT);
      digitalWrite(kRowPins[i], HIGH);
    }
    for (int i = 0; i < MATRIX_COLS; ++i) {
      pinMode(kColumnPins[i], INPUT_PULLUP);
    }

    // Scan the rows once with handlers suppressed to initialize last_vals_.
    for (int i = 0; i < MATRIX_ROWS; ++i) {
      scan_row(true);
    }
  }

  // Inserts an input handler into the matrix.  Caller retains ownership of
  // target. Returns false if target has invalid row or pin indices or if
  // target is null.
  bool insert(InputHandler *target) {
    if (NULL == target) return false;

    int row = target->get_row();
    int pin_a_column = target->get_pin_b_column();
    int pin_b_column = target->get_pin_b_column();

    if (row >= MATRIX_ROWS ||
        pin_a_column >= MATRIX_COLS ||
        pin_b_column >= MATRIX_COLS) {
      return false;
    }

    handlers_[row][pin_a_column] = target;

    if (pin_b_column >= 0) {
      handlers_[row][pin_b_column] = target;
    }
    return true;
  }

  // Scan the current row for pin state changes.
  void scan_row(bool suppress_handlers = false) {
    for (int i = 0; i < MATRIX_COLS; ++i) {
      InputHandler *handler = handlers_[current_row_][i];
      int val = digitalRead(kColumnPins[i]);
      int last = last_vals_[current_row_][i];
      last_vals_[current_row_][i] = val;

      if (suppress_handlers) continue;
      if (val == last) continue;
      if (NULL == handler) continue;

      Control result = handler->trigger(kColumnPins[i], val);
      if (NULL != result) {
        Serial.println(result);
      }
    }

    // Disable the current row, wait for voltages to settle, and move to the
    // next row.
    digitalWrite(kRowPins[current_row_], HIGH);
    delayMicroseconds(50);
    current_row_ = (current_row_ + 1) % MATRIX_ROWS;
    digitalWrite(kRowPins[current_row_], LOW);
  }

 private:
  // The index of the current row to be scanned.
  int current_row_;

  // Mapping from pin indices to input handlers.  The input handlers are
  // notified when their associated pins change state.
  InputHandler *handlers_[MATRIX_ROWS][MATRIX_COLS] = {};

  // Values seen at each matrix position on the last scan.
  int last_vals_[MATRIX_ROWS][MATRIX_COLS];
};

// Handles a simple active low momentary button.  No builtin debounce.
class Button : public InputHandler {
  Control control_;

 public:
  Button(Control control, int row_index, int col_index) :
      InputHandler(row_index, col_index),
      control_(control) {}

  virtual Control trigger(int pin, int val) {
    if (pin != pin_a_) return NULL;
    if (val == LOW && digitalRead(pin_a_) == LOW) return control_;
    return NULL;
  }
};

// Handles most quadrature encoders.
// Tested with ELMA E37 and Bournes PEC11R series.
// Set double_pulse = true for encoders that generate two pulses per detent.
class Encoder : public InputHandler {
 protected:
  Control left_control_;
  Control right_control_;
  bool double_pulse_;

 public:
  Encoder(Control left, Control right, int row_index, int pin_a_index,
          int pin_b_index, bool double_pulse = false)
      : InputHandler(row_index, pin_a_index, pin_b_index),
        left_control_(left),
        right_control_(right),
        double_pulse_(double_pulse) {}

  virtual Control trigger(int pin, int val) {
    if (pin == pin_a_ && LOW == val) {
      if (LOW == digitalRead(pin_b_)) {
        return left_control_;
      }
      return right_control_;
    }
    if (!double_pulse_ && pin == pin_b_ && HIGH == val) {
      if (LOW == digitalRead(pin_a_)) {
        return left_control_;
      }
      return right_control_;
    }
    return NULL;
  }
};

// Handles the quadrature encoder in a Grayhill 60A joystick / encoder.
// That encoder has a detent at every pin state change, which requires
// slightly different logic than the other encoders.
class OptoEncoder : public InputHandler {
  Control pin_a_changed_outputs_[2][2];
  Control pin_b_changed_outputs_[2][2];
  Control left_control_;
  Control right_control_;

 public:
  OptoEncoder(Control left, Control right, int row_index, int pin_a_index,
              int pin_b_index)
      : InputHandler(row_index, pin_a_index, pin_b_index),
        left_control_(left),
        right_control_(right),
        pin_a_changed_outputs_{{left, right}, {right, left}},
        pin_b_changed_outputs_{{right, left}, {left, right}} {}

  virtual Control trigger(int pin, int val) {
    if (pin == pin_a_) {
      int b_val = digitalRead(pin_b_);
      return pin_a_changed_outputs_[val == HIGH][b_val == HIGH];
    }
    if (pin == pin_b_) {
      int a_val = digitalRead(pin_a_);
      return pin_b_changed_outputs_[val == HIGH][a_val == HIGH];
    }
  }
};

// Handles the analog 2 axis joystick in a Grayhill 60A joystick / knob.
class Joystick {
#define ANALOG_MAX 1023
#define AXIS_COUNT 2

 public:
  Joystick(Control left, Control right, Control up, Control down, int pin_x,
           int pin_y) :
      skipped_scan_count_(0) {
    pins_[AXIS_X] = pin_x;
    pins_[AXIS_Y] = pin_y;

    // Initialize last_vals to a value that corresponds to a centered position.
    last_val_[AXIS_X] = 2;
    last_val_[AXIS_Y] = 2;

    low_control_[AXIS_X] = left;
    high_control_[AXIS_X] = right;
    low_control_[AXIS_Y] = down;
    high_control_[AXIS_Y] = up;
  }

  // Maybe scan the joystick for changes.
  void scan(void) {
    // analogRead is slow. We can only afford to do this once every 16
    // matrix scans.
    if (skipped_scan_count_ == 0) {
      scan_axis(AXIS_X);
      scan_axis(AXIS_Y);
    }
    skipped_scan_count_ = (skipped_scan_count_ + 1) % 16;
  }

 private:
  int pins_[AXIS_COUNT];
  int last_val_[AXIS_COUNT];
  int skipped_scan_count_;
  Control low_control_[AXIS_COUNT];
  Control high_control_[AXIS_COUNT];

  enum JoystickAxis {
    AXIS_X = 0,
    AXIS_Y,
  };

  Control trigger_axis(JoystickAxis axis, int val) {
    switch (val) {
      case 0:
        return low_control_[axis];
      case 5:
        return high_control_[axis];
      default:
        return NULL;
    }
  }

  void scan_axis(JoystickAxis axis) {
    int val = analogRead(pins_[axis]);
    if (val > ANALOG_MAX) val = ANALOG_MAX;
    val = map(val, 0, ANALOG_MAX, 0, 5);

    if (val != last_val_[axis]) {
      Control control = trigger_axis(axis, val);
      Serial.println(control);
      last_val_[axis] = val;
    }
  }
};

InputMatrix *input_matrix;
Joystick *range_joystick;

SerialRx serial_rx(IDENTIFIER);

void setup() {
  Serial.begin(9600);
  Serial.println("Booting...");

  input_matrix = new InputMatrix();

  input_matrix->insert(new Button(NAV_ID_TOGGLE, 7, 5));

  input_matrix->insert(new Button(NAV_FREQ_TOGGLE, 7, 4));

  input_matrix->insert(new Encoder(LARGE_NAV_DECR, LARGE_NAV_INCR, 7, 0, 1));
  input_matrix->insert(new Encoder(SMALL_NAV_DECR, SMALL_NAV_INCR, 7, 2, 3));
  input_matrix->insert(new Button(SMALL_NAV_PRESS, 6, 7));

  input_matrix->insert(new Encoder(HDG_DECR, HDG_INCR, 6, 5, 6, true));
  input_matrix->insert(new Button(HDG_PRESS, 6, 4));

#ifdef GFC700
  input_matrix->insert(new Button(AFCS_AP, 0, 8));
  input_matrix->insert(new Button(AFCS_FD, 0, 9));
  input_matrix->insert(new Button(AFCS_HDG, 1, 8));
  input_matrix->insert(new Button(AFCS_ALT, 1, 9));
  input_matrix->insert(new Button(AFCS_NAV, 2, 8));
  input_matrix->insert(new Button(AFCS_VNV, 2, 9));
  input_matrix->insert(new Button(AFCS_APR, 3, 8));
  input_matrix->insert(new Button(AFCS_BC, 3, 9));
  input_matrix->insert(new Button(AFCS_VS, 4, 8));
  input_matrix->insert(new Button(AFCS_UP, 4, 9));
  input_matrix->insert(new Button(AFCS_FLC, 5, 8));
  input_matrix->insert(new Button(AFCS_DN, 5, 9));
#endif  // GFC700

  input_matrix->insert(new Encoder(LARGE_ALT_DECR, LARGE_ALT_INCR, 6, 0, 1));
  input_matrix->insert(new Encoder(SMALL_ALT_DECR, SMALL_ALT_INCR, 6, 2, 3));
  input_matrix->insert(new Button(SMALL_ALT_PRESS, 5, 7));

  input_matrix->insert(new Button(SOFTKEY_1, 5, 6));
  input_matrix->insert(new Button(SOFTKEY_2, 5, 5));
  input_matrix->insert(new Button(SOFTKEY_3, 5, 4));
  input_matrix->insert(new Button(SOFTKEY_4, 5, 3));
  input_matrix->insert(new Button(SOFTKEY_5, 5, 2));
  input_matrix->insert(new Button(SOFTKEY_6, 5, 1));
  input_matrix->insert(new Button(SOFTKEY_7, 5, 0));
  input_matrix->insert(new Button(SOFTKEY_8, 4, 7));
  input_matrix->insert(new Button(SOFTKEY_9, 4, 6));
  input_matrix->insert(new Button(SOFTKEY_10, 4, 5));
  input_matrix->insert(new Button(SOFTKEY_11, 4, 4));
  input_matrix->insert(new Button(SOFTKEY_12, 4, 3));

  input_matrix->insert(new Encoder(LARGE_FMS_DECR, LARGE_FMS_INCR, 0, 0, 1));
  input_matrix->insert(new Encoder(SMALL_FMS_DECR, SMALL_FMS_INCR, 0, 3, 4));
  input_matrix->insert(new Button(SMALL_FMS_PRESS, 0, 2));

  input_matrix->insert(new Button(DIRECT_TO, 1, 6));
  input_matrix->insert(new Button(FPL, 1, 4));
  input_matrix->insert(new Button(CLR, 1, 2));
  input_matrix->insert(new Button(MENU, 1, 5));
  input_matrix->insert(new Button(PROC, 1, 3));
  input_matrix->insert(new Button(ENT, 1, 1));

  input_matrix->insert(new Button(RANGE_PRESS, 1, 7));

  input_matrix->insert(new Encoder(BARO_DECR, BARO_INCR, 2, 3, 4));
  input_matrix->insert(new Encoder(CRS_DECR, CRS_INCR, 2, 5, 6));
  input_matrix->insert(new Button(CRS_PRESS, 2, 2));

  input_matrix->insert(new Encoder(LARGE_COM_DECR, LARGE_COM_INCR, 3, 0, 1));
  input_matrix->insert(new Encoder(SMALL_COM_DECR, SMALL_COM_INCR, 3, 2, 3));
  input_matrix->insert(new Button(SMALL_COM_PRESS, 2, 7));

  input_matrix->insert(new Button(COM_FREQ_TOGGLE, 3, 4));

  input_matrix->insert(new OptoEncoder(RANGE_DECR, RANGE_INCR, 6, 8, 9));
  range_joystick = new Joystick(RANGE_PAN_LEFT, RANGE_PAN_RIGHT, RANGE_PAN_UP,
                                RANGE_PAN_DOWN, 14, 15);
}

void loop() {
  input_matrix->scan_row();
  range_joystick->scan();

  serial_rx.process();
}
