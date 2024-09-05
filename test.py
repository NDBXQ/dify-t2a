import socketio

# 创建 SocketIO 客户端实例
sio = socketio.Client()

# 连接到服务器
@sio.event
def connect():
    print('连接成功')

# 接收服务器发送的消息
@sio.on('response')
def receive_message(data):
    # 将二进制字符串转文本
    data = data.decode('utf-8')
    # print('收到消息:', type(data))
    print('收到消息:', data)

# 发送消息给服务器
def send_message(message):
    sio.emit('message', message)
    print('发送消息:', message)

if __name__ == '__main__':
    # 服务器地址和端口
    server_address = 'http://localhost:8765'
    # server_address = 'http://14.29.175.216:8766'
    
    # 连接到服务器
    sio.connect(server_address)
    content = {
                "userid":"xiaoxiaohong2",
                "qurey":'你好呀',
                "conversation_id":"",
                "role":"zh-CN-YunjianNeural",
                "device":"12345678",
                "device_name":"xiaoxiaohong",
            }
    send_message(content)
    # 持续接收消息
    while True:
        # 等待消息事件触发
        sio.wait()

    # 断开连接
    sio.disconnect()