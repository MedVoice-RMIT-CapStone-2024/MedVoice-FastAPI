#!/bin/bash

# wait-for-it.sh script
# Use this script to wait for another service to become available

TIMEOUT=20  # Increased timeout to 20 seconds for better reliability
WAIT_HOST=$1
WAIT_PORT=$2

if [[ $WAIT_HOST == "" || $WAIT_PORT == "" ]]; then
  echo "Usage: $0 host port"
  exit 1
fi

shift 2

cmd="$@"

start_ts=$(date +%s)
while :
do
  if nc -z $WAIT_HOST $WAIT_PORT; then
    break
  fi

  curr_ts=$(date +%s)
  elapsed_time=$((curr_ts - start_ts))

  if [ $elapsed_time -ge $TIMEOUT ]; then
    echo "Timeout of $TIMEOUT seconds reached. Moving on..."
    break
  fi

  echo "Waiting for $WAIT_HOST:$WAIT_PORT..."
  sleep 1
done

>&2 echo "$WAIT_HOST:$WAIT_PORT is available"

exec $cmd
