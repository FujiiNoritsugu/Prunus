import google.generativeai as genai

with open("../gemini_api_key", "r") as file:
    # ファイルからデータを読み込む
    api_key = file.read().strip()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(
    history=[
        {
            "role": "model",
            "parts": """
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
        {"role": "user", "parts": "おはよう"},
    ]
)
response = chat.send_message("ばか")
print(response.text)
