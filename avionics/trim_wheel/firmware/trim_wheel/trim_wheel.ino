#include <movingAvg.h>
#include <serial_rx.h>

#include "trim_stepper.h"

#define POSITION_PIN 0 // replace with actual pin
#define CENTER 475
#define DEAD_ZONE 2

class TrimWheel : public SerialRx {
 public:
  TrimWheel() :
      SerialRx("TRIM"),
      driving_(false),
      target_value_(CENTER),
      last_value_(-1),
      motor_state_(STOP),
      avg_value_(10) {
    Serial.begin(9600);
    trim_stepper_init();
    avg_value_.begin();
  }

  void reset() {
    target_value_ = CENTER;
    driving_ = true;
  }

  void line_rx() {
    if (strncmp(read_buffer, "POSITION:", 9) == 0) {
      int new_target = atoi(&read_buffer[9]);
      if (new_target >= 50 && new_target <= 950) {
        driving_ = true;
        target_value_ = new_target;
      }
    }
    else if (strncmp(read_buffer, "POSITION?", 9) == 0) {
      Serial.print("POSITION:");
      Serial.println(last_value_);
    }
    else if (strncmp(read_buffer, "RELEASE", 6) == 0) {
      driving_ = false;
    }
  }

  void process() {
    SerialRx::process();

    int value = avg_value_.reading(analogRead(POSITION_PIN));

    int difference = last_value_ - value;
    bool non_zero = abs(difference) > DEAD_ZONE;
    if (non_zero) {
      last_value_ = value;
    }

    if (!driving_) {
      if (motor_state_ != STOP) {
        trim_stepper_stop();
        motor_state_ = STOP;
      }
      if (non_zero) {
        Serial.print("POSITION:");
        Serial.println(last_value_);
      }
      return;
    }

    difference = value - target_value_;
    non_zero = abs(difference) > DEAD_ZONE;
    if (!non_zero) {
      driving_ = false;
      trim_stepper_stop();
      motor_state_ = STOP;
    }
    else if (difference > 0 && motor_state_ != FORWARD) {
      trim_stepper_forward();
      motor_state_ = FORWARD;
    }
    else if (difference < 0 && motor_state_ != BACKWARD) {
      trim_stepper_backward();
      motor_state_ = BACKWARD;
    }
    
  }
 private:
  enum MotorState {
    STOP = 0,
    FORWARD = 1,
    BACKWARD = 2,
  };
  bool driving_;
  int target_value_;
  int last_value_;
  movingAvg avg_value_;
  MotorState motor_state_;
};

TrimWheel* trim_wheel;

void setup() {
  trim_wheel = new TrimWheel();
}

void loop() {
  trim_wheel->process();
}
