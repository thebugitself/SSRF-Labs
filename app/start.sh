#!/bin/sh

# Start the internal admin service on localhost only (not exposed externally)
uvicorn internal_app:app --host 127.0.0.1 --port 80 &

# Start the main web application on all interfaces (exposed to host)
exec uvicorn main:app --host 0.0.0.0 --port 8000
