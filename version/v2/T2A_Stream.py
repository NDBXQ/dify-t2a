# -*- coding: utf-8 -*-
# This Python file uses the following encoding: utf-8
from typing import Iterator
import time
import requests
import json
import requests
import json


class T2A_Stream:

    def __init__(self):
        self.group_id = '1694704972592141'
        self.api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLph43luobnj4_nm5vmlZnogrLnp5HmioDmnInpmZDlhazlj7giLCJVc2VyTmFtZSI6Iue9l-asoyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxNjk0NzA0OTcyMzUxNDUxIiwiUGhvbmUiOiIxOTkyMzU5MDYzNSIsIkdyb3VwSUQiOiIxNjk0NzA0OTcyNTkyMTQxIiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoianNoaW5ldGVjaEAxNjMuY29tIiwiQ3JlYXRlVGltZSI6IjIwMjQtMDYtMTEgMTM6NDk6NDkiLCJpc3MiOiJtaW5pbWF4In0.iYlLrkOnRehE5NYRFB1VeT4Qkgd6ZF5E4tOh-eco2qBozP2zqZJ2YCCwMO0EO5FGF7YU6EBnvCMpJNh2omDos3cNNY9cq-4rL1nLZuw7zXNuCkcXQ1qCya8CZreZfHmRyTLykS4XdN1q555uqDZHxJwrCDAUkaZwUIMkOKGh82WaC7nSx0SJox9e_USN_86SDNB-PyJm-vvU3NjHc-G-meAZoC-q_L3MGpVwjCYyqaYUAsB-FzUwMo-emleL83vW7Bk428KOozJzuXofc2UhLV-eFHIPu0WhBNopnEm_HycViSBW5dV4-z3cG3vloPf8GtFHZIVpV5DVVqECqVdBnA"
        self.file_format='mp3'    
        # 支持 mp3/pcm/flac


    def build_tts_stream_headers(self) -> dict:
        headers =   {
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'authorization':  "Bearer "+ self.api_key,
        }
        return headers

    def build_tts_stream_body(self, msg, role) -> dict:
        print("role:",role)

        if role == "zh-CN-XiaoxiaoNeural":
            voice_id = "female-tianmei"
            
        if role == "zh-CN-YunjianNeural":
            voice_id = "presenter_male"
   
        body =  json.dumps({
            "timber_weights": [
            {
                "voice_id": voice_id,
                "weight": 1
            }
   
            ],
            "text": msg,
            "voice_id": "",
            "model": "speech-01",
            "speed": 1.15,
            "vol": 1,
            "pitch": 0,
            "audio_sample_rate": 32000,
            "bitrate": 128000,
            "format": self.file_format,
        })
        return body
    
    def call_tts_stream(self, msg, role) -> Iterator[bytes]:
        url = "https://api.minimax.chat/v1/tts/stream?GroupId="+ self.group_id
        headers = self.build_tts_stream_headers()
        body= self.build_tts_stream_body(msg, role)
        print("start.....")
        response =  requests.request("POST", url, stream=True, headers=headers, data=body)
        print("Trace-Id: "+ response.headers.get("Trace-Id"))
    
        for chunk in (response.raw):

            if chunk:
                if chunk[:5] == b'data:':
                    data = json.loads(chunk[5:])
                    if "data" in data and "extra_info" not in data:
                        if "audio" in data["data"] :
                            audio =data["data"]['audio']
                            print("<==========音频块==========>")
                            yield audio

            
    def tts(self,audio_stream:Iterator[bytes]) -> bytes:
        audio = b""
    
        for chunk in audio_stream:
            if chunk is not None:
                decoded_hex = bytes.fromhex(chunk)
                
                audio += decoded_hex

        return audio 
            



if __name__ == '__main__':
    start = time.time()
    t2a_stream = T2A_Stream()
    file_format = t2a_stream.file_format
    print("开始合成语音...")
    msg = "你好呀，今天心情怎么样呀！"
    role = "zh-CN-YunjianNeural"
    audio_chunk_iterator = t2a_stream.call_tts_stream(msg, role)
    print(time.time()-start)
    audio = t2a_stream.tts(audio_chunk_iterator)
    # print("audio===========>:",audio)

    print(time.time()-start)

    # 结果保存至文件
    timestamp = int(time.time())
    file_name=f'output_{timestamp}.{file_format}'
    with open(file_name, 'wb') as file:
        file.write(audio)


