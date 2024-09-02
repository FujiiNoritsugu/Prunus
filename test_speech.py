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

SAMPLERATE = 44100
SPEAKER_ID = 0

open_jtalk_dict_dir = './voicevox_core/open_jtalk_dic_utf_8-1.11'
acceleration_mode = AccelerationMode.AUTO

def callback(in_data, frame_count, time_info, status):
    global sprec
    global core
    global openai_client
    try:
        audiodata = speech_recognition.AudioData(in_data,SAMPLERATE,2)
        sprec_text = sprec.recognize_google(audiodata, language='ja-JP')
        print(sprec_text)

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content":"あなたはずんだもんです。",
                },
                {
                    "role": "user",
                    "content": sprec_text,
                },
            ],
        )

        response = completion.choices[0].message.content
        response = "アレクサ、" + response
        print(response)
        audio_query = core.audio_query(response, SPEAKER_ID)
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
    finally:
        return (None, pyaudio.paContinue)
    
def main():
    # ファイルを開く
    with open("../chat_gpt_api_key", "r") as file:
        # ファイルからデータを読み込む
        data = file.read()

    global openai_client
    openai_client = OpenAI(api_key=data)

    global core
    core = VoicevoxCore(
        acceleration_mode=acceleration_mode, open_jtalk_dict_dir=open_jtalk_dict_dir
    )
    core.load_model(SPEAKER_ID)

    global sprec 
    sprec = speech_recognition.Recognizer()  # インスタンスを生成
    # Audio インスタンス取得
    audio = pyaudio.PyAudio() 
    stream = audio.open( format = pyaudio.paInt16,
                        rate = SAMPLERATE,
                        channels = 1, 
                        input_device_index = 21,
                        input = True, 
                        frames_per_buffer = SAMPLERATE*5, # 5秒周期でコールバック
                        stream_callback=callback)
    stream.start_stream()
    while stream.is_active():
        time.sleep(0.1)
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
if __name__ == '__main__':
    main()
