from codeinterpreterapi import CodeInterpreterSession, settings

with open("../chat_gpt_api/chat_gpt_api_key", "r") as file:
    # ファイルからデータを読み込む
    settings.OPENAI_API_KEY = file.read()

# create a session and close it automatically
with CodeInterpreterSession() as session:
    # generate a response based on user input
    response = session.generate_response("Plot the bitcoin chart of year 2023")
    # output the response
    response.show()
