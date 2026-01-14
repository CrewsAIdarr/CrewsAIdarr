#!/bin/bash

docker run \
  -it --rm \
  --memory=12g \
  --memory-swap=12g \
  --net=host \
  --add-host=host.docker.internal:host-gateway \
  -v $(pwd):/cecli \
  -v $(pwd)/tmp.benchmarks/.:/benchmarks \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  -e HISTFILE=/cecli/.bash_history \
  -e PROMPT_COMMAND='history -a' \
  -e HISTCONTROL=ignoredups \
  -e HISTSIZE=10000 \
  -e HISTFILESIZE=20000 \
  -e AIDER_DOCKER=1 \
  -e AIDER_BENCHMARK_DIR=/benchmarks \
  cecli-cat \
  bash
