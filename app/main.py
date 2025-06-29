from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints
from app.zmq_receiver import zmq_receiver

app = FastAPI()

# Allow cross-origin requests (use specific domains in prod!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register your API endpoints
app.include_router(endpoints.router, prefix="/api")

# Start ZMQ receiver when app launches
@app.on_event("startup")
def on_startup():
    print("[Startup] Starting ZMQ receiver...")
    zmq_receiver.start()

# Stop ZMQ receiver cleanly on shutdown
@app.on_event("shutdown")
def on_shutdown():
    print("[Shutdown] Stopping ZMQ receiver...")
    zmq_receiver.stop()
