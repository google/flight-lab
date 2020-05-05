
#include "dimmer_box.h"

DimmerBox::DimmerBox(uint8_t clock_pin, uint8_t data_pin, uint8_t latch_pin) {
  _clock_pin = clock_pin;
  _data_pin = data_pin;
  _latch_pin = latch_pin;
  
  pwmbuffer = (uint16_t *) malloc(sizeof(uint16_t) * 24);
}

DimmerBox::~DimmerBox(void) {
  if(pwmbuffer){
    free(pwmbuffer);
    pwmbuffer = nullptr;
  }
}

void DimmerBox::update(void) {
  digitalWrite(_latch_pin, LOW);
  // 24 channels per TLC5974
  for (int16_t c = 23; c >= 0 ; --c) {
    // 12 bits per channel, send MSB first
    for (int8_t b = 11; b >= 0; --b) {
      digitalWrite(_clock_pin, LOW);
      digitalWrite(_data_pin, pwmbuffer[c] & (1 << b) ? LOW : HIGH);
      digitalWrite(_clock_pin, HIGH);
    }
  }
  digitalWrite(_clock_pin, LOW);
  digitalWrite(_data_pin, LOW);
  
  digitalWrite(_latch_pin, HIGH);
  digitalWrite(_latch_pin, LOW);
}

void DimmerBox::set(uint16_t channel, uint16_t value) {
  // The optocouplers used cannot respond fast enough to ensure full MOSFET switching
  // much below 150, or above 4000 - clip at 150 and 4000 to avoid accidently operating 
  // the MOSFETS in linear mode which may cause overheating and failure.
  if (value > 4000) value = 4095;
  if (value < 150) value = 0;
  if (channel > 24 || channel == 0) return;
  pwmbuffer[channel - 1] = value;  
}

uint16_t DimmerBox::get(uint16_t channel) {
  if (channel > 24 || channel == 0) return 0;
  return pwmbuffer[channel - 1];  
}

void DimmerBox::connect(void) {
  pinMode(_clock_pin, OUTPUT);
  pinMode(_data_pin, OUTPUT);
  pinMode(_latch_pin, OUTPUT);
  digitalWrite(_latch_pin, LOW);
  // memsetting all bytes to 8 sets a value of 2056 or about half brightness.
  memset(pwmbuffer, 8, 2 * 24);
  update();
}

