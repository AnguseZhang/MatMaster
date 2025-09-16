#!/bin/bash
PYTHON=/internfs/ycjin/MatMaster/.venv/bin/python
set -a
source /internfs/ycjin/MatMaster/.env
set +a

export PYTHONPATH=/internfs/ycjin/MatMaster:$PYTHONPATH
export MAX_JOBS=3

TOTAL=$($PYTHON -c "
import os
import json
with open('structure_generate.json') as f:
        dataset_json = json.load(f)
print(len(dataset_json))
")

echo '总数据量:' $TOTAL

running_jobs=0

for ((i=0; i<$TOTAL; i++)); do
    echo "🚀 提交任务: item $i"
    sleep 3
    $PYTHON /internfs/ycjin/MatMaster/evaluate/experiments/threads/structure_generate/structure_generate_bash.py \
        --item_id $i > item_$i.log 2>&1 &

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
