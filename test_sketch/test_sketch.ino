// 圧力センサのピンを指定
const int pressureSensorPin = A0;

void setup() {
  // シリアル通信を開始
  Serial.begin(9600);
}

void loop() {
  // 圧力センサからアナログ値を読み取る（0〜1023の範囲）
  int sensorValue = analogRead(pressureSensorPin);
  
  // 読み取った値をシリアルモニタに表示
  // Serial.print("Pressure Sensor Value: ");
  Serial.println(sensorValue);
  
  // 0.5秒待つ
  delay(500);
}
