// CP3 - A1302 Hall Effect Raw Sensor
// Reads the A1302 through the LM358 buffer + scaling divider, averages a
// batch of samples to knock down ADC jitter, then prints to serial.
//
// Signal chain: A1302 (5V) -> LM358 buffer (5V, unity gain) ->
//               10k/15k scaling divider -> ESP32 ADC (GPIO34)
//
// We undo the scaling divider in software below so the printed
// "lm358_output_volts" column reflects the actual op-amp output,
// not just whatever shows up at the ESP32 pin.

const int SENSOR_PIN = 34;       // GPIO34 (ADC1_CH6), input-only pin, good for analog
const float ADC_MAX = 4095.0;    // ESP32 ADC is 12-bit
const float ADC_VREF = 3.3;      // ESP32 ADC reference voltage
const float DIVIDER_RATIO = 0.6; // our 15k/(10k+15k) scaling divider
const int NUM_SAMPLES = 20;      // how many readings to average per print

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("CP3 - A1302 Raw Sensor (Averaged)");
  Serial.println("raw_adc_avg, esp32_pin_volts, lm358_output_volts");
}

void loop() {
  // Average a batch of samples instead of trusting a single ADC read -
  // the ESP32 ADC is noisy enough on its own that single readings
  // jump around by 100+ counts even with the sensor sitting still.
  long sum = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogRead(SENSOR_PIN);
    delay(2);
  }
  float avgADC = (float)sum / NUM_SAMPLES;

  float pinVoltage = (avgADC / ADC_MAX) * ADC_VREF;
  float lm358OutputVoltage = pinVoltage / DIVIDER_RATIO;

  Serial.print(avgADC, 1);
  Serial.print(", ");
  Serial.print(pinVoltage, 3);
  Serial.print(", ");
  Serial.println(lm358OutputVoltage, 3);

  delay(150);
}
