#!/bin/bash

# Check if the model is available
curl --fail http://ollama:11434/api/models/nomic-embed-text || exit 1
