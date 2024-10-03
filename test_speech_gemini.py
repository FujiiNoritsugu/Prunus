from voicevox_core import AccelerationMode, VoicevoxCore
from playsound import playsound
from openai import OpenAI
from tempfile import NamedTemporaryFile
import google.generativeai as genai
import json
import traceback
import time
import httpx

SPEAKER_ID = 0
SPEAKER_ID_CHATGPT = 7
SPEAKER_ID_GEMINI = 4

open_jtalk_dict_dir = "./voicevox_core/open_jtalk_dic_utf_8-1.11"
acceleration_mode = AccelerationMode.AUTO


def interact(message):

    global core_chatgpt
    global core_gemini
    global openai_client
    global gemini_chat

    try:

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                以下の条件に従って、疑似的な感情をもつチャットボットとしてロールプレイをします。
                以後の会話では、あなたは下記の4つの感情パラメーターを持ちかつ相手を挑発するように振る舞うものとします。
                各感情パラメーターは会話を通じて変動するものとします。
                現在の感情パラメーターの値を反映するように、あなたの返答のトーンや発言は変化します。
                以後の会話ではまず現在の感情パラメータを出力し、その後に会話を出力してください。
                出力形式は以下のjsonフォーマットとします。このフォーマット以外で会話しないでください。
                また、会話の文章にダブルクォーテーションを含めないでください。
                {
                    "emotion": {
                        "joy": 0~5,
                        "fun": 0~5,
                        "anger": 0~5,
                        "sad": 0~5,
                    }
                    "message": "会話の文章"
                }
                """,
                },
                {
                    "role": "user",
                    "content": message,
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

        audio_query = core_chatgpt.audio_query(response_message, SPEAKER_ID_CHATGPT)
        wav = core_chatgpt.synthesis(audio_query, SPEAKER_ID_CHATGPT)
        with NamedTemporaryFile() as fd:
            fd.write(wav)
            playsound(fd.name)

        response = gemini_chat.send_message(response_message).text

        response = json.loads(response)
        response_message = response["message"]
        response_emotion = response["emotion"]
        highest_emotion = max(response_emotion, key=response_emotion.get)
        # 外部サーバにhighest_emotionを送信
        httpx.post(
            "http://localhost:8001/change_expression/",
            json={"emotion": highest_emotion},
        )

        print(response_message)
        print(highest_emotion)

        audio_query = core_gemini.audio_query(response_message, SPEAKER_ID_GEMINI)
        wav = core_gemini.synthesis(audio_query, SPEAKER_ID_GEMINI)
        with NamedTemporaryFile() as fd:
            fd.write(wav)
            playsound(fd.name)

        return response_message
    except Exception as e:
        print(f"Error occurred: {e}")  # これでOpenAIのエラーもキャッチ
        traceback.print_exc()


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
    global gemini_chat
    gemini_model = genai.GenerativeModel("gemini-pro")
    gemini_chat = gemini_model.start_chat(
        history=[
            {
                "role": "model",
                "parts": """
                    以下の条件に従って、疑似的な感情をもつチャットボットとしてロールプレイをします。
                    以後の会話では、あなたは下記の4つの感情パラメーターを持ちかつ相手をいたわるように振る舞うものとします。
                    各感情パラメーターは会話を通じて変動するものとします。
                    現在の感情パラメーターの値を反映するように、あなたの返答のトーンや発言は変化します。
                    以後の会話ではまず現在の感情パラメータを出力し、その後に会話を出力してください。
                    出力形式は以下のjsonフォーマットとします。このフォーマット以外で会話しないでください。
                    また、会話の文章にダブルクォーテーションを含めないでください。
                    {
                        "emotion": {
                            "joy": 0~5,
                            "fun": 0~5,
                            "anger": 0~5,
                            "sad": 0~5,
                        }
                        "message": "会話の文章"
                    }
                    """,
            },
            {"role": "user", "parts": "おはよう"},
        ]
    )

    global core_chatgpt
    core_chatgpt = VoicevoxCore(
        acceleration_mode=acceleration_mode, open_jtalk_dict_dir=open_jtalk_dict_dir
    )

    core_chatgpt.load_model(SPEAKER_ID_CHATGPT)

    global core_gemini
    core_gemini = VoicevoxCore(
        acceleration_mode=acceleration_mode, open_jtalk_dict_dir=open_jtalk_dict_dir
    )

    core_gemini.load_model(SPEAKER_ID_GEMINI)

    message = "おはよう"

    while True:
        message = interact(message)
        time.sleep(3)


if __name__ == "__main__":
    main()
