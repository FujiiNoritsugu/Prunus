import leap
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()
latest_grab_strength = {"grab_strength": None}  # 最新のgrab_strengthを保存する辞書


class MyListener(leap.Listener):
    def on_connection_event(self, event):
        print("Connected")

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")

    def on_tracking_event(self, event):
        global latest_grab_strength
        for hand in event.hands:
            grab_strength = hand.grab_strength
            latest_grab_strength["grab_strength"] = grab_strength
            print(f"Updated grab_strength: {grab_strength}")


async def start_leap_motion():
    my_listener = MyListener()
    connection = leap.Connection()
    connection.add_listener(my_listener)

    try:
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            while True:
                await asyncio.sleep(1)
    finally:
        print("Leap Motion connection closed")


@app.get("/get_grab_strength")
async def get_grab_strength():
    """最新のgrab_strengthを返すエンドポイント"""
    if latest_grab_strength["grab_strength"] is not None:
        return JSONResponse(content=latest_grab_strength)
    else:
        return JSONResponse(content={"error": "No data available"}, status_code=404)


async def main():
    # 並行タスクでLeap Motionのリスナーを開始
    leap_task = asyncio.create_task(start_leap_motion())

    # FastAPIのサーバーを起動
    uvicorn_task = asyncio.create_task(
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    )

    await asyncio.gather(leap_task, uvicorn_task)


if __name__ == "__main__":
    asyncio.run(main())
