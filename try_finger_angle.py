import leap
import time
import math
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
            # 指の曲がり具合を取得し、度数に変換
            finger_angles = {}
            for finger in hand.fingers:
                proximal_bone = finger.bone(leap.Bone.TYPE_PROXIMAL)
                intermediate_bone = finger.bone(leap.Bone.TYPE_INTERMEDIATE)

                # 関節の角度を計算して度数に変換
                angle_radians = proximal_bone.direction.angle_to(
                    intermediate_bone.direction
                )
                angle_degrees = math.degrees(angle_radians)

                # 指のタイプごとに角度を記録
                finger_angles[finger.type.name.lower()] = angle_degrees

            # 10秒ごとに指の曲がり具合をJSON形式で送信
            counter += 1
            if counter > 1000:
                try:
                    response = client.post(
                        "http://localhost:8000/sensor_data", json=finger_angles
                    )
                    print(f"Sent finger angles: {finger_angles} response: {response}")
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
