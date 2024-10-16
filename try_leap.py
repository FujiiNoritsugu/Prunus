import leap
import time


def detect_kneading(hand):
    # 手の位置や動きを記録する（シンプルな例）
    # ここでは、一定時間内に手が開閉を繰り返すかを見ます
    kneading = False
    if hand.grab_strength > 0.9:
        # 手が握られているとき
        print(f"Hand {hand.id} is grabbing.")
        time.sleep(0.5)  # ちょっと待って開閉を確認する
        if hand.grab_strength < 0.1:
            print(f"Hand {hand.id} has opened.")
            kneading = True
    return kneading


def process_frame(frame):
    for hand in frame.hands:
        if detect_kneading(hand):
            print(f"Hand {hand.id} is kneading.")


def main():
    connection = leap.Connection()

    with connection.open() as open_connection:
        while True:
            frame = connection.frame()
            if frame:
                process_frame(frame)


if __name__ == "__main__":
    main()
