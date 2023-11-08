void setup() {
  // LEDピンを出力に設定
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // LEDを点灯
  digitalWrite(LED_BUILTIN, HIGH);

  // 1秒待つ
  delay(1000);

  // LEDを消灯
  digitalWrite(LED_BUILTIN, LOW);

  // 1秒待つ
  delay(1000);
}
