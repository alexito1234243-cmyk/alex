#!/usr/bin/env sh
# Descarga el modelo de voz Kokoro (multilingüe, con voces en español) de las releases de sherpa-onnx en GitHub.
# Con --check también baja Whisper base para comprobar la pronunciación (python3 video/voz.py --check "...").
set -e
DIR="$(cd "$(dirname "$0")" && pwd)/models"
mkdir -p "$DIR"
cd "$DIR"
BASE=https://github.com/k2-fsa/sherpa-onnx/releases/download

fetch() {  # fetch <carpeta> <url>
  [ -d "$1" ] && return
  curl -fL --retry 3 -o "$1.tar.bz2" "$2"
  tar xjf "$1.tar.bz2"
  rm "$1.tar.bz2"
}

fetch kokoro-multi-lang-v1_0 "$BASE/tts-models/kokoro-multi-lang-v1_0.tar.bz2"
if [ "$1" = "--check" ]; then
  fetch sherpa-onnx-whisper-base "$BASE/asr-models/sherpa-onnx-whisper-base.tar.bz2"
fi
pip install -q sherpa-onnx
echo "Modelos listos en $DIR"
