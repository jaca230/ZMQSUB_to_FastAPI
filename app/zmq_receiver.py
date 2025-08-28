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
        self.merge_count = 0

    def _merge_waveform_integrals(self, msg):
        if isinstance(msg, list):
            if len(msg) == 1 and isinstance(msg[0], str):
                try:
                    parsed_msg = json.loads(msg[0])
                    if isinstance(parsed_msg, dict):
                        return self._merge_waveform_integrals(parsed_msg)
                except json.JSONDecodeError:
                    pass
            
            processed_list = []
            for item in msg:
                if isinstance(item, dict):
                    processed_list.append(self._merge_waveform_integrals(item))
                elif isinstance(item, str):
                    try:
                        parsed_item = json.loads(item)
                        if isinstance(parsed_item, dict):
                            processed_list.append(self._merge_waveform_integrals(parsed_item))
                        else:
                            processed_list.append(parsed_item)
                    except json.JSONDecodeError:
                        processed_list.append(item)
                else:
                    processed_list.append(item)
            return processed_list

        if not isinstance(msg, dict):
            return msg

        data_products = msg.get("data_products", {})
        waveform_collection = (
            data_products.get("WFD5WaveformCollection")
            if data_products
            else msg.get("WFD5WaveformCollection")
        )
        integral_collection = (
            data_products.get("WFD5TraceIntegralCollection")
            if data_products
            else msg.get("WFD5TraceIntegralCollection")
        )
        
        if not waveform_collection or not integral_collection:
            return msg
        
        waveforms = waveform_collection.get("arr", []) if isinstance(waveform_collection, dict) else []
        integrals = integral_collection.get("arr", []) if isinstance(integral_collection, dict) else []
        
        if not waveforms or not integrals:
            return msg

        integral_map = {}
        for wi in integrals:
            if isinstance(wi, dict):
                key = (wi.get("crateNum"), wi.get("amcNum"), wi.get("channelTag"))
                integral_map[key] = wi

        for wf in waveforms:
            if isinstance(wf, dict):
                key = (wf.get("crateNum"), wf.get("amcNum"), wf.get("channelTag"))
                wi = integral_map.get(key)
                if wi:
                    wf.update({
                        "fullintegral": wi.get("fullintegral"),
                        "integral": wi.get("integral"),
                        "amplitude": wi.get("amplitude"),
                        "pedestalLevel": wi.get("pedestalLevel"),
                        "pedestalStdev": wi.get("pedestalStdev"),
                        "peak_time": wi.get("peak_time"),
                        "threshold": wi.get("threshold"),
                        "integration_window": wi.get("integration_window"),
                        "is_energy_calibrated": wi.get("is_energy_calibrated", False),
                        "clipped_integration_window": wi.get("clipped_integration_window", False),
                        "calibration_factor": wi.get("calibration_factor"),
                        "nsigma": wi.get("nsigma"),
                        "search_method": wi.get("search_method"),
                    })

        if data_products and "WFD5TraceIntegralCollection" in data_products:
            data_products.pop("WFD5TraceIntegralCollection")
        elif "WFD5TraceIntegralCollection" in msg:
            msg.pop("WFD5TraceIntegralCollection")

        self.merge_count += 1
        return msg

    def _receive_loop(self):
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        
        while self.running:
            socks = dict(poller.poll(1000))
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

                    if self.topic == "DATA":
                        msg = self._merge_waveform_integrals(msg)

                    self.buffer.append(msg)
                    
                except Exception:
                    pass

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def get_buffer(self):
        return list(self.buffer)

    def get_merge_stats(self):
        return {
            "total_merges": self.merge_count,
            "buffer_size": len(self.buffer)
        }


# Export two global instances
zmq_receiver_data = ZMQReceiver(zmq_url="tcp://127.0.0.1:5555", topic="DATA", maxlen=50)
zmq_receiver_odb = ZMQReceiver(zmq_url="tcp://127.0.0.1:5556", topic="ODB", maxlen=10)
