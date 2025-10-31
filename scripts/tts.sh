#!/usr/bin/env bash
set -euo pipefail

# Defaults (override with flags)
SERVER_URL="${SERVER_URL:-http://localhost:8080}"
ENDPOINT="/v1/audio/speech"
VOICE="af_heart"
FORMAT="wav"
OUT_DIR="${OUT_DIR:-client_out}"

# Flags: -u server -v voice -f format -o out_dir
while getopts "u:v:f:o:" opt; do
  case "$opt" in
    u) SERVER_URL="$OPTARG" ;;
    v) VOICE="$OPTARG" ;;
    f) FORMAT="$OPTARG" ;;
    o) OUT_DIR="$OPTARG" ;;
  esac
done

REQ_TEMPLATE="scripts/request.json"
if [[ ! -f "$REQ_TEMPLATE" ]]; then
  echo "Missing $REQ_TEMPLATE. Create it first." >&2
  exit 1
fi

# Tools check
if ! command -v jq >/dev/null 2>&1; then
  echo "Please install jq (brew install jq)." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

echo "Server:  $SERVER_URL$ENDPOINT"
echo "Voice:   $VOICE"
echo "Format:  $FORMAT"
echo "Out dir: $OUT_DIR"
echo
echo "Type text and press Enter (Ctrl+C to quit)."

i=1
while true; do
  # prompt
  read -r -p "> " LINE || break
  # skip empty lines
  [[ -z "$LINE" ]] && continue

  # build request on the fly (only input changes)
  # keep model/voice/format from the template/flags
  REQ_BODY=$(jq \
    --arg input "$LINE" \
    --arg voice "$VOICE" \
    --arg fmt "$FORMAT" \
    '.input=$input | .voice=$voice | .response_format=$fmt' \
    "$REQ_TEMPLATE")

  # choose extension by format
  case "$FORMAT" in
    wav) EXT="wav" ;;
    mp3) EXT="mp3" ;;
    ogg|opus) EXT="ogg" ;;
    *) EXT="bin" ;;
  esac

  OUT_PATH="$OUT_DIR/utt_$(printf '%04d' "$i").$EXT"

  # call server
  echo "→ Synthesizing…"
  curl -s -X POST "$SERVER_URL$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "$REQ_BODY" \
    --output "$OUT_PATH"

  if [[ ! -s "$OUT_PATH" ]]; then
    echo "Request failed or empty output (see server logs)." >&2
    rm -f "$OUT_PATH"
    continue
  fi

  echo "✔ Saved: $OUT_PATH"

  # auto-play if possible (macOS: afplay; else try ffplay or play)
  if command -v afplay >/dev/null 2>&1; then
    afplay "$OUT_PATH"
  elif command -v ffplay >/dev/null 2>&1; then
    ffplay -autoexit -nodisp "$OUT_PATH" >/dev/null 2>&1
  elif command -v play >/dev/null 2>&1; then
    play "$OUT_PATH" >/dev/null 2>&1
  fi

  i=$((i+1))
done
