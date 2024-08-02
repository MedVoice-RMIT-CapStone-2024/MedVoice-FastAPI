./bin/ollama serve &

pid=$!

sleep 5

echo "Pulling LLM"
ollama pull llama2
ollama nomic-embed-text

wait $pid