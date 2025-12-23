#!/usr/bin/bash
: ${EDIT_FORMATS:=$(shuf benchmark/formats.list)}
: ${MODELS:=$(shuf models.list)}
: ${BENCH_CMD:='./benchmark/benchmark.py'}
if [[ -f .env ]]; then
  source .env
fi
for format  in ${EDIT_FORMATS}; do
  for model in ${MODELS}; do
  ${BENCH_CMD} \
    ${model}-${format} \
    --new \
    --model "ollama_chat/${model}" \
    --edit-format ${format} \
    --threads 1 \
    --exercises-dir polyglot-benchmark
  done
done
