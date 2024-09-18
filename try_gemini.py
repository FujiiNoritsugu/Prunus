import google.generativeai as genai

with open("../gemini_api_key", "r") as file:
    # ファイルからデータを読み込む
    api_key = file.read()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("かっこの言葉をアレクサへの質問に変えて。「おはようございます。なにかごようでしょうか？」")
print(response.text)
