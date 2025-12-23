#!/usr/bin/bash
EDIT_FORMATS=$(shuf formats.list)
MODELS=$(shuf models.list)
for format  in ${EDIT_FORMATS}; do
  for model in ${MODELS}; do
  ./benchmark/benchmark.py ${model}-${format} \
    --new \
    --model "ollama_chat/${model}" \
    --edit-format ${format} \
    --threads 1 \
    --exercises-dir polyglot-benchmark
  done
done
