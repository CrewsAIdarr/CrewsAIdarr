#!/usr/bin/env bash
ollama list \
  |awk '{print $1}'\
  |grep -v NAME \
  |grep -v mxbai-embed-large:latest \
  |grep -v nomic-embed-text:latest \
  |grep -v nomic-embed-text-v2-moe:latest \
  > models.list
