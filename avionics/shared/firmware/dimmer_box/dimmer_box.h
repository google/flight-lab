#ifndef _DIMMER_BOX_H
#define _DIMMER_BOX_H

#include <Arduino.h>

/*
 * The Dimmer Box is built on an TLC5947 (http://www.ti.com/lit/ds/symlink/tlc5947.pdf).
 * 
 * The box itself exposes 18 of the 24 available channels, the remaining 6 channels
 * are available but not connected - they could be exposed if needed.
 * 
 * Latch and Blank pins on the TLC5947 are tied together to prevent flickering.
 */
class DimmerBox {
 public:
  DimmerBox(uint8_t clock_pin, uint8_t data_pin, uint8_t latch_pin);
  ~DimmerBox(void);

  void connect(void);
  
  /*
   * Sets the PWM value on the given channel.
   * 
   * Args
   *   channel: Channel number from 1 to 24 inclusive.
   *   value: PWM value from 0 to 4095.
   */
  void set(uint16_t channel, uint16_t value);
  
  /*
   * Gets the PWM value set for a given channel.
   */
  uint16_t get(uint16_t channel);
  
  /*
   * Update pushes the current set values to the PWM controller.
   * This process takes aprox 1.5ms
   */
  void update(void);

 private:
  uint16_t *pwmbuffer;
  uint8_t _clock_pin, _data_pin, _latch_pin;
};
#endif

