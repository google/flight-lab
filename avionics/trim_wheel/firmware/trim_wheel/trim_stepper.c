#include <Arduino.h>

#define _PIN_A1 22
#define _PIN_A2 24
#define _PIN_PWMA 9
#define _PIN_B1 28
#define _PIN_B2 30
#define _PIN_PWMB 10
#define _PIN_STBY 26

// Timer values are the compare value at prescaler 8
// That means timer value can be calculated from desire frequency F with:
//   16,000,000 [clock speed] / 8 [prescaler] / F
// Example:
//   To step every 8ms, frequency is 125 Hz. That gives timer value
//   16,000,000 / 8 / 125 = 16,000
//
// To caluclate desired frequency from desired RPM, consider:
//  - Motor has 200 full steps per revolution
//  - We are microstepping with sizeof(_curve)/2 = 4 microsteps per full step.
// If desired RPM is R, then desired frequency (microsteps per second) is
//     R*4*200 / 60
//
// Putting all together, the relationship between RPM and timer value is
//   Timer value = 150,000 / RPM
#define SPEED_RAMP_START 20000  // Timer value for initial speed (~7.5 RPM)
#define SPEED_RAMP_END 10000    // Timer value for final speed (~15 RPM)
#define SPEED_RAMP_ALPHA 100    // Ramp up alpha. Lower values give faster ramp

#if SPEED_RAMP_START < SPEED_RAMP_END
#error SPEED_RAMP_START must be larger than SPEED_RAM_END
#endif

// Stores half the period of a sine curve in twice the desired number of microsteps, on the scale 0-255.
static const uint8_t _curve[8] =  {0, 97, 180, 235, 255, 235, 180, 97};

#define CTR_SIGN (sizeof(_curve))
#define CTR_MASK (CTR_SIGN - 1)

static uint8_t _ctrA, _ctrB, _stepsize;

static inline void _step(int8_t n) {
  _ctrA = (_ctrA + n) & (CTR_SIGN | CTR_MASK);
  _ctrB = (_ctrB + n) & (CTR_SIGN | CTR_MASK);

  // A1 and A2 should be set as follows:
  //    - HIGH, HIGH  if curve value is zero, which only happens when _ctrA is zero
  //    - HIGH, LOW   if curve value is positive, i.e. the sign bit is not set
  //    - LOW,  HIGH  if curve value is negative, i.e. the sign bit is set
  // PWMA is set to the absolute curve value
  digitalWrite(_PIN_A1, (_ctrA & CTR_MASK) == 0 || (_ctrA & CTR_SIGN) == 0 ? HIGH : LOW);
  digitalWrite(_PIN_A2, (_ctrA & CTR_MASK) == 0 || (_ctrA & CTR_SIGN) != 0 ? HIGH : LOW);
  analogWrite(_PIN_PWMA, _curve[_ctrA & CTR_MASK]);

  // Identical logic to the A phase
  digitalWrite(_PIN_B1, (_ctrB & CTR_MASK) == 0 || (_ctrB & CTR_SIGN) == 0 ? HIGH : LOW);
  digitalWrite(_PIN_B2, (_ctrB & CTR_MASK) == 0 || (_ctrB & CTR_SIGN) != 0 ? HIGH : LOW);
  analogWrite(_PIN_PWMB, _curve[_ctrB & CTR_MASK]);
}

void trim_stepper_init() {
  _ctrA = 0;
  _ctrB = sizeof(_curve)/2;  // 90 degree phase offset from A
  pinMode(_PIN_A1, OUTPUT);
  pinMode(_PIN_A2, OUTPUT);
  pinMode(_PIN_B1, OUTPUT);
  pinMode(_PIN_B2, OUTPUT);
  pinMode(_PIN_STBY, OUTPUT);
  digitalWrite(_PIN_STBY, LOW);  // start in STBY
  noInterrupts();
  TCCR5A = 0;
  TCCR5B = 0;
  TCNT5 = 0;
  OCR5A = SPEED_RAMP_START;           // 125 Hz  (16M / 8 / 125)
  TCCR5B |= (1 << WGM12);  // CTC mode
  TCCR5B |= (1 << CS11);   // prescaler 8
  TIMSK5 |= (1 << OCIE5A); // input compare match interrupt
  interrupts();
}

void trim_stepper_forward() {
  _stepsize = 1;
  noInterrupts();
  OCR5A = SPEED_RAMP_START;
  TIMSK5 |= (1 << OCIE5A);  // Enable input compare match interrupt
  interrupts();
  digitalWrite(_PIN_STBY, HIGH);
}

void trim_stepper_backward() {
  _stepsize = -1;
  noInterrupts();
  OCR5A = SPEED_RAMP_START;
  TIMSK5 |= (1 << OCIE5A);  // Enable input compare match interrupt
  interrupts();
  digitalWrite(_PIN_STBY, HIGH);
}

void trim_stepper_stop() {
  noInterrupts();
  TIMSK5 &= ~(1 << OCIE5A);  // Disable input compare match interrupt
  interrupts();
  digitalWrite(_PIN_STBY, LOW);
}

SIGNAL(TIMER5_COMPA_vect) {
  _step(_stepsize);
  if (OCR5A > SPEED_RAMP_END) OCR5A -= (OCR5A - SPEED_RAMP_END)/SPEED_RAMP_ALPHA;
}
