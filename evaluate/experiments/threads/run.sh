#!/bin/bash

SCRIPT_PATH=$(realpath "$BASH_SOURCE")
MATMASTER_DIR=$(dirname $(dirname $(dirname $(dirname "$SCRIPT_PATH"))))
THREADS_DIR=$MATMASTER_DIR/evaluate/experiments/threads

if [ x"$1" == x ];then
  echo "Please specify evaluation type...[$(ls -l $THREADS_DIR | grep '^d' | awk '{print $9}'| xargs)]"
  exit 1
fi

PYTHON=$MATMASTER_DIR/.venv/bin/python # your .venv
set -a
source $MATMASTER_DIR/.env # your .env
set +a

export PYTHONPATH=$MATMASTER_DIR:$PYTHONPATH
export MAX_JOBS=5

TOTAL=$($PYTHON -c "
import os
import json
if not os.path.exists(f'$THREADS_DIR/$1/logs'):
    os.makedirs(f'$THREADS_DIR/$1/logs')

with open('$THREADS_DIR/$1/$1.json') as f:
        dataset_json = json.load(f)
print(len(dataset_json))
")

echo '总数据量:' $TOTAL

running_jobs=0

for ((i=0; i<$TOTAL; i++)); do
    echo "🚀 提交任务: item $i"
    sleep 3
    $PYTHON $THREADS_DIR/$1/$1_bash.py \
        --item_id $i > logs/item_$i.log 2>&1 &

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
