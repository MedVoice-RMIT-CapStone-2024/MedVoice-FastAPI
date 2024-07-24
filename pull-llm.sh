./bin/ollama serve &

pid=$!

sleep 5

echo "Pulling LLM"
ollama pull llama3

wait $pid