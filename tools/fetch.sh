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

echo "==> technologies/all.json, civilizations/<civ>.json"
curl -sSL --max-time 120 https://data.aoe4world.com/technologies/all.json -o data/technologies-all.json
python3 - <<'PYT'
import json, os, urllib.request
idx = json.load(open('data/civs-index.json'))
os.makedirs('data/civ-overviews', exist_ok=True)
for code, c in idx.items():
    url = f"https://data.aoe4world.com/civilizations/{c['slug']}.json"
    with urllib.request.urlopen(url, timeout=60) as r:
        d = json.loads(r.read())
    d.pop('techtree', None)      # 使わないうえに重い
    json.dump(d, open(f"data/civ-overviews/{c['slug']}.json", 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
print(f'   civ overviews: {len(idx)}')
PYT

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

echo "==> technology icons"
python3 -c "
import collections, json, os
d = json.load(open('data/technologies-all.json'))['data']
owners = collections.defaultdict(set)
for t in d: owners[t['baseId']].add(t['civs'][0])
# 固有テクノロジーぶんだけ落とす（判定は tools/build_civs.py と同じ）
uniq = [t for t in d if t.get('unique') or len(owners[t['baseId']]) == 1]
rows = {(t['icon'], os.path.join('assets/techs', t['id'] + '.png')) for t in uniq if t.get('icon')}
missing = [f'{u}\t{p}' for u, p in sorted(rows) if not os.path.exists(p)]
open('/tmp/aoe4-techicons.tsv','w').write('\n'.join(missing))
print(f'   {len(rows)} icons, {len(missing)} to download')"
if [ -s /tmp/aoe4-techicons.tsv ]; then
  awk -F'\t' '{print $1" "$2}' /tmp/aoe4-techicons.tsv | \
    xargs -P 4 -n 2 sh -c 'curl -sSL --max-time 30 --create-dirs "$0" -o "$1"'
fi
