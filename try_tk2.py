import tkinter as tk

# ウィンドウの作成
root = tk.Tk()
root.title("喜怒哀楽を描画")

# Canvasの作成
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()


# 顔の輪郭を描く関数
def draw_face():
    canvas.create_oval(50, 50, 350, 350, fill="yellow", outline="black", width=2)


# 喜の表情を描く関数
def draw_happy():
    canvas.delete("all")
    draw_face()
    # 目
    canvas.create_oval(120, 120, 180, 180, fill="black")
    canvas.create_oval(220, 120, 280, 180, fill="black")
    # 口（弧）
    canvas.create_arc(120, 200, 280, 300, start=0, extent=-180, style=tk.ARC, width=2)


# 怒の表情を描く関数
def draw_angry():
    canvas.delete("all")
    draw_face()
    # 目（怒りの眉を追加）
    canvas.create_line(120, 140, 180, 120, width=5)  # 左目の眉
    canvas.create_line(220, 120, 280, 140, width=5)  # 右目の眉
    canvas.create_oval(120, 120, 180, 180, fill="black")
    canvas.create_oval(220, 120, 280, 180, fill="black")
    # 口（逆さの弧）
    canvas.create_arc(120, 200, 280, 300, start=0, extent=180, style=tk.ARC, width=2)


# 哀の表情を描く関数
def draw_sad():
    canvas.delete("all")
    draw_face()
    # 目
    canvas.create_oval(120, 120, 180, 180, fill="black")
    canvas.create_oval(220, 120, 280, 180, fill="black")
    # 口（下向きの弧）
    canvas.create_arc(120, 250, 280, 350, start=0, extent=180, style=tk.ARC, width=2)


# 楽の表情を描く関数
def draw_surprised():
    canvas.delete("all")
    draw_face()
    # 目（大きく）
    canvas.create_oval(110, 110, 190, 190, fill="black")
    canvas.create_oval(210, 110, 290, 190, fill="black")
    # 口（丸い口）
    canvas.create_oval(170, 230, 230, 290, outline="black", width=2)


# ボタンを配置して表情を変更できるようにする
btn_happy = tk.Button(root, text="喜", command=draw_happy)
btn_happy.pack(side=tk.LEFT, padx=10)

btn_angry = tk.Button(root, text="怒", command=draw_angry)
btn_angry.pack(side=tk.LEFT, padx=10)

btn_sad = tk.Button(root, text="哀", command=draw_sad)
btn_sad.pack(side=tk.LEFT, padx=10)

btn_surprised = tk.Button(root, text="楽", command=draw_surprised)
btn_surprised.pack(side=tk.LEFT, padx=10)

# 初期の顔（喜）
draw_happy()

# ウィンドウを表示
root.mainloop()
