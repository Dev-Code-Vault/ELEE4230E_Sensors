// mpu6050_angle_reading.ino 
// with updated "zero"

#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

Adafruit_MPU6050 mpu;

// for "zero" changed with zero_offset = -9.30° = (-9.08 + -9.43 + -9.05 + -9.64 + -9.30 + -9.25 + -9.28) / 7 = -9.29°
float zero_offset = -9.30;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(21, 22); // ESP32 SDA = 21, SCL = 22

  if (!mpu.begin()) {
    Serial.println("MPU6050 not found");
    while (1) {
      delay(10);
    }
  }

  Serial.println("time_ms,accel_x,accel_y,accel_z,raw_angle_deg,angle_deg");
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // For your current upright/breadboard orientation
  float raw_angle_deg = atan2(a.acceleration.z, a.acceleration.x) * 180.0 / PI;

  // Calibrated angle
  float angle_deg = raw_angle_deg - zero_offset;

  Serial.print(millis());
  Serial.print(",");
  Serial.print(a.acceleration.x);
  Serial.print(",");
  Serial.print(a.acceleration.y);
  Serial.print(",");
  Serial.print(a.acceleration.z);
  Serial.print(",");
  Serial.print(raw_angle_deg);
  Serial.print(",");
  Serial.println(angle_deg);

  delay(200);
}