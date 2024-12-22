#include "esp_camera.h"
#include <WiFi.h>

// Chọn model camera
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// Thông tin WiFi
const char *ssid = "WifiName";
const char *password = "password";

void startCameraServer();

void setup() {
  Serial.begin(115200);
  Serial.println();

  // Cấu hình camera
  camera_config_t config = {
    .ledc_channel = LEDC_CHANNEL_0,
    .ledc_timer = LEDC_TIMER_0,
    .pin_d0 = Y2_GPIO_NUM,
    .pin_d1 = Y3_GPIO_NUM,
    .pin_d2 = Y4_GPIO_NUM,
    .pin_d3 = Y5_GPIO_NUM,
    .pin_d4 = Y6_GPIO_NUM,
    .pin_d5 = Y7_GPIO_NUM,
    .pin_d6 = Y8_GPIO_NUM,
    .pin_d7 = Y9_GPIO_NUM,
    .pin_xclk = XCLK_GPIO_NUM,
    .pin_pclk = PCLK_GPIO_NUM,
    .pin_vsync = VSYNC_GPIO_NUM,
    .pin_href = HREF_GPIO_NUM,
    .pin_sccb_sda = SIOD_GPIO_NUM,
    .pin_sccb_scl = SIOC_GPIO_NUM,
    .pin_pwdn = PWDN_GPIO_NUM,
    .pin_reset = RESET_GPIO_NUM,
    .xclk_freq_hz = 20000000,
    .frame_size = FRAMESIZE_UXGA,
    .pixel_format = PIXFORMAT_JPEG,
    .fb_location = CAMERA_FB_IN_PSRAM,
    .jpeg_quality = 12,
    .fb_count = 2
  };

  // Khởi tạo camera
  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera init failed");
    return;
  }

  // Kết nối WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  // Bắt đầu server
  startCameraServer();

  Serial.println("Camera Ready! Visit:");
  Serial.println(WiFi.localIP());
}

void loop() {
  delay(10000);
}
