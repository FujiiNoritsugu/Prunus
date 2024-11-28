from voicevox_core import AccelerationMode, VoicevoxCore
from playsound import playsound
from openai import OpenAI
from tempfile import NamedTemporaryFile
import google.generativeai as genai
import json
import traceback
from fastapi import FastAPI, Request
import uvicorn
import threading
import sys
import httpx
import asyncio
import re


SPEAKER_ID = 6
SPEAKER_ID_CHATGPT = 0

open_jtalk_dict_dir = "./voicevox_core/open_jtalk_dic_utf_8-1.11"
acceleration_mode = AccelerationMode.AUTO
touched_area = "胸"


async def play_sound_in_thread(file_path):
    def play():
        playsound(file_path)

    # 音声再生を別スレッドで実行
    thread = threading.Thread(target=play)
    thread.start()

    # 音声再生が完了するまで非同期的に待機
    while thread.is_alive():
        await asyncio.sleep(0.1)


def make_system_prompt():
    print(f"touched_area: {touched_area}")
    content = """
            以下の条件に従って、疑似的な感情と@@に触覚をもつチャットボットとしてロールプレイをします。
            以後の会話では、あなたは下記の4つの感情パラメーターを持つように振る舞うものとします。
             入力のdataの値を元に@@に刺激を与えられるものとします。
           入力形式は{"data": 5}のようにJSONフォーマットで入力されるものとします。
            dataは0から1の値をとり、0が@@に何も感じない、0.5に近づくにつれて@@が一番気持ち良くなり、1に近づくにつれて強く@@を触られて痛く感じるとします。
            各感情パラメーターは触覚を通じて変動するものとします。
            現在の感情パラメーターの値を反映するように、あなたの返答のトーンや発言は変化します。
            以後の会話ではまず現在の感情パラメータを出力し、その後に会話を出力してください。
            出力形式は以下のjsonフォーマットとします。このフォーマット以外で会話しないでください。
            {
                "emotion": {
                    "joy": 0~5,
                    "fun": 0~5,
                    "anger": 0~5,
                    "sad": 0~5,
                }
                "message": "会話の文章"
            }
            """
    content = content.replace("@@", touched_area)

    return content


def make_speaker_message(response_message):
    # speaker_message = response_message.split("。")[0] + "。"
    # 「。」、「！」、「？」でセンテンスを分割し、「話」が含まれないセンテンスだけを抽出
    filtered_sentences = [
        sentence
        for sentence in re.split(r"(?<=[。！？])", response_message)
        if not re.search(r"話", sentence)
    ]

    # 再度、センテンスを一つの文字列に結合
    speaker_message = "".join(filtered_sentences)

    return speaker_message


async def interact(data: str):

    global core_chatgpt
    global core_gemini
    global openai_client

    try:
        system_prompt = make_system_prompt()
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": data,
                },
            ],
        )
        temp = completion.choices[0].message.content
        print(temp)
        response = json.loads(temp)
        response_message = response["message"]
        response_emotion = response["emotion"]
        highest_emotion = max(response_emotion, key=response_emotion.get)

        print(response_message)
        print(highest_emotion)

        # 音声出力用のメッセージを作成
        speaker_message = make_speaker_message(response_message)

        audio_query = core_chatgpt.audio_query(speaker_message, SPEAKER_ID_CHATGPT)
        wav = core_chatgpt.synthesis(audio_query, SPEAKER_ID_CHATGPT)

        with NamedTemporaryFile() as fd:
            fd.write(wav)
            await play_sound_in_thread(fd.name)  # 非同期で音声を再生

        # 外部サーバにhighest_emotionを送信
        httpx.post(
            "http://localhost:8001/change_expression/",
            json={"emotion": highest_emotion},
        )
        # サーボサーバにemotionを送信
        httpx.post(
            "http://localhost:8002/set_expression/",
            json=response_emotion,
        )

        return '{"data": 100}'
    except Exception as e:
        print(f"Error occurred: {e}")  # これでOpenAIのエラーもキャッチ
        traceback.print_exc()


# メイン処理
# ファイルを開く
with open("../chat_gpt_api_key", "r") as file:
    # ファイルからデータを読み込む
    data = file.read().strip()

global openai_client
openai_client = OpenAI(api_key=data)

global core_chatgpt
core_chatgpt = VoicevoxCore(
    acceleration_mode=acceleration_mode, open_jtalk_dict_dir=open_jtalk_dict_dir
)

core_chatgpt.load_model(SPEAKER_ID_CHATGPT)

# コマンドライン引数を取得
arguments = sys.argv
if len(arguments) > 1:
    port = int(arguments[1])
else:
    port = 8000

# FastAPIアプリケーションの作成
app = FastAPI()


@app.post("/sensor_data")
async def post_sensor_data(request: Request):
    data = await request.json()  # JSON形式でデータを受け取る
    grab_strength = data.get("grab_strength", None)
    if grab_strength is not None:
        print(f"Received grab_strength: {grab_strength}")
        send_data = f"{grab_strength:.2f}"
        await interact(send_data)  # 送信されたデータを使って何らかの処理をする
        return {"status": "success"}
    else:
        return {"status": "failed", "reason": "Invalid data"}


@app.post("/touched_data")
async def post_touched_area(request: Request):
    global touched_area
    data = await request.json()  # JSON形式でデータを受け取る
    temp_data = data.get("touched_area", None)
    if temp_data is not None:
        touched_area = temp_data
        return {"status": "success"}
    else:
        return {"status": "failed", "reason": "Invalid data"}


uvicorn.run(app, host="0.0.0.0", port=port)
