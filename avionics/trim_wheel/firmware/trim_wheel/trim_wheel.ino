#include <movingAvg.h>
#include <serial_rx.h>

#include "trim_stepper.h"

#define POSITION_PIN 0 // replace with actual pin
#define CENTER 475
#define DEAD_ZONE 2
#define POT_MAX 950
#define POT_MIN 50
#define POT_RANGE (POT_MAX - POT_MIN)
#define API_MAX 4096
#define REVOLUTIONS 9
#define ENCODER_MAX 4096

class TrimWheel : public SerialRx {
 public:
  TrimWheel() :
      SerialRx("TRIM"),
      driving_(false),
      target_pot_(CENTER),
      last_pot_(-1),
      pot_base_(-1),
      last_encoder_(0),
      encoder_offset_(0),
      encoder_base_(0),
      motor_state_(STOP),
      avg_value_(4) {
    Serial.begin(9600);
    trim_stepper_init();
    avg_value_.begin();
    ReadPot();
    SetEncoderBase();
  }

  int ApiToPot(int api_val) { return (api_val * POT_RANGE) / API_MAX + POT_MIN; }
  int PotToApi(int pot_val) { return ((pot_val - POT_MIN) * API_MAX) / POT_RANGE; }
  int EncoderToApi(int encoder_val) { return encoder_val * API_MAX / ENCODER_MAX / REVOLUTIONS; }
    
  void reset() {
    target_pot_ = CENTER;
    driving_ = true;
  }

  void line_rx() {
    if (strncmp(read_buffer, "POSITION:", 9) == 0) {
      int new_target = atoi(&read_buffer[9]);
      if (new_target >= 0 && new_target <= API_MAX) {
        driving_ = true;
        target_pot_ = ApiToPot(new_target);
      }
    }
    else if (strncmp(read_buffer, "POSITION?", 9) == 0) {
      Serial.print("POSITION:");
      Serial.println(PotToApi(last_pot_));
    }
    else if (strncmp(read_buffer, "RELEASE", 6) == 0) {
      driving_ = false;
    }
  }

  void ReadPot() {
    int value = avg_value_.reading(analogRead(POSITION_PIN));
    last_pot_ = value;
  }

  void ReadEncoderOffset() {
    int value = 0;//encoder.GetAngle();
    int difference = 0;
    if (value - last_encoder_ > ENCODER_MAX / 2){
      difference = value - (ENCODER_MAX + last_encoder_);
    } else if (last_encoder_ - value > ENCODER_MAX / 2) {
      difference = ENCODER_MAX - last_encoder_ + value;
    } else {
      difference = value - last_encoder_;
    }

    encoder_offset_ += difference;
  }

  void SetEncoderBase() {
    encoder_base_ = 0;//encoder.GetAngle();
    encoder_offset_ = 0;
    pot_base_ = last_pot_;
  }

  void DriveStepper() {
    int difference = last_pot_ - target_pot_;
    bool target_reached = abs(difference) <= DEAD_ZONE;
    if (target_reached) {
      driving_ = false;
      trim_stepper_stop();
      motor_state_ = STOP;
      SetEncoderBase();
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

  void ReleaseStepper() {
    if (motor_state_ != STOP) {
      trim_stepper_stop();
      motor_state_ = STOP;
      SetEncoderBase();
    }
  }

  void SendPosition() {
    int encoder_offset = EncoderToApi(encoder_base_ + encoder_offset_);
    int driven_position = PotToApi(last_pot_);
    Serial.print("POSITION:");
    Serial.println(driven_position + encoder_offset);
  }

  void process() {
    SerialRx::process();

    ReadPot();

    if (driving_) {
      DriveStepper();
    } else {
      ReleaseStepper();
      ReadEncoderOffset();
      SendPosition();
    }
}
 private:
  enum MotorState {
    STOP = 0,
    FORWARD = 1,
    BACKWARD = 2,
  };
  bool driving_;
  int target_pot_;
  int last_pot_;
  int pot_base_;
  int last_encoder_;
  int encoder_offset_;
  int encoder_base_;
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
