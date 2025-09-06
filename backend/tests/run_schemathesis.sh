#!/bin/bash

# Script to run Schemathesis tests with automatic server management
# Usage: ./run_schemathesis.sh [output_file]
# If output_file is provided, all output will be redirected there

OUTPUT_FILE="$1"

# Function to output either to stdout or file
output() {
    if [ -n "$OUTPUT_FILE" ]; then
        echo "$@" >> "$OUTPUT_FILE"
    else
        echo "$@"
    fi
}

# Redirect all output if file is specified
if [ -n "$OUTPUT_FILE" ]; then
    # Clear the output file
    > "$OUTPUT_FILE"
    exec >> "$OUTPUT_FILE" 2>&1
fi

echo "========================================="
echo "Running Schemathesis API Tests"
echo "========================================="

# Create a temporary directory for the database
TMPDIR=$(mktemp -d)
export DB_PATH="$TMPDIR/test.db"
echo "Using temporary database: $DB_PATH"

# Find an available port (doesn't kill existing servers)
PORT=$(python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')
echo "Using port: $PORT"

# Start the FastAPI server in the background with temp database
echo "Starting FastAPI server..."
DB_PATH="$TMPDIR/test.db" uvicorn backend.main:app --port $PORT --log-level error &
SERVER_PID=$!

# Wait for server to be ready
echo "Waiting for server to start..."
for i in {1..30}; do
    if curl -s http://localhost:$PORT/openapi.json > /dev/null; then
        echo "Server is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Server failed to start after 30 attempts"
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Run Schemathesis tests
echo ""
echo "Running Schemathesis tests..."
echo "-----------------------------------------"

# Comprehensive testing with reasonable examples for fast iteration
echo "[1/1] Running comprehensive API tests (20 examples per endpoint)..."
schemathesis run http://localhost:$PORT/openapi.json \
    --max-examples 20

# Store exit code
TEST_EXIT_CODE=$?

# Stop the server
echo ""
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

# Clean up temporary directory
echo "Cleaning up temporary database..."
rm -rf "$TMPDIR"

echo ""
echo "========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All Schemathesis tests passed!"
else
    echo "❌ Some Schemathesis tests failed"
fi
echo "========================================="

exit $TEST_EXIT_CODE