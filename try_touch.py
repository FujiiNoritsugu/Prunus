import tkinter as tk
from tkinter import messagebox


# 選択した部位を表示する関数
def select_body_part(part):
    messagebox.showinfo("選択した部位", f"あなたが選択した部位: {part}")


# メインウィンドウの作成
root = tk.Tk()
root.title("人型アイコンで部位選択")
root.geometry("300x500")

# Canvasの作成
canvas = tk.Canvas(root, width=300, height=500, bg="white")
canvas.pack()

# 人型の描画（円や線を使ってシンプルな人の形にします）
# 顔
face = canvas.create_oval(120, 50, 180, 110, fill="lightblue", outline="black")
# 胸
chest = canvas.create_rectangle(110, 120, 190, 200, fill="lightgreen", outline="black")
# 左手
left_hand = canvas.create_rectangle(
    60, 130, 110, 180, fill="lightpink", outline="black"
)
# 右手
right_hand = canvas.create_rectangle(
    190, 130, 240, 180, fill="lightpink", outline="black"
)
# 左足
left_leg = canvas.create_rectangle(
    110, 200, 140, 300, fill="lightyellow", outline="black"
)
# 右足
right_leg = canvas.create_rectangle(
    160, 200, 190, 300, fill="lightyellow", outline="black"
)

# タッチイベントの設定
canvas.tag_bind(face, "<ButtonPress-1>", lambda event: select_body_part("顔"))
canvas.tag_bind(left_hand, "<ButtonPress-1>", lambda event: select_body_part("手"))
canvas.tag_bind(right_hand, "<ButtonPress-1>", lambda event: select_body_part("手"))
canvas.tag_bind(chest, "<ButtonPress-1>", lambda event: select_body_part("胸"))
canvas.tag_bind(left_leg, "<ButtonPress-1>", lambda event: select_body_part("足"))
canvas.tag_bind(right_leg, "<ButtonPress-1>", lambda event: select_body_part("足"))

# メインループの開始
root.mainloop()
