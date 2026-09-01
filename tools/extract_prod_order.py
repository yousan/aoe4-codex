# -*- coding: utf-8 -*-
"""ゲーム内の生産ボタンの並び順を、建物の spawner_ext から取り出す。

サイトの列の並びを、ゲームの生産キューと同じにするために使う
（戦士育成所なら 槍兵 → 軍兵、のような順番）。

    python3 tools/extract_prod_order.py [ゲームのインストール先]

出力: data/prod-order.json  {文明: {建物: [ユニットのbaseId, ...]}}
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sga import Sga, read_rgd, _Multi  # noqa: E402

DEFAULT_DIRS = [
    '/mnt/c/Program Files (x86)/Steam/steamapps/common/Age of Empires IV',
    'C:/Program Files (x86)/Steam/steamapps/common/Age of Empires IV',
]


def spawn_names(node):
    """spawner_ext から squad の attribName を順番どおりに拾う"""
    items = ((node.get('spawner_ext') or {}).get('spawn_items') or {}).get('spawn_item')
    if items is None:
        return []
    if isinstance(items, dict):
        items = [items]
    out = []
    for it in items:
        sq = (it or {}).get('squad') or {}
        n = sq.get('$PBGNAME')
        if n:
            out.append(n)
    return out


def main():
    game = (sys.argv[1] if len(sys.argv) > 1
            else next((d for d in DEFAULT_DIRS
                       if os.path.isdir(os.path.join(d, 'cardinal', 'archives'))), None))
    if not game:
        sys.exit('ゲームのインストール先が見つからない。引数で渡してください。')
    sga = Sga(os.path.join(game, 'cardinal', 'archives', 'Attrib.sga'))

    units = json.load(open(os.path.join(ROOT, 'data', 'units-all.json')))['data']
    blds = json.load(open(os.path.join(ROOT, 'data', 'buildings-all.json')))['data']
    unit_base = {u['attribName']: u['baseId'] for u in units if u.get('attribName')}

    index = {}
    for path in sga.names():
        norm = path.replace('\\', '/')
        if '/ebps/' in norm and norm.endswith('.rgd'):
            index.setdefault(norm.rsplit('/', 1)[-1][:-4], path)   # 元のキーで引く

    out = {}
    miss = 0
    for b in blds:
        an = b.get('attribName')
        path = index.get(an)
        if not path:
            miss += 1
            continue
        try:
            node = (read_rgd(sga.read(path)) or {}).get('default') or {}
        except Exception:
            continue
        order, seen = [], set()
        for name in spawn_names(node):
            base = unit_base.get(name)
            if base and base not in seen:
                seen.add(base)
                order.append(base)
        if not order:
            continue
        for civ in b.get('civs', []):
            out.setdefault(civ, {})[b['baseId']] = order

    path = os.path.join(ROOT, 'data', 'prod-order.json')
    json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    n = sum(len(v) for v in out.values())
    print(f'prod-order.json: {len(out)} civs / {n} buildings '
          f'({os.path.getsize(path)//1024} KB, 建物の未解決 {miss})')
    for civ in ('en', 'od'):
        if civ in out:
            for b in ('barracks', 'archery-range', 'stable'):
                if b in out[civ]:
                    print(f'  {civ} {b}: {out[civ][b]}')


if __name__ == '__main__':
    main()
