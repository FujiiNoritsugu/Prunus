import tkinter as tk
from fastapi import FastAPI
import uvicorn
import threading
from pydantic import BaseModel
import sys

# コマンドライン引数を取得
arguments = sys.argv
if len(arguments) != 3:
    print("Usage: python try_emotion_fastapi.py title port_number")
    sys.exit(1)
title = arguments[1]
port = int(arguments[2])

# FastAPIアプリケーションの作成
app = FastAPI()

# Tkinterのウィンドウを作成
root = tk.Tk()
root.title(title)
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()


# 顔の輪郭を描く関数
def draw_face():
    canvas.create_oval(50, 50, 350, 350, fill="yellow", outline="black", width=2)


# 表情を描く関数
def draw_happy():
    canvas.delete("all")
    draw_face()
    canvas.create_oval(120, 120, 180, 180, fill="black")
    canvas.create_oval(220, 120, 280, 180, fill="black")
    canvas.create_arc(120, 200, 280, 300, start=0, extent=-180, style=tk.ARC, width=2)


def draw_angry():
    canvas.delete("all")
    draw_face()
    canvas.create_line(120, 140, 180, 120, width=5)  # 左目の眉
    canvas.create_line(220, 120, 280, 140, width=5)  # 右目の眉
    canvas.create_oval(120, 120, 180, 180, fill="black")
    canvas.create_oval(220, 120, 280, 180, fill="black")
    canvas.create_arc(120, 200, 280, 300, start=0, extent=180, style=tk.ARC, width=2)


def draw_sad():
    canvas.delete("all")
    draw_face()
    canvas.create_oval(120, 120, 180, 180, fill="black")
    canvas.create_oval(220, 120, 280, 180, fill="black")
    canvas.create_arc(120, 250, 280, 350, start=0, extent=180, style=tk.ARC, width=2)


def draw_surprised():
    canvas.delete("all")
    draw_face()
    canvas.create_oval(110, 110, 190, 190, fill="black")
    canvas.create_oval(210, 110, 290, 190, fill="black")
    canvas.create_oval(170, 230, 230, 290, outline="black", width=2)


class EmotionRequest(BaseModel):
    emotion: str


class EmotionRequest(BaseModel):
    emotion: str


# FastAPIエンドポイントを定義
@app.post("/change_expression/")
def change_expression(request: EmotionRequest):
    emotion = request.emotion
    if emotion == "joy":
        root.after(0, draw_happy)
    elif emotion == "anger":
        root.after(0, draw_angry)
    elif emotion == "sad":
        root.after(0, draw_sad)
    elif emotion == "fun":
        root.after(0, draw_surprised)
    return {"status": "success", "expression": emotion}


# FastAPIを別スレッドで実行
def run_api():
    uvicorn.run(app, host="0.0.0.0", port=port)


api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()

draw_happy()
# Tkinterのウィンドウを実行
root.mainloop()
