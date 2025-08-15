from .service import Service
from app.zmq_receiver import zmq_receiver_odb
from pydantic import BaseModel, Field
from typing import Optional
import json

class BufferQueryModelOdb(BaseModel):
    last: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of latest messages to return. Returns all if not specified."
    )

class BufferServiceOdb(Service):
    query_model = BufferQueryModelOdb

    def get(self, last: Optional[int] = None):
        buf = zmq_receiver_odb.get_buffer()
        if not buf:
            return {"data": None}

        if last is None:
            target = buf
        else:
            if last <= 0:
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

        if last == 1:
            return {"data": parsed[0] if parsed else None}
        else:
            return {"data": parsed}

service = BufferServiceOdb()
