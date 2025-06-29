# app/services/buffer_service.py

from .service import Service
from app.zmq_receiver import zmq_receiver
from pydantic import BaseModel, Field
from typing import Optional
import json

class BufferQueryModel(BaseModel):
    last: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of latest messages to return. Returns all if not specified."
    )

class BufferService(Service):
    query_model = BufferQueryModel

    def get(self, last: Optional[int] = None):
        buf = zmq_receiver.get_buffer()
        if not buf:
            return {"data": None}

        if last is None:
            target = buf
        else:
            if last <= 0:
                # If last is zero or negative, return empty list (or raise error if you prefer)
                return {"data": []}
            target = buf[-last:] if len(buf) >= last else buf

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

        # If last was 1, return the single object directly (not a list)
        if last == 1:
            return {"data": parsed[0] if parsed else None}
        else:
            return {"data": parsed}

service = BufferService()
