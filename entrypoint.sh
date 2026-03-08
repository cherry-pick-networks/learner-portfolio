#!/bin/sh
set -e
chown -R appuser:appuser /data
if [ -z "${API_PORT}" ]; then
  echo "API_PORT is required"
  exit 1
fi
exec su appuser -s /bin/sh -c 'uv run uvicorn main:app --host 0.0.0.0 --port "${API_PORT}"'
