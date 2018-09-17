import pyaudio
import wave
import requests
import json
import ConfigParser


def record_voice():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16 # int16型
    CHANNELS = 1             # ステレオ:2
    RATE = 16000             # 16kHz
    RECORD_SECONDS = 3       # 3秒録音
    WAVE_OUTPUT_FILENAME = "output2.wav"
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    print("* recording")
    
    frames = []
    
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")
        
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def get_text_from_voice():
    config = ConfigParser.ConfigParser()

    APIKEY = config.get('API', 'APIKEY')
    
    url = "https://api.apigw.smt.docomo.ne.jp/amiVoice/v1/recognize?APIKEY={}".format(APIKEY)
    files = {"a": open("./output2.wav", 'rb'), "v":"on"}
    r = requests.post(url, files=files)
    print(r.json()['text'])
    print(r)

record_voice()
get_text_from_voice()
