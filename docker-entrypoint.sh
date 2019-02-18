#!/bin/sh

NUM_CORES=$(grep -c ^processor /proc/cpuinfo)
NUM_WORKERS=$(($NUM_CORES + 1)) #optimizing concurrency

#execute python app with gunicorn
echo "running $NUM_WORKERS workers"
gunicorn restapp:app --workers=$NUM_WORKERS -b 0.0.0.0:80
