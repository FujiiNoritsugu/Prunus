import os
from openai import OpenAI

# ファイルを開く
with open("../chat_gpt_api/chat_gpt_api_key", "r") as file:
    # ファイルからデータを読み込む
    data = file.read()

# 読み込んだデータを変数に設定
openai = OpenAI(api_key=data)

# 会話を続けるループ
while True:
    # ユーザから標準入力を受け取る
    user_input = input("あなた: ")

    # "STOP"と入力されたらループを終了する
    if user_input.strip().upper() == "STOP":
        print("会話を終了します。")
        break

    # OpenAI APIにリクエストを送る
    completion = openai.chat.completions.create(
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
                "content": user_input,
            },
        ],
    )

    # APIの応答を取得して出力する
    response = completion.choices[0].message.content
    print(f"チャットボット: {response}")
