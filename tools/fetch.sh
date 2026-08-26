#!/usr/bin/env bash
# 元データ (aoe4world/data, ゲームファイルから自動抽出) を取得する
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data
curl -sSL --max-time 120 https://data.aoe4world.com/units/all.json -o data/units-all.json
python3 - <<'PY'
import json
d = json.load(open('data/units-all.json'))
print('units:', len(d['data']), '/ data version:', d.get('__version__'))
PY
