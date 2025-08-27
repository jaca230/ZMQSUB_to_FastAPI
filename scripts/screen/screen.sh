#!/bin/bash

BASE_SESSION_NAME="fastapi_server"
DEFAULT_PORT="8000"

usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message and exit"
    echo "  -p, --port     Port number (default: $DEFAULT_PORT)"
    echo ""
    echo "All other arguments are passed directly to run.sh"
    echo "Example:"
    echo "  $0 -p 8080 -r -a 0.0.0.0"
}

# Parse arguments to extract port
PORT="$DEFAULT_PORT"
ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -p|--port)
            if [[ -n "$2" && "$2" != -* ]]; then
                PORT="$2"
                ARGS+=("$1" "$2")
                shift 2
            else
                echo "Error: --port requires a value"
                exit 1
            fi
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

# Create session name with port
SESSION_NAME="${BASE_SESSION_NAME}_${PORT}"

# Resolve the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
RUN_SCRIPT="$SCRIPT_DIR/../run.sh"

# Kill existing screen session with this name
if screen -list | grep -q "$SESSION_NAME"; then
    echo "[INFO] Existing screen session '$SESSION_NAME' found. Killing it..."
    screen -S "$SESSION_NAME" -X quit
    sleep 1
fi

# Launch new screen session and run run.sh with all arguments
echo "[INFO] Starting new screen session '$SESSION_NAME' with port $PORT..."
screen -dmS "$SESSION_NAME" bash -c "\"$RUN_SCRIPT\" ${ARGS[*]}; exec bash"

echo "[INFO] Screen session '$SESSION_NAME' started. Use 'screen -r $SESSION_NAME' to attach."
