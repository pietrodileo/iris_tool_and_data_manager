#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "Retrieving model gemma2:2b..."
ollama pull gemma2:2b
echo "Retrieving model gemma3:1b..."
ollama pull gemma3:1b
echo "Done."

# Wait for Ollama process to finish.
wait $pid

echo "Process exited with code $?"