import os
import openai

import re


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
    with open(os.getenv("OPENAI_API_KEY"), "r") as file:
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
                "content": "Arduino UNOでLEDを点灯させるプログラムを生成してください。",
            },
        ],
    )

    # print(completion.choices[0].message)
    print(extract_code(completion.choices[0].message.content))


if __name__ == "__main__":
    main()
