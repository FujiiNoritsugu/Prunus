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
import httpx
import traceback

SAMPLERATE = 44100
SPEAKER_ID = 0

open_jtalk_dict_dir = "./voicevox_core/open_jtalk_dic_utf_8-1.11"
acceleration_mode = AccelerationMode.AUTO


def get_input_device_index():
    # pyaudioで利用可能なデバイスをリストアップ
    audio = pyaudio.PyAudio()
    return audio.get_device_count() - 1


# ChatGPTの回答をAlexaへの質問に変換する関数
def convert_to_alexa_question(chatgpt_response):
    pattern = r"(?<=[。？！、])"
    sentences = re.split(pattern, chatgpt_response)
    # シンプルな変換ロジックの例
    alexa_question = "アレクサ, " + sentences[0]

    return alexa_question


# ChatGPTの回答を受け取り、Alexaの質問を生成する
def generate_alexa_question(chatgpt_response):
    global gemini_model
    gemini_respose = gemini_model.generate_content(
        f"かっこの言葉をアレクサへの質問に変えて。「{chatgpt_response}」"
    )
    return gemini_respose.text


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
                以後の会話ではまず現在の感情パラメータを出力し、その後に会話を出力してください。
                出力形式は以下のjsonフォーマットとします。このフォーマット以外で会話しないでください。
                {
                    emotion: {
                        joy: 0~5,
                        fun: 0~5,
                        anger: 0~5,
                        sad: 0~5,
                    }
                    message: "会話の文章"
                }
                """,
                },
                {
                    "role": "user",
                    "content": sprec_text,
                },
            ],
        )

        response = json.loads(completion.choices[0].message.content)
        response_message = response["message"]
        response_emotion = response["emotion"]
        highest_emotion = max(response_emotion, key=response_emotion.get)
        # 外部サーバにhighest_emotionを送信
        httpx.post(
            "http://localhost:8000/change_expression/",
            json={"emotion": highest_emotion},
        )

        print(response_message)
        print(highest_emotion)
        response_message = generate_alexa_question(response_message)
        print(response_message)
        audio_query = core.audio_query(response_message, SPEAKER_ID)
        wav = core.synthesis(audio_query, SPEAKER_ID)
        with NamedTemporaryFile() as fd:
            fd.write(wav)
            playsound(fd.name)

    except speech_recognition.UnknownValueError:
        pass
    except speech_recognition.RequestError as e:
        pass
    except Exception as e:
        print(f"Error occurred: {e}")  # これでOpenAIのエラーもキャッチ
        traceback.print_exc()
    finally:
        return (None, pyaudio.paContinue)


def main():
    # ファイルを開く
    with open("../chat_gpt_api_key", "r") as file:
        # ファイルからデータを読み込む
        data = file.read().strip()

    global openai_client
    openai_client = OpenAI(api_key=data)

    with open("../gemini_api_key", "r") as file:
        # ファイルからデータを読み込む
        api_key = file.read().strip()

    genai.configure(api_key=api_key)
    global gemini_model
    gemini_model = genai.GenerativeModel("gemini-pro")

    global core
    core = VoicevoxCore(
        acceleration_mode=acceleration_mode, open_jtalk_dict_dir=open_jtalk_dict_dir
    )

    core.load_model(SPEAKER_ID)

    global sprec
    sprec = speech_recognition.Recognizer()  # インスタンスを生成
    # Audio インスタンス取得
    audio = pyaudio.PyAudio()

    global input_device_index
    input_device_index = get_input_device_index()
    if input_device_index is None:
        print("利用可能なマイク入力デバイスがありません。")
        return

    stream = audio.open(
        format=pyaudio.paInt16,
        rate=SAMPLERATE,
        channels=1,
        input_device_index=input_device_index,
        input=True,
        frames_per_buffer=SAMPLERATE * 5,  # 5秒周期でコールバック
        stream_callback=callback,
    )
    stream.start_stream()
    while stream.is_active():
        time.sleep(0.1)

    stream.stop_stream()
    stream.close()
    audio.terminate()


if __name__ == "__main__":
    main()
