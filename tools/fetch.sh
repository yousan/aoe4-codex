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

echo "==> buildings/all.json, civilizations/civs-index.json"
curl -sSL --max-time 120 https://data.aoe4world.com/buildings/all.json -o data/buildings-all.json
curl -sSL --max-time 60 https://data.aoe4world.com/civilizations/civs-index.json -o data/civs-index.json

echo "==> civ flags (aoe4world/explorer)"
python3 - <<'PYX'
import urllib.request, os
FLAG = {'ab':'ab','ay':'ay','by':'by','ch':'ch','de':'de','en':'en','fr':'fr',
        'gol':'goldenhorde','hl':'hl','hr':'hr','ja':'ja','je':'je','jin':'jindynasty',
        'kt':'kt','ma':'ma','mac':'macedonian','mo':'mo','od':'od','ot':'ot','ru':'ru',
        'sen':'sengoku','tug':'tughlaq','zx':'zx'}
base = 'https://raw.githubusercontent.com/aoe4world/explorer/main/assets/flags/'
os.makedirs('assets/flags', exist_ok=True)
n = 0
for code, name in FLAG.items():
    dst = f'assets/flags/{code}.png'
    if os.path.exists(dst):
        continue
    urllib.request.urlretrieve(base + name + '.png', dst); n += 1
print(f'   flags: {n} downloaded, {len(FLAG)} total')
PYX

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
