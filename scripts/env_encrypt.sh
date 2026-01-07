#!/usr/bin/env bash
set -euo pipefail

KEY_ID="YOUR_KEY_ID"

if [ ! -f .env ]; then
  echo ".env not found" >&2
  exit 1
fi

gpg -e -r "$KEY_ID" .env
echo "Encrypted .env to .env.gpg"
