#!/bin/bash

# Script to run Schemathesis tests with automatic server management

echo "========================================="
echo "Running Schemathesis API Tests"
echo "========================================="

# Find an available port (doesn't kill existing servers)
PORT=$(python -c 'import socket; s=socket.socket(); s.bind(("", 0)); print(s.getsockname()[1]); s.close()')
echo "Using port: $PORT"

# Start the FastAPI server in the background
echo "Starting FastAPI server..."
uvicorn backend.main:app --port $PORT --log-level error &
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

# Basic schema validation
echo "[1/3] Running basic schema validation..."
schemathesis run http://localhost:$PORT/openapi.json \
    --checks all \
    --max-examples 10

# Stateful testing with links
echo ""
echo "[2/3] Running stateful tests..."
schemathesis run http://localhost:$PORT/openapi.json \
    --checks all \
    --max-examples 5

# Negative testing
echo ""
echo "[3/3] Running negative tests..."
schemathesis run http://localhost:$PORT/openapi.json \
    --checks negative_data_rejection \
    --max-examples 10

# Store exit code
TEST_EXIT_CODE=$?

# Stop the server
echo ""
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo ""
echo "========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All Schemathesis tests passed!"
else
    echo "❌ Some Schemathesis tests failed"
fi
echo "========================================="

exit $TEST_EXIT_CODE