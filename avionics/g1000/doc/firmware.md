# Flashing the firmware

1. Load firmware/g1000.ino into Arduino IDE.
2. Set your sketchbook location to the avionics directory (Under preferences).
3. Install support for the [Feather M0 Proto](https://learn.adafruit.com/adafruit-feather-m0-basic-proto/using-with-arduino-ide).
4. Comment out either "#define PFD" or "#define MFD" at the top of the file.
   If this will be the PFD, leave MFD commented.  Otherwise comment out PFD
   and uncomment MFD.
5. Connect the Arduino to your PC with a micro USB cable.
6. Set the board to "Feather M0 Proto" under "Tools > Board"
7. Set the port under "Tools > Port".
8. Select "Sketch > Upload".
9. Done!
