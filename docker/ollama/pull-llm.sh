./bin/ollama serve &

pid=$!

sleep 5

echo "Pulling LLM"
ollama pull nomic-embed-text

wait $pid