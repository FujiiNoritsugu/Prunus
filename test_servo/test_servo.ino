#include <Servo.h>

Servo servo1;  // サーボモーター1（眉や目の動き）
Servo servo2;  // サーボモーター2（口の動き）
Servo servo3;  // サーボモーター3（首の動き）
Servo servo4;  // サーボモーター4（頭の動き）

void setup() {
  Serial.begin(9600);   // シリアル通信の初期化
  servo1.attach(8);     // サーボモーター1をデジタルピン8に接続
  servo2.attach(9);     // サーボモーター2をデジタルピン9に接続
  servo3.attach(10);    // サーボモーター3をデジタルピン10に接続
  servo4.attach(11);    // サーボモーター4をデジタルピン11に接続
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // シリアルポートからのデータを読み取る

    // JSON形式の解析を行う
    int joyIndex = input.indexOf("\"joy\":");
    int funIndex = input.indexOf("\"fun\":");
    int angerIndex = input.indexOf("\"anger\":");
    int sadIndex = input.indexOf("\"sad\":");

    if (joyIndex != -1 && funIndex != -1 && angerIndex != -1 && sadIndex != -1) {
      int joy = input.substring(joyIndex + 6, joyIndex + 7).toInt();
      int fun = input.substring(funIndex + 6, funIndex + 7).toInt();
      int anger = input.substring(angerIndex + 8, angerIndex + 9).toInt();
      int sad = input.substring(sadIndex + 6, sadIndex + 7).toInt();

      // 0〜5の値に基づいてサーボモータの角度を設定
      servo1.write(map(joy, 0, 5, 0, 180));  // joyが0〜5のとき、角度を0〜180度にマッピング
      servo2.write(map(fun, 0, 5, 0, 180));  // funが0〜5のとき、角度を0〜180度にマッピング
      servo3.write(map(anger, 0, 5, 0, 180));  // angerが0〜5のとき、角度を0〜180度にマッピング
      servo4.write(map(sad, 0, 5, 0, 180));  // sadが0〜5のとき、角度を0〜180度にマッピング

      Serial.print("Emotion set to - Joy: ");
      Serial.print(joy);
      Serial.print(", Fun: ");
      Serial.print(fun);
      Serial.print(", Anger: ");
      Serial.print(anger);
      Serial.print(", Sad: ");
      Serial.println(sad);
    }
  }
}
