from queue import Queue
 
 
class MessageBase:
    def __init__(self):
        self.data = dict()
 
    def add(self, device, data):
        if device in self.data:
            self.data[device].put(data)
        else:
            self.data[device] = Queue()
            self.data[device].put(data)
 
    def get(self, device):
        data_queue: Queue = self.data.get(device)
        if not data_queue or data_queue.empty():
            return None
        data = data_queue.get()
        return data
 
 
if __name__ == '__main__':
    mb = MessageBase()
    mb.add("a", "asdasd")
    mb.add("a", "11111111")
    print(mb.data)
    data = mb.get("a")
    print(data)