#!/bin/bash

# wait-for-it.sh script
# Use this script to wait for another service to become available

# This is the original wait-for-it.sh script from the GitHub repository

TIMEOUT=15
WAIT_HOST=$1
WAIT_PORT=$2

if [[ $WAIT_HOST == "" || $WAIT_PORT == "" ]]; then
  echo "Usage: $0 host port"
  exit 1
fi

shift 2

cmd="$@"

while ! nc -z $WAIT_HOST $WAIT_PORT; do
  echo "Waiting for $WAIT_HOST:$WAIT_PORT..."
  sleep 1
  TIMEOUT=$(($TIMEOUT - 1))
  if [[ $TIMEOUT == 0 ]]; then
    echo "Timeout waiting for $WAIT_HOST:$WAIT_PORT"
    exit 1
  fi
done

>&2 echo "$WAIT_HOST:$WAIT_PORT is available"

exec $cmd
