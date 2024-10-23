#include <Servo.h>

Servo servo1;  // サーボモーター1（眉や目の動き）
Servo servo2;  // サーボモーター2（口の動き）

void setup() {
  Serial.begin(9600);  // シリアル通信の初期化
  servo1.attach(9);    // サーボモーター1をデジタルピン9に接続
  servo2.attach(10);   // サーボモーター2をデジタルピン10に接続
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // シリアルポートからのデータを読み取る
    if (input == "happy") {
      // 喜びの表情
      servo1.write(30);  // 目や眉の位置
      servo2.write(60);  // 口の位置
    } else if (input == "angry") {
      // 怒りの表情
      servo1.write(150);  // 目や眉の位置
      servo2.write(30);   // 口の位置
    } else if (input == "sad") {
      // 悲しみの表情
      servo1.write(120);  // 目や眉の位置
      servo2.write(90);   // 口の位置
    } else if (input == "neutral") {
      // ニュートラルな表情
      servo1.write(90);   // 目や眉の位置
      servo2.write(90);   // 口の位置
    }
    Serial.print("Expression set to: ");
    Serial.println(input);
  }
}
