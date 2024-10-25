#include <Servo.h>  // Servoライブラリをインクルード

Servo myservo;      // サーボオブジェクトを作成

void setup() {
  myservo.attach(9);  // サーボを9番ピンに接続
}

void loop() {
  // 0度から180度までの範囲でサーボを動かす
  for (int pos = 0; pos <= 180; pos += 1) {
    myservo.write(pos);  // サーボを指定した角度に動かす
    delay(15);           // 少し待機してスムーズに動かす
  }
  
  // 180度から0度までの範囲でサーボを戻す
  for (int pos = 180; pos >= 0; pos -= 1) {
    myservo.write(pos);  // サーボを指定した角度に動かす
    delay(15);           // 少し待機してスムーズに動かす
  }
}
