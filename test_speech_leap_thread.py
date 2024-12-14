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
import sounddevice as sd
import numpy as np
from uvicorn import Config, Server

SPEAKER_ID_CHATGPT = 0
FETCH_INTERVAL = 1  # 1秒ごとにリクエストを送信

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


async def speak_with_voicevox(text, speaker_id=1):
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        # audio_queryエンドポイントにPOSTリクエストを送信
        # TODO ここのlocalhostをngrokのURLに書き換える
        query_response = await client.post(
            "https://localhoost:8080/audio_query",
            params={"text": text, "speaker": speaker_id},
        )
        query_response.raise_for_status()
        audio_query = query_response.json()

        # synthesisエンドポイントにPOSTリクエストを送信
        synthesis_response = await client.post(
            "https://localhost:8080/synthesis",
            json=audio_query,
            params={"speaker": speaker_id},
        )
        synthesis_response.raise_for_status()

    # バイナリデータをnumpy配列に変換
    audio_data = np.frombuffer(synthesis_response.content, dtype=np.int16)

    # サンプルレートはVoiceVoxの標準値である24kHz
    sd.play(audio_data, samplerate=24000)
    sd.wait()


async def post_servo_and_emotion(highest_emotion, response_emotion):
    """サーボサーバーにemotionを送信"""
    async with httpx.AsyncClient() as client:
        try:
            # 外部サーバにhighest_emotionを送信
            await client.post(
                "http://localhost:8001/change_expression/",
                json={"emotion": highest_emotion},
            )
            # サーボサーバにemotionを送信
            await client.post(
                "http://localhost:8002/set_expression/",
                json=response_emotion,
            )

        except httpx.RequestError as e:
            print(f"Error sending emotion: {e}")


async def interact(data: str):

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

        # 音声を出力
        await speak_with_voicevox(speaker_message, speaker_id=SPEAKER_ID_CHATGPT)

        await post_servo_and_emotion(highest_emotion, response_emotion)

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

# コマンドライン引数を取得
arguments = sys.argv
if len(arguments) > 1:
    port = int(arguments[1])
else:
    port = 8000

# FastAPIアプリケーションの作成
app = FastAPI()


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


async def fetch_and_interact():
    """定期的にget_grab_strengthエンドポイントからデータを取得し、処理する"""
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get("http://localhost:8003/get_grab_strength")
                response.raise_for_status()
                data = response.json()
                grab_strength = data.get("grab_strength", None)
                if grab_strength is not None:
                    print(f"Fetched grab_strength: {grab_strength}")
                    await interact(str(grab_strength))  # `interact`でアクションを実行
            except httpx.RequestError as e:
                print(f"Error fetching grab_strength: {e}")
            await asyncio.sleep(FETCH_INTERVAL)

async def start_server():
    """FastAPIサーバーを起動"""
    config = Config(app, host="0.0.0.0", port=8004, log_level="info")
    server = Server(config)
    await server.serve()


async def main():
    """メイン処理"""
    # `fetch_and_interact`を別タスクとして起動
    fetch_task = asyncio.create_task(fetch_and_interact())

    # FastAPIサーバーの起動
    server_task = asyncio.create_task(start_server())

    await asyncio.gather(fetch_task, server_task)


if __name__ == "__main__":
    asyncio.run(main())
