./bin/ollama serve &

pid=$!

sleep 5

echo "Pulling LLM"
ollama pull llama2

wait $pid