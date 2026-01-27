#!/bin/bash
#
# Run a Python script inside 3D Slicer
#
# Usage:
#   ./scripts/run_in_slicer.sh <script.py> [args...]
#   ./scripts/run_in_slicer.sh scripts/capture_screenshots.py
#   ./scripts/run_in_slicer.sh scripts/capture_screenshots.py --exit
#
# Configuration:
#   Set SLICER_PATH in .env file or environment variable
#
# Example .env:
#   SLICER_PATH=/opt/Slicer-5.6.0-linux-amd64/Slicer
#

set -e

# Get script directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env if it exists
if [ -f "$PROJECT_DIR/.env" ]; then
    source "$PROJECT_DIR/.env"
fi

# Check SLICER_PATH
if [ -z "$SLICER_PATH" ]; then
    echo "Error: SLICER_PATH not set"
    echo ""
    echo "Set it in .env file:"
    echo "  echo 'SLICER_PATH=/path/to/Slicer' > $PROJECT_DIR/.env"
    echo ""
    echo "Or set environment variable:"
    echo "  export SLICER_PATH=/path/to/Slicer"
    exit 1
fi

if [ ! -x "$SLICER_PATH" ]; then
    echo "Error: Slicer not found or not executable: $SLICER_PATH"
    exit 1
fi

# Check for script argument
if [ $# -lt 1 ]; then
    echo "Usage: $0 <script.py> [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 scripts/capture_screenshots.py"
    echo "  $0 scripts/capture_screenshots.py --exit"
    exit 1
fi

PYTHON_SCRIPT="$1"
shift

# Resolve script path relative to project directory
if [[ ! "$PYTHON_SCRIPT" = /* ]]; then
    PYTHON_SCRIPT="$PROJECT_DIR/$PYTHON_SCRIPT"
fi

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Create logs directory
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

# Create timestamped log file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCRIPT_NAME=$(basename "$PYTHON_SCRIPT" .py)
LOG_FILE="$LOG_DIR/${SCRIPT_NAME}_${TIMESTAMP}.log"

echo "Running: $PYTHON_SCRIPT"
echo "Slicer: $SLICER_PATH"
echo "Log: $LOG_FILE"
echo "Args: $@"
echo ""

# Run Slicer with the Python script
# Tee output to both terminal and log file
"$SLICER_PATH" --python-script "$PYTHON_SCRIPT" "$@" 2>&1 | tee "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "Exit code: $EXIT_CODE"
echo "Log saved: $LOG_FILE"

exit $EXIT_CODE
