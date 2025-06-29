from .service import Service
from app.zmq_receiver import zmq_receiver
from pydantic import BaseModel, Field
from typing import Optional
import json

class BufferKeysQueryModel(BaseModel):
    last: int = Field(default=1, ge=0, description="Number of latest messages to use (0 means all)")
    key_depth: Optional[int] = Field(
        default=1,
        ge=1,
        le=10,
        description="Depth of nested keys to return"
    )

    model_config = {
        "populate_by_name": True,
    }

def extract_keys(obj, levels: int, level=0):
    if levels <= 0:
        return {}

    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            result[k] = extract_keys(v, levels - 1, level + 1)
        return result

    elif isinstance(obj, list):
        if not obj:
            return None
        # Recurse into first element with same level since list is not a dict key itself
        return extract_keys(obj[0], levels, level + 1)

    else:
        return None

class BufferKeysService(Service):
    query_model = BufferKeysQueryModel

    def get(self, last: int = 1, key_depth: Optional[int] = 1):
        buf = zmq_receiver.get_buffer()
        if not buf:
            return {"keys": None}

        # Determine which messages to use:
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

        keys_list = [
            extract_keys(msg, key_depth) if isinstance(msg, dict) else None
            for msg in parsed
        ]

        if len(keys_list) == 1:
            return {"keys": keys_list[0]}
        else:
            return {"keys": keys_list}

service = BufferKeysService()
