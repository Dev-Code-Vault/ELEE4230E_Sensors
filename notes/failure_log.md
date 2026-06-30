# Failure Log

## Project Start

- USB cable issue connecting to ESP32
- COM ports 3 and 4 are always on, while port 5 was where the ESP32 was
- ESP32 wouldn't upload, threw timeout errors. Turned out to be a
  charge-only USB cable, not a driver or board issue. Swapping cables
  fixed it instantly.
- After wiring the A1302 + LM358 circuit, readings drifted slowly and
  spiked erratically even with the sensor held still. Root cause was
  a missing common ground between the battery/MT3608 side and the
  ESP32/breadboard rail - fixed with one jumper wire.
- After fixing ground, readings became binary (stuck at either 0 or
  one fixed high value) instead of sweeping smoothly. The LM358 was
  missing its feedback resistor between pin 1 (output) and pin 2
  (inverting input), so it was behaving like a comparator instead of
  a unity-gain buffer. Adding the resistor fixed it.
- Even after that, raw single-sample ADC readings still jittered by
  roughly +/-100 counts. Fixed in firmware by averaging 20 samples
  per print instead of trying to filter it in hardware.