#!/bin/sh
set -e
chown -R appuser:appuser /data
exec su appuser -s /bin/sh -c 'exec "$@"' -- "$@"
