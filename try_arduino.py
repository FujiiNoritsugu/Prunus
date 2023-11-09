import os
import openai

import re
import subprocess

def extract_code(text):
    # プログラムコードの正規表現パターン
    code_pattern = r"```[^\n]*\n([\s\S]*?)\n```"

    # 正規表現パターンにマッチする全ての部分を抽出
    code_matches = re.findall(code_pattern, text)

    # 抽出されたコードをリストで返す
    return code_matches


def remove_2_byte_characters(input_text):
    # 正規表現パターンでASCII範囲外の文字を検出
    pattern = re.compile("[^\x00-\x7F]+")

    # パターンに一致する文字列を空白文字列に置換
    cleaned_text = pattern.sub("", input_text)

    return cleaned_text


def main():
    # ファイルを開く
    # with open(os.getenv("OPENAI_API_KEY"), "r") as file:
    with open("../chat_gpt_api_key", "r") as file:
        # ファイルからデータを読み込む
        data = file.read()

    # 読み込んだデータを変数に設定
    openai.api_key = data

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "あなたはArduinoのプログラムを生成するAIです。",
            },
            {
                "role": "user",
                "content": "Arduino UNO でLEDを1秒毎に点灯させるプログラムを生成してください。",
            },
        ],
    )

    # コードをスケッチに書き込む
    with open('./test_sketch/test_sketch.ino', 'w') as f:
        f.writelines(extract_code(completion.choices[0].message.content))

    # アップロードシェルを実行する
    subprocess.run('./upload.sh', shell=True)

if __name__ == "__main__":
    main()
