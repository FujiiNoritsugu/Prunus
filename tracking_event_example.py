"""Prints the palm position of each hand, every frame. When a device is 
connected we set the tracking mode to desktop and then generate logs for 
every tracking frame received. The events of creating a connection to the 
server and a device being plugged in also generate logs. 
"""

import leap
import time
import httpx

client = httpx.Client()
counter = 0

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
        global counter
        print(f"Frame {event.tracking_frame_id} with {len(event.hands)} hands.")
        for hand in event.hands:
            grab_strength = hand.grab_strength

            # 10秒毎にgrab_strengthを送信
            data = {"grab_strength": grab_strength}
            counter += 1
            if counter > 1000:
                try:
                  response  = client.post("http://localhost:8000/sensor_data", json=data)
                  print(f"Sent grab_strength: {grab_strength} response:{response}")
                except httpx.RequestError as exc:
                    print(f"An error occurred while requesting: {exc}")
                counter = 0


def main():
    my_listener = MyListener()

    connection = leap.Connection()
    connection.add_listener(my_listener)

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)
        while running:
            time.sleep(1)


if __name__ == "__main__":
    main()
