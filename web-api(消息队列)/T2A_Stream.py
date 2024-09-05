# This Python file uses the following encoding: utf-8
import shutil
import subprocess
from typing import Iterator
import time

import requests
import json

import requests
import json
import base64


class T2A_Stream:

    def __init__(self):
        self.group_id = '1793261014549008867'
        self.api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLph43luobnj4_nm5vmmbrog73np5HmioDmnInpmZDlhazlj7giLCJVc2VyTmFtZSI6Iue9l-asoyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxNzkzMjYxMDE0NTU3Mzk3NDc1IiwiUGhvbmUiOiIxODk4MzI2ODU1OSIsIkdyb3VwSUQiOiIxNzkzMjYxMDE0NTQ5MDA4ODY3IiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjQtMDYtMDYgMTA6NTk6NTUiLCJpc3MiOiJtaW5pbWF4In0.ZhhmaRGZrx-NMgG2vr95C0T6iFykWahAykeiMzhHOsBb1Gj9lGoWEsMCI9KdLoneyc6xHsYvWGoPkJjvfJ6hF4U4u_cgvCrZXH_--D8QXzO6bXVo9McDyLXhw38Twl1WduQOQRLdLV6_Kxvnu16m9TcOwCEAUUZHLClufKPUg1Tu5lz9sNzkWCc_LOGLxbDtI7TkfW4cZVJb3bTNG5Wv3rlVh8QKX9WGw5LUMYS74Yd9S_Dl1ZpnEcQo7IoXKzXQ81eNubXKWljJJcMvhUCutwe9oiqpXF2zhty5-uOn5WWDMAYnslaQ_-IJpn2Xl83q6OlHGIr1d2XEZxrl47uBmw"
        # self.api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJOREJYLiIsIlVzZXJOYW1lIjoiTkRCWC4iLCJBY2NvdW50IjoiIiwiU3ViamVjdElEIjoiMTc4MjU4ODUwOTcwNjUyMzIxNyIsIlBob25lIjoiMTc2MjM4Nzk3OTkiLCJHcm91cElEIjoiMTc4MjU4ODUwOTY5ODEzNDYwOSIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6IiIsIkNyZWF0ZVRpbWUiOiIyMDI0LTA2LTA1IDE0OjQ4OjI5IiwiaXNzIjoibWluaW1heCJ9.K1mbIXa_bwFubUpXSPCALDOQR6IZTyH-rFHaB2ZpbWf785DifPn6i30ZJoZDmjbKqWaySdEQSM1QW9Jwaa08O8LAKoUZs-FE0b4UluHZr5uKEfFSWUHgCSQ5iXYjsrABZrHn-St5H5h5M_EOWo0wQ5jGbcrsl4oOeOHhk8LbyRMfK6f_tpGRbru-gUCimTEM0xVqk-YWDhCDEKBiD2RwJ-GYjsJVzD1tfLN0F89Lt3U0NQlMidULl2OieCtbcYwQ1C8DKbBO1E1ycg3Mb8CcIWeTz6Wi1hh6QSfD8dhRuNr0XGOmXGVckRc82TmjqCbRLRUy0YjIUfs6yHU0QNcdiQ"
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
            "speed": 1.25,
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
                # else:
                #     print(str(chunk))
            
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
    msg = "亲,渠道方入驻我们平台有以下优惠政策:首先,入驻首季度完成接单任务,可享受免佣金待遇。其次,前10万名平台入驻者,每人赠送50次免费AI内容创作权益。"
    role = "zh-CN-YunjianNeural"
    audio_chunk_iterator = t2a_stream.call_tts_stream(msg, role)
    print(time.time()-start)
    audio = t2a_stream.tts(audio_chunk_iterator)

    print(time.time()-start)

    # 结果保存至文件
    timestamp = int(time.time())
    file_name=f'output_{timestamp}.{file_format}'
    with open(file_name, 'wb') as file:
        file.write(audio)


