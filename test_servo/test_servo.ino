#include <Servo.h>
#include <ArduinoJson.h>

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;

void setup() {
  Serial.begin(9600);
  servo1.attach(8);
  servo2.attach(9);
  servo3.attach(10);
  servo4.attach(11);
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // シリアルポートからのデータを読み取る
    
    // JSON解析用のStaticJsonDocumentを宣言
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, input);

    // JSON解析が失敗した場合はエラーメッセージを出力
    if (error) {
      Serial.print("JSON parse error: ");
      Serial.println(error.c_str());
      return;
    }

    // JSONからデータを取得
    int joy = doc["joy"] | -1;
    int fun = doc["fun"] | -1;
    int anger = doc["anger"] | -1;
    int sad = doc["sad"] | -1;

    // 値が有効な範囲かを確認し、範囲外であれば無視
    if (joy >= 0 && joy <= 5 && fun >= 0 && fun <= 5 && anger >= 0 && anger <= 5 && sad >= 0 && sad <= 5) {
      servo1.write(map(joy, 0, 5, 0, 180));
      servo2.write(map(fun, 0, 5, 0, 180));
      servo3.write(map(anger, 0, 5, 0, 180));
      servo4.write(map(sad, 0, 5, 0, 180));

      Serial.print("Emotion set to - Joy: ");
      Serial.print(joy);
      Serial.print(", Fun: ");
      Serial.print(fun);
      Serial.print(", Anger: ");
      Serial.print(anger);
      Serial.print(", Sad: ");
      Serial.println(sad);
    } else {
      Serial.println("Emotion values out of range.");
    }
  }
}
