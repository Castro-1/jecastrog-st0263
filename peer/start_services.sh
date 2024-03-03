#!/bin/bash

python pserver.py &

PSERVER_PID=$!

python pclient.py &

PCLIENT_PID=$!

wait $PSERVER_PID $PCLIENT_PID

