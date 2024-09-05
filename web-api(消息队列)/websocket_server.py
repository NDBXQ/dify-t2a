import asyncio
import json
import threading
import websockets
##
from message_base import MessageBase
 
 
class WebServer:
    def __init__(self, host, port, message_base: MessageBase):
        self.host = host
        self.port = port
        self.clients = []
        self.message_base = message_base
 
    async def echo(self, websocket, path):
        self.clients.append(websocket)
        client_ip, client_port = websocket.remote_address
        print(f"连接到:{client_ip}:{client_port}")
        while True:
            try:
                recv_text = await websocket.recv()
                data = json.loads(recv_text)
                print("data=======>", data)
                device = data.get("device")
                
                if device:
                    self.message_base.add(device, data)
                    print("device=====>", device)
                else:
                    continue
            except websockets.ConnectionClosed:
                print("ConnectionClosed...")  # 链接断开
                self.clients.remove(websocket)
                break
            except websockets.InvalidState:
                print("InvalidState...")  # 无效状态
                self.clients.remove(websocket)
                break
            except Exception as e:
                print(e)
 
    def connect(self):
        print("连接成功！")
        asyncio.set_event_loop(asyncio.new_event_loop())
        start_server = websockets.serve(self.echo, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
 
    def run(self):
        t = threading.Thread(target=self.connect)
        t.start()
        print("已启动！")
 
 
if __name__ == '__main__':
    mb = MessageBase()
    ws = WebServer("0.0.0.0", 8765, mb)
    ws.run()