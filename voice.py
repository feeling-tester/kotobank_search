import pyaudio
import wave
import requests
import json
import configparser
import subprocess

def gererate_voice_data(speak_str, wavefile_path):
    jtalk_path = "~/HTS/open_jtalk/bin/open_jtalk"
    voicemodel_path = "/usr/share/hts-voice/mei/mei_normal.htsvoice"
    dictmodel_path = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
    #print(speak_str)
    commands = "echo "+ str(speak_str).replace("\n", "") + "|"\
               + jtalk_path\
               + " -m "+ voicemodel_path\
               + " -x "+ dictmodel_path\
               + " -ow "+ wavefile_path
    #print(commands)
    
    proc = subprocess.Popen(
        commands,
        shell  = True,
        stdin  = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)  
    stdout_data, stderr_data = proc.communicate() #処理実行を待つ(†1)
    
    #print(stdout_data)  #標準出力の確認
    #print(stderr_data)  #標準エラーの確認

def play_wav(wavefile_path):
    commands = "aplay " + wavefile_path
    #print(commands)
    proc = subprocess.Popen(
        commands,
        shell  = True)  
    stdout_data, stderr_data = proc.communicate() #処理実行を待つ(†1)
    
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
    config = configparser.ConfigParser()
    config.read('config.ini')
    APIKEY = config.get('API', 'APIKEY')
    url = "https://api.apigw.smt.docomo.ne.jp/amiVoice/v1/recognize?APIKEY={}".format(APIKEY)
    files = {"a": open("./output2.wav", 'rb'), "v":"on"}
    r = requests.post(url, files=files)
    print(r.json()['text'])
    print(r)
    return r.json()['text']

# record_voice()
# get_text_from_voice()
#gererate_voice_data("あああ", "tmp.wav")
