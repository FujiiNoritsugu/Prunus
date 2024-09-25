import time
import speech_recognition
import pyaudio
from pathlib import Path
import voicevox_core
from voicevox_core import AccelerationMode, AudioQuery, VoicevoxCore
from playsound import playsound
import os
from openai import OpenAI
import io
from tempfile import NamedTemporaryFile
import re
import google.generativeai as genai
import json
import tkinter as tk  # プログラム2を動かすために追加

SAMPLERATE = 44100
SPEAKER_ID = 0
open_jtalk_dict_dir = "./voicevox_core/open_jtalk_dic_utf_8-1.11"
acceleration_mode = AccelerationMode.AUTO

# プログラム2のウィンドウを作成（表情描画用）
root = tk.Tk()
root.title("喜怒哀楽を描画")
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()


# 顔の描画関数をプログラム2から移植
def draw_face():
    canvas.create_oval(50, 50, 350, 350, fill="yellow", outline="black", width=2)


def draw_happy():
    canvas.delete("all")
    draw_face()
    canvas.create_oval(120, 120, 180, 180, fill="black")
    canvas.create_oval(220, 120, 280, 180, fill="black")
    canvas.create_arc(120, 200, 280, 300, start=0, extent=-180, style=tk.ARC, width=2)


def draw_angry():
    canvas.delete("all")
    draw_face()
    canvas.create_line(120, 140, 180, 120, width=5)
    canvas.create_line(220, 120, 280, 140, width=5)
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


def change_expression(highest_emotion):
    if highest_emotion == "joy":
        draw_happy()
    elif highest_emotion == "anger":
        draw_angry()
    elif highest_emotion == "sad":
        draw_sad()
    elif highest_emotion == "fun":
        draw_surprised()


# ここでプログラム1の中で highest_emotion を取得した後、プログラム2の表情を変更
def callback(in_data, frame_count, time_info, status):
    global sprec
    global core
    global openai_client

    try:
        audiodata = speech_recognition.AudioData(in_data, SAMPLERATE, 2)
        sprec_text = sprec.recognize_google(audiodata, language="ja-JP")
        print(sprec_text)

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    以下の条件に従って、疑似的な感情をもつチャットボットとしてロールプレイをします。 
                    以後の会話では、あなたは下記の4つの感情パラメーターを持つかのように、振る舞うものとします。 
                    各感情パラメーターは会話を通じて変動するものとします。 
                    現在の感情パラメーターの値を反映するように、あなたの返答のトーンや発言は変化します。
                    """,
                },
                {
                    "role": "user",
                    "content": sprec_text,
                },
            ],
        )

        response = json.loads(completion.choices[0].message.content)
        highest_emotion = max(response["emotion"], key=response["emotion"].get)
        print(f"Highest emotion: {highest_emotion}")

        # プログラム2の表情を変更する関数を呼び出す
        change_expression(highest_emotion)

    except speech_recognition.UnknownValueError:
        pass
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        return (None, pyaudio.paContinue)


# プログラム1の残り部分はそのまま
