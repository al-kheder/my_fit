#!/bin/sh
# Use the PORT env var or default to 8000
port="${PORT:-8000}"
exec uvicorn main:app --host 0.0.0.0 --port "$port"
