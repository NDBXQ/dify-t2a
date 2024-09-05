import json
import websocket
import random
import time
 
class WebClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.conn = None
        self.flag = False
 
    def connect(self):
        try:
            url = f"ws://{self.host}:{self.port}"
            self.conn = websocket.create_connection(url)
            self.flag = True
            print("连接成功")
        except Exception as err:
            self.flag = False
            print("连接失败", err)
 
    def close(self):
        self.conn.close()
 
    def recv(self):
        data = self.conn.recv(1024)
        print(data)
 
    def send(self, data):
        self.conn.send(data)
        print("发送成功")
 
 
if __name__ == '__main__':
    host = "localhost"
    port = 8765
    ws = WebClient(host, port)
    if not ws.flag:
        ws.connect()
    devices = ["aa", "bb", "cc"]
    while True:
        device = random.choice(devices)
        s = ""
        for i in range(random.randint(0, 100)):
            s += chr(random.randint(65, 122))
        data = {"device": device, "value": s}
        data = json.dumps(data)
        ws.send(data)
        time.sleep(1)