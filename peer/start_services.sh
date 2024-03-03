#!/bin/bash

# Start pserver.py in the background
python pserver.py &
PSERVER_PID=$!

# Start pclient.py in the foreground
python pclient.py

# After pclient.py exits, gracefully shutdown pserver.py
kill -SIGTERM $PSERVER_PID
wait $PSERVER_PID
