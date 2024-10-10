import serial
import time
import httpx

# シリアルポートの設定
ser = serial.Serial(
    "/dev/ttyACM0", 9600
)  # 'COM3' はArduinoが接続されているポートに変更（例: '/dev/ttyACM0'）

sensor_data = []  # センサデータのリスト
interval = 5  # データ送信の間隔（秒）

# センサデータの範囲（例として、センサの出力が0～1023の範囲と仮定）
sensor_min = 0
sensor_max = 1023


def map_to_range(value, in_min, in_max, out_min, out_max):
    """値を指定した範囲に線形変換する関数"""
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


try:
    start_time = time.time()
    while True:
        if ser.in_waiting > 0:  # 受信データがあるか確認
            line = ser.readline().decode("utf-8").rstrip()  # データの読み取り
            try:
                value = float(line)  # 数値に変換
                sensor_data.append(value)  # リストに追加
                print(f"Received data: {value}")  # 取得したデータを表示
            except ValueError:
                print(f"Invalid data: {line}")  # 無効なデータの場合はスキップ

        # 5秒ごとにデータを送信
        current_time = time.time()
        if current_time - start_time >= interval:
            if sensor_data:
                # 平均値の計算
                average_value = sum(sensor_data) / len(sensor_data)
                # 0～100の範囲に変換
                mapped_value = map_to_range(
                    average_value, sensor_min, sensor_max, 0, 100
                )
                # GETリクエストを送信
                try:
                    response = httpx.get(
                        "http://localhost:8000/sensor_data",
                        params={"data": mapped_value},
                    )
                    print(
                        f"Sent mapped data: {mapped_value}, Response: {response.status_code}"
                    )
                except httpx.RequestError as e:
                    print(f"An error occurred while requesting: {e}")
                # センサデータのリストをリセット
                sensor_data = []
            start_time = current_time
except KeyboardInterrupt:
    print("終了します。")
finally:
    ser.close()  # シリアルポートを閉じる
