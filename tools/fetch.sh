#!/usr/bin/env bash
# 元データとユニットアイコンを取得する。
# 出典: https://github.com/aoe4world/data （ゲームファイルから抽出）
# 再頒布は README の「データの出典と権利」を参照。
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data assets/units

echo "==> units/all.json"
curl -sSL --max-time 120 https://data.aoe4world.com/units/all.json -o data/units-all.json
python3 -c "
import json; d=json.load(open('data/units-all.json'))
print('   units:', len(d['data']), '/ data version:', d.get('__version__'))"

echo "==> unit icons"
python3 -c "
import json, os
d = json.load(open('data/units-all.json'))['data']
urls = sorted({u['icon'] for u in d if u.get('icon')})
pre = 'https://data.aoe4world.com/images/units/'
rows = [(u, os.path.join('assets/units', u[len(pre):])) for u in urls if u.startswith(pre)]
missing = [f'{u}\t{p}' for u, p in rows if not os.path.exists(p)]
open('/tmp/aoe4-icons.tsv','w').write('\n'.join(missing))
print(f'   {len(rows)} icons, {len(missing)} to download')"
if [ -s /tmp/aoe4-icons.tsv ]; then
  awk -F'\t' '{print $1" "$2}' /tmp/aoe4-icons.tsv | \
    xargs -P 4 -n 2 sh -c 'curl -sSL --max-time 30 --create-dirs "$0" -o "$1"'
fi
echo "   done: $(find assets/units -type f | wc -l) files, $(du -sh assets/units | cut -f1)"
