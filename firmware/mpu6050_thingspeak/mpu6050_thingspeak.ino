#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "secrets.h"

Adafruit_MPU6050 mpu;

const char* ssid     = WIFI_SSID;
const char* password = WIFI_PASSWORD;

const char* apiKey   = THINGSPEAK_KEY;
const char* server    = "http://api.thingspeak.com/update";

float zero_offset = -9.30;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  if (!mpu.begin()) {
    Serial.println("MPU6050 not found");
    while (1) delay(10);
  }

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected. IP: " + WiFi.localIP().toString());
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  float raw_angle = atan2(a.acceleration.z, a.acceleration.x) * 180.0 / PI;
  float angle_deg = -(raw_angle - zero_offset);

  Serial.print("Angle: ");
  Serial.println(angle_deg);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(server) + "?api_key=" + apiKey + "&field1=" + String(angle_deg);
    http.begin(url);
    int code = http.GET();
    Serial.println(code > 0 ? "ThingSpeak OK" : "ThingSpeak FAIL");
    http.end();
  }

  delay(20000); // ThingSpeak free tier minimum = 15 seconds
}