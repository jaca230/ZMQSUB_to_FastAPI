import zmq
import threading
import json
from collections import deque

class ZMQReceiver:
    def __init__(self, zmq_url="tcp://127.0.0.1:5555", topic="DATA", maxlen=50):
        self.zmq_url = zmq_url
        self.topic = topic
        self.buffer = deque(maxlen=maxlen)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(self.zmq_url)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        self.running = False
        self.thread = threading.Thread(target=self._receive_loop, daemon=True)

    def _receive_loop(self):
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        while self.running:
            socks = dict(poller.poll(1000))  # timeout in milliseconds
            if self.socket in socks and socks[self.socket] == zmq.POLLIN:
                try:
                    frames = self.socket.recv_multipart()
                    topic = frames[0].decode("utf-8")
                    if topic != self.topic:
                        continue
                    payload_str = frames[1].decode("utf-8")
                    try:
                        msg = json.loads(payload_str)
                    except json.JSONDecodeError:
                        msg = {"raw": payload_str}
                    self.buffer.append(msg)
                except Exception as e:
                    print(f"ZMQ receive error: {e}")

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def get_buffer(self):
        return list(self.buffer)

zmq_receiver = ZMQReceiver()
