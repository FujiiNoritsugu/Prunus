import serial

# シリアルポートの設定
ser = serial.Serial('/dev/ttyACM0', 9600)  # 'COM3' はArduinoが接続されているポートに変更（例: '/dev/ttyACM0'）

try:
    while True:
        if ser.in_waiting > 0:  # 受信データがあるか確認
            line = ser.readline().decode('utf-8').rstrip()  # データの読み取り
            print(f"Received data: {line}")  # 取得したデータを表示
except KeyboardInterrupt:
    print("終了します。")
finally:
    ser.close()  # シリアルポートを閉じる
