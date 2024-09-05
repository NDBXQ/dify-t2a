import threading
 
 
class DeviceThread(threading.Thread):
    def __init__(self, device_name, message_base):
        super().__init__(target=self.process)
        self.device_name = device_name
        self.message_base = message_base
 
    def get_data(self):
        data = self.message_base.get(self.device_name)
        # print("device_name=======>", self.device_name)
        
        # print("base=======>", data)
        print("message_base=======>", self.message_base)
        return data
 
    def process(self):
        while True:
            data = self.get_data()
            if data:
                print(self.device_name, "收到消息:", data.get("value"))