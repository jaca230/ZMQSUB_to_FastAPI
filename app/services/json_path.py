from .service import Service
from app.zmq_receiver import zmq_receiver
from pydantic import BaseModel, Field
from typing import Optional
import json
import jsonpointer

class JsonPathQueryModel(BaseModel):
    last: int = Field(default=1, ge=0, description="Number of latest messages to use (0 means all)")
    json_path: str = Field(default="", description="JSON Pointer path (slash-separated, e.g. /data_products/ChannelIntegralCollection)")

    model_config = {
        "populate_by_name": True,
    }

def get_by_json_pointer(obj, pointer: str):
    if not pointer:
        return obj
    if not pointer.startswith('/'):
        pointer = '/' + pointer
    try:
        return jsonpointer.resolve_pointer(obj, pointer)
    except jsonpointer.JsonPointerException:
        return None

class JsonPathService(Service):
    query_model = JsonPathQueryModel

    def get(self, last: int = 1, json_path: str = ""):
        buf = zmq_receiver.get_buffer()
        if not buf:
            return {"data": None}

        if last == 0:
            target = buf[:]  # all messages
        else:
            target = buf[-last:]  # last N messages

        def parse(obj):
            if isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], str):
                try:
                    return json.loads(obj[0])
                except json.JSONDecodeError:
                    return obj
            elif isinstance(obj, str):
                try:
                    return json.loads(obj)
                except json.JSONDecodeError:
                    return obj
            return obj

        parsed = [parse(m) for m in target]

        extracted = [
            get_by_json_pointer(msg, json_path) if isinstance(msg, dict) else None
            for msg in parsed
        ]

        if len(extracted) == 1:
            return {"data": extracted[0]}
        else:
            return {"data": extracted}

service = JsonPathService()
