# ZMQ Receiver Backend with FastAPI and Dynamic Services

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-0.29.0-blue.svg)](https://www.uvicorn.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

This project provides a backend server built with **FastAPI** that asynchronously receives data via **ZeroMQ (ZMQ)**, buffers recent messages, and exposes flexible REST API endpoints dynamically registered from service classes.

---

## Features

* **ZMQ Subscriber**: Connects to a ZMQ publisher on a configurable URL and topic, buffering the latest messages.
* **Dynamic REST API endpoints**: Services are auto-registered from Python modules under `app.services`.
* **Data querying services**:

  * Retrieve last N messages
  * Extract nested keys up to a specified depth
  * Extract data via JSON Pointer paths
* Clean startup and shutdown of the ZMQ receiving thread.

---

## Project Structure

```
.
├── app
│   ├── api
│   │   └── endpoints.py          # FastAPI router registering dynamic service endpoints
│   ├── services                  # Services providing API endpoints
│   │   ├── buffer_service.py     # Returns buffered ZMQ messages with optional limit
│   │   ├── buffer_keys_service.py # Returns nested keys from buffered messages
│   │   ├── json_path_service.py  # Extracts data via JSON Pointer paths
│   │   └── service.py            # Base Service class
│   ├── zmq_receiver.py           # ZMQ subscriber implementation
│   └── main.py                   # FastAPI app entrypoint and lifecycle events
├── scripts
│   └── run.sh                   # Bash script to run the FastAPI server with options
├── requirements.txt             # Python dependencies
└── README.md
```

---

## Installation

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```

2. Create and activate a Python virtual environment (recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Linux/macOS
   .\venv\Scripts\activate     # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Server

Use the helper script to run the FastAPI server with Uvicorn:

```bash
bash scripts/run.sh [options]
```

### Available options:

| Flag           | Description                     | Default        |
| -------------- | ------------------------------- | -------------- |
| `-p, --port`   | Port number                     | `8000`         |
| `-a, --host`   | Host address                    | `127.0.0.1`    |
| `-r, --reload` | Enable hot reload (development) | Off            |
| `-m, --module` | Python module for uvicorn app   | `app.main:app` |

### Example:

```bash
bash scripts/run.sh -p 8080 -a 0.0.0.0 -r
```

---

## How It Works

* **ZMQ Receiver** (`app/zmq_receiver.py`) connects to the specified ZeroMQ publisher (default `tcp://127.0.0.1:5555`) subscribing to the topic `"DATA"`.
* Received multipart messages are decoded, JSON-parsed, and buffered up to a configurable size (default 50 messages).
* **Dynamic Service Registration**:
  The API router (`app/api/endpoints.py`) auto-discovers service classes under `app.services/`. Each service defines an optional Pydantic query model and a `get()` method. These services expose REST GET endpoints based on their module names.
* **Example Services**:

  * `buffer_service` — Returns last N buffered messages.
  * `buffer_keys_service` — Returns nested keys from buffered messages up to a specified depth.
  * `json_path_service` — Extracts data from messages using JSON Pointer paths.

---

## Example API Usage

* **Get last N messages**:
  `GET /api/buffer_service?last=5`

* **Get keys from last N messages**:
  `GET /api/buffer_keys_service?last=3&key_depth=2`

* **Extract JSON path from last N messages**:
  `GET /api/json_path_service?last=1&json_path=/data_products/ChannelIntegralCollection`

---

## Extending Services

To add a new endpoint:

1. Create a new service module under `app.services/`.
2. Implement a `Service` subclass with an optional Pydantic query model and a `get()` method.
3. The service will be automatically registered and exposed under `/api/<module_name>`.

---

## License

Specify your license here (e.g., MIT License).

