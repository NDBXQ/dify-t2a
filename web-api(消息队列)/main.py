from message_base import MessageBase
from websocket_server import WebServer
from device_function import DeviceThread
 
 
class MainThread:
    def __init__(self, message_base: MessageBase, websocket_server: WebServer, device_list):
        self.message_base = message_base
        self.websocket_server = websocket_server
        self.device_list = device_list
 
    def run_server(self):
        self.websocket_server.run()
        
    # def run(self):
    #     self.run_server()
    #     while True:
    #         for device in self.device_list:
    #             try:
    #                 # 开始根据设备即功能处理消息
    #                 data = self.message_base.get(device)
    #                 if not data:
    #                     continue
    #                 df = DeviceFunc(device, data)
    #                 df.show_data()
    #             except Exception as err:
    #                 pass

    def run(self):
        self.run_server()
        for device in self.device_list:
            t = DeviceThread(device, self.message_base)
            t.start()

 
 
if __name__ == '__main__':
    mb = MessageBase()
    ws = WebServer("0.0.0.0", 8765, mb)
    device_list = ["xiaoxiaohong", "aa", "bb", "cc"]
 
    mt = MainThread(mb, ws, device_list)
    mt.run()