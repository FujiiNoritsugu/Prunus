"""Prints the palm position of each hand, every frame. When a device is 
connected we set the tracking mode to desktop and then generate logs for 
every tracking frame received. The events of creating a connection to the 
server and a device being plugged in also generate logs. 
"""

import leap
import time
import httpx
import asyncio


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

    async def on_tracking_event(self, event):
        print(f"Frame {event.tracking_frame_id} with {len(event.hands)} hands.")
        async with httpx.AsyncClient() as client:
            for hand in event.hands:
                grab_strength = hand.grab_strength
                if grab_strength > 0.9:
                    print(f"Hand {hand.id} is grabbing.")
                elif grab_strength < 0.1:
                    print(f"Hand {hand.id} has opened.")

                # 10秒毎にgrab_strengthを送信
                data = {"grab_strength": grab_strength}
                try:
                    response = await client.post(
                        "http://localhost:8000/sensor_data", json=data
                    )
                    print(
                        f"Sent grab_strength: {grab_strength}, response status: {response.status_code}"
                    )
                except httpx.RequestError as exc:
                    print(f"An error occurred while requesting: {exc}")

                # 10秒待機
                await asyncio.sleep(10)


async def main():
    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)
        while running:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
