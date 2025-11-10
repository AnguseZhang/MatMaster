#!/bin/bash

SCRIPT_PATH=$(realpath "$BASH_SOURCE")
MATMASTER_DIR=$(dirname $(dirname $(dirname $(dirname "$SCRIPT_PATH"))))
THREADS_DIR=$MATMASTER_DIR/evaluate/experiments/threads

if [ x"$1" == x ];then
  echo "Please specify evaluation type...[$(ls -l $THREADS_DIR | grep '^d' | awk '{print $9}'| xargs)]"
  exit 1
fi

# Check if we're on Windows or Unix-like system and set Python path accordingly
if [ -d "$MATMASTER_DIR/.venv/Scripts" ]; then
  # Windows system
  PYTHON=$MATMASTER_DIR/.venv/Scripts/python.exe
else
  # Unix-like system
  PYTHON=$MATMASTER_DIR/.venv/bin/python
fi

set -a
# Check if .env file exists before sourcing
if [ -f "$MATMASTER_DIR/.env" ]; then
  source $MATMASTER_DIR/.env
fi
set +a

export PYTHONPATH=$MATMASTER_DIR:$PYTHONPATH
export MAX_JOBS=3

# Check if Python executable exists
if [ ! -f "$PYTHON" ]; then
  echo "Error: Python executable not found at $PYTHON"
  echo "Please make sure the virtual environment is properly set up."
  exit 1
fi

# Use relative path to avoid Windows Git Bash path issues
RELATIVE_JSON_PATH="$1/$1.json"

# Check if JSON file exists
if [ ! -f "$THREADS_DIR/$RELATIVE_JSON_PATH" ]; then
  echo "Error: JSON file not found at expected location:"
  echo "  $THREADS_DIR/$RELATIVE_JSON_PATH"
  echo "Available evaluation types:"
  ls -l $THREADS_DIR | grep '^d' | awk '{print "  - " $9}'
  exit 1
fi

# Create temporary Python script for better cross-platform compatibility
PYTHON_SCRIPT=$(mktemp)
cat > "$PYTHON_SCRIPT" <<EOF
import os
import sys
import json
if not os.path.exists(f'$THREADS_DIR/$1/logs'):
    os.makedirs(f'$THREADS_DIR/$1/logs')
try:
    # Use relative path to avoid Windows Git Bash path issues
    filepath = '$RELATIVE_JSON_PATH'
    with open(filepath, 'r', encoding='utf-8') as f:
        dataset_json = json.load(f)
    print(len(dataset_json))
except Exception as e:
    print("Error:", str(e), file=sys.stderr)
    sys.exit(1)
EOF

# Change to THREADS_DIR directory to ensure relative paths work correctly
cd "$THREADS_DIR"

# Run Python script to get total count
TOTAL_TEMP_FILE=$(mktemp)
ERROR_TEMP_FILE=$(mktemp)

"$PYTHON" "$PYTHON_SCRIPT" >"$TOTAL_TEMP_FILE" 2>"$ERROR_TEMP_FILE"

# Check for Python errors
if [ $? -ne 0 ] || [ -s "$ERROR_TEMP_FILE" ]; then
  echo "Error: Failed to compute total number of items. Check if the JSON file exists and is valid."
  echo "File used: $THREADS_DIR/$RELATIVE_JSON_PATH"
  cat "$ERROR_TEMP_FILE"
  rm -f "$TOTAL_TEMP_FILE" "$ERROR_TEMP_FILE" "$PYTHON_SCRIPT"
  exit 1
fi

TOTAL=$(cat "$TOTAL_TEMP_FILE")
rm -f "$TOTAL_TEMP_FILE" "$ERROR_TEMP_FILE" "$PYTHON_SCRIPT"

# Check if TOTAL was successfully computed
if [ -z "$TOTAL" ] || ! [[ "$TOTAL" =~ ^[0-9]+$ ]]; then
  echo "Error: Failed to compute total number of items. Check if the JSON file exists and is valid."
  echo "File used: $THREADS_DIR/$RELATIVE_JSON_PATH"
  exit 1
fi

echo '总数据量:' $TOTAL

running_jobs=0

for ((i=0; i<$TOTAL; i++)); do
    echo "🚀 提交任务: item $i"
    sleep 3
    $PYTHON $THREADS_DIR/$1/${1}_bash.py \
        --item_id $i >  $THREADS_DIR/$1/logs/item_$i.log 2>&1 &

    ((running_jobs++))

    # 如果正在运行的任务数达到上限，就等待任意一个完成
    if (( running_jobs >= MAX_JOBS )); then
        wait -n
        ((running_jobs--))
    fi
done

# 等待最后一批任务
wait
echo "✅ 所有任务完成"
