import leap
import asyncio
import httpx

counter = 0


class MyListener(leap.Listener):
    def __init__(self):
        self.client = httpx.AsyncClient()

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
        global counter
        print(f"Frame {event.tracking_frame_id} with {len(event.hands)} hands.")
        for hand in event.hands:
            grab_strength = hand.grab_strength

            # 10秒毎にgrab_strengthを送信
            data = {"grab_strength": grab_strength}
            counter += 1
            if counter > 1000:
                asyncio.create_task(self.send_data(data))
                counter = 0

    async def send_data(self, data):
        try:
            response = await self.client.post(
                "http://localhost:8000/sensor_data", json=data
            )
            print(
                f"Sent grab_strength: {data['grab_strength']} response: {response.status_code}"
            )
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting: {exc}")

    async def close_client(self):
        await self.client.aclose()


async def main():
    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True

    try:
        with connection.open():
            connection.set_tracking_mode(leap.TrackingMode.Desktop)
            while running:
                await asyncio.sleep(1)
    finally:
        await my_listener.close_client()


if __name__ == "__main__":
    asyncio.run(main())
