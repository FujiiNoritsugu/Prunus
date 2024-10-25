import serial
import time
import httpx
import asyncio

# シリアルポートの設定
ser = serial.Serial(
    "/dev/ttyACM0", 9600
)  # 'COM3' はArduinoが接続されているポートに変更（例: '/dev/ttyACM0'）

sensor_data = []  # センサデータのリスト
interval = 10  # データ送信の間隔（秒）

# センサデータの範囲（例として、センサの出力が0～1023の範囲と仮定）
sensor_min = 0
sensor_max = 1024


def map_to_range(value, in_min, in_max, out_min, out_max):
    """値を指定した範囲に線形変換する関数"""
    return float((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


async def send_data(mapped_value):
    # 10秒毎にgrab_strengthを送信
    data = {"grab_strength": mapped_value}
 
    """非同期でデータを送信する関数"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/sensor_data", json=data
            )
            print(f"Sent mapped data: {mapped_value}, Response: {response.status_code}")
        except httpx.RequestError as e:
            print(f"An error occurred while requesting: {e}")


async def read_sensor_data():
    """センサデータを読み取り、5秒ごとに送信する非同期関数"""
    global sensor_data
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
                # 0～1の範囲に変換
                mapped_value = map_to_range(
                    average_value, sensor_min, sensor_max, 0, 1
                )
                # 非同期でデータを送信
                await send_data(mapped_value)
                # センサデータのリストをリセット
                sensor_data = []
            start_time = current_time
        # 少し待ってから次のループへ
        await asyncio.sleep(0.1)


async def main():
    """メイン関数"""
    try:
        await read_sensor_data()
    except KeyboardInterrupt:
        print("終了します。")
    finally:
        ser.close()  # シリアルポートを閉じる


# 非同期イベントループを開始
asyncio.run(main())
