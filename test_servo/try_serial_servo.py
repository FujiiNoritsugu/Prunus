from fastapi import FastAPI, HTTPException
import serial
import time
import uvicorn
import threading

# FastAPIアプリケーションの作成
app = FastAPI()

# Arduinoのシリアルポートを指定 (環境に応じて適切に変更)
ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
time.sleep(2)  # Arduino接続待機のため少し待つ


# 感情に対応する表情を設定する関数
def set_expression(expression: str):
    valid_expressions = ["happy", "angry", "sad", "neutral"]
    if expression in valid_expressions:
        ser.write(f"{expression}\n".encode())  # 感情データを送信
        time.sleep(0.1)  # 送信後の待機
        response = ser.readline().decode("utf-8").strip()  # Arduinoからの応答を読み取る
        return {"message": response}
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid expression. Use 'happy', 'angry', 'sad', or 'neutral'.",
        )


# 感情に基づくサーボモーターの動きを設定するAPIエンドポイント
@app.post("/set_expression/")
async def set_expression_api(expression: str):
    try:
        return set_expression(expression)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# FastAPIが終了するときにシリアルポートを閉じる
@app.on_event("shutdown")
def shutdown_event():
    ser.close()


# FastAPIを別スレッドで実行
def run_api():
    uvicorn.run(app, host="0.0.0.0", port=port)


api_thread = threading.Thread(target=run_api, daemon=True)
api_thread.start()
