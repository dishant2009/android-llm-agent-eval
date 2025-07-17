#!/bin/bash
set -euo pipefail

# Install Python dependencies and clone android_world if missing.

echo "[setup] Installing Python dependencies..."
pip install -r requirements.txt

if [ ! -d "android_world" ]; then
  echo "[setup] Cloning android_world repository..."
  git clone https://github.com/google-research/android_world.git
else
  echo "[setup] android_world repository already present. Skipping clone."
fi

echo "[setup] Done! Copy .env.example to .env and add your API keys." 