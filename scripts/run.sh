#!/bin/bash

usage() {
  echo "Usage: $0 [options]

Options:
  -h, --help          Show this help message and exit
  -p, --port PORT     Set the port (default: 8000)
  -r, --reload        Enable auto-reload (default: off)
  -a, --host ADDRESS  Set the host address (default: 127.0.0.1)
  -m, --module MODULE Set the uvicorn module path (default: app.main:app)

Examples:
  $0 -p 8080 -r       Run on port 8080 with reload enabled
  $0 --host 0.0.0.0   Run accessible on all interfaces
  $0 --module main:app  Run uvicorn with module main:app
"
}

# Defaults
PORT=8000
HOST="127.0.0.1"
RELOAD=""
MODULE="app.main:app"

# Resolve project root (assumes script lives in scripts/)
PROJECT_ROOT=$(dirname "$(dirname "$(realpath "$0")")")

# Append PROJECT_ROOT to PYTHONPATH if not already there
if [[ ":$PYTHONPATH:" != *":$PROJECT_ROOT:"* ]]; then
  if [ -z "$PYTHONPATH" ]; then
    export PYTHONPATH="$PROJECT_ROOT"
  else
    export PYTHONPATH="$PYTHONPATH:$PROJECT_ROOT"
  fi
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      usage
      exit 0
      ;;
    -p|--port)
      PORT="$2"
      shift 2
      ;;
    -a|--host)
      HOST="$2"
      shift 2
      ;;
    -r|--reload)
      RELOAD="--reload"
      shift
      ;;
    -m|--module)
      MODULE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

echo "Starting FastAPI server on http://$HOST:$PORT (reload: ${RELOAD:-off}, module: $MODULE)"
uvicorn "$MODULE" --host "$HOST" --port "$PORT" $RELOAD
