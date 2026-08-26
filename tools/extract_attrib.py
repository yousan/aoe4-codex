# -*- coding: utf-8 -*-
"""ゲーム本体の Attrib.sga から、いま入っているパッチの数値を取り出す。

upstream (aoe4world/data) は構造（どの文明・時代・生産施設か）を持っているが、
数値の更新はパッチから遅れる。こちらはインストール済みのゲームから直接読むので、
常に手元のバージョンと一致する。

    python3 tools/extract_attrib.py [ゲームのインストール先] [--diff]

出力: data/attrib-live.json   {attribName: {...}} 形式
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sga import Sga, read_rgd  # noqa: E402

DEFAULT_DIRS = [
    '/mnt/c/Program Files (x86)/Steam/steamapps/common/Age of Empires IV',
    'C:/Program Files (x86)/Steam/steamapps/common/Age of Empires IV',
]
SCALE = 4.0        # ゲーム内部の距離・速度はタイルの4倍で入っている
ATTACK_TICK = 0.125  # 1発ぶんの固定時間。upstream の durations.attack と同じ


def deep_merge(parent, child):
    out = dict(parent)
    for k, v in child.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def get(d, *path, default=None):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return default
        d = d[p]
    return d


def unit_stats(e):
    cost = get(e, 'cost_ext', 'time_cost', 'cost', default={}) or {}
    armor = get(e, 'health_ext', 'armor_scaler_by_damage_type', default={}) or {}
    return {
        'hp': get(e, 'health_ext', 'hitpoints'),
        'armor': {'melee': armor.get('Melee'), 'ranged': armor.get('Ranged')},
        'cost': {'food': cost.get('food'), 'wood': cost.get('wood'),
                 'gold': cost.get('gold'), 'stone': cost.get('stone')},
        'time': get(e, 'cost_ext', 'time_cost', 'time_seconds'),
        'pop': get(e, 'population_ext', 'personnel_pop'),
        'speed': (get(e, 'moving_ext', 'speed_scaling_table', 'default_speed') or 0) / SCALE or None,
    }


def weapon_stats(e):
    w = e.get('weapon_bag') or {}
    dmg = w.get('damage') or {}
    fire = w.get('fire') or {}
    dur = lambda *p: get(w, *p, default=0) or 0          # noqa: E731
    interval = (dur('aim', 'fire_aim_time', 'min') + (fire.get('wind_up') or 0) + ATTACK_TICK
                + (fire.get('wind_down') or 0)
                + dur('cooldown', 'duration', 'min') + dur('reload', 'duration', 'min'))
    return {
        'type': dmg.get('damage_type'),
        'damage': dmg.get('max'),
        'interval': round(interval, 4) or None,
        'range': (get(w, 'range', 'max') or 0) / SCALE or None,
        'windup': fire.get('wind_up'), 'winddown': fire.get('wind_down'),
        'setup': dur('setup', 'duration'), 'teardown': dur('teardown', 'duration'),
        'cooldown': dur('cooldown', 'duration', 'min'),
        'reload': dur('reload', 'duration', 'min'),
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    game = args[0] if args else next((d for d in DEFAULT_DIRS
                                      if os.path.isdir(os.path.join(d, 'cardinal', 'archives'))), None)
    if not game:
        sys.exit('ゲームのインストール先が見つからない。引数で渡してください。')
    sga = Sga(os.path.join(game, 'cardinal', 'archives', 'Attrib.sga'))
    print(f'Attrib.sga: {len(sga.entries)} files')

    # 同じ名前の rgd が ebps / sbps / weapon にあるので、種類ごとに引く
    index = {'ebps': {}, 'sbps': {}, 'weapon': {}}
    for path in sga.names():
        norm = path.replace('\\', '/')
        base = norm.rsplit('/', 1)[-1]
        if not base.endswith('.rgd'):
            continue
        for kind in index:
            if f'/{kind}/' in norm:
                index[kind].setdefault(base[:-4], path)
                break

    cache = {}

    def load(kind, name, depth=0):
        """parent_pbg を辿って親の値を継承させる"""
        key = (kind, name)
        if key in cache:
            return cache[key]
        path = index[kind].get(name)
        if not path or depth > 8:
            return {}
        d = (read_rgd(sga.read(path)) or {}).get('default') or {}
        par = d.get('parent_pbg') or {}
        pname = par.get('$PBGNAME')
        if pname and pname != name:
            pkind = (par.get('$PBGMAP') or kind).split('\\')[0].split('/')[0]
            if pkind not in index:
                pkind = kind
            merged = deep_merge(load(pkind, pname, depth + 1), d)
        else:
            merged = d
        cache[key] = merged
        return merged

    upstream = json.load(open(os.path.join(ROOT, 'data', 'units-all.json')))['data']
    out = {'units': {}, 'weapons': {}}
    miss_u = miss_w = 0
    for u in upstream:
        an = u.get('attribName')
        if an and an not in out['units']:
            e = load('ebps', an)
            if not e:
                miss_u += 1
                continue
            try:
                out['units'][an] = unit_stats(e)
            except Exception as ex:
                print('  unit NG', an, ex)
        for w in u.get('weapons') or []:
            wn = w.get('attribName')
            if not wn or wn in out['weapons']:
                continue
            e = load('weapon', wn)
            if not e:
                miss_w += 1
                continue
            try:
                out['weapons'][wn] = weapon_stats(e)
            except Exception as ex:
                print('  weapon NG', wn, ex)

    path = os.path.join(ROOT, 'data', 'attrib-live.json')
    json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f'units {len(out["units"])} (見つからず {miss_u}) / '
          f'weapons {len(out["weapons"])} (見つからず {miss_w}) -> {os.path.getsize(path)//1024} KB')

    if '--diff' in sys.argv:
        diff(upstream, out)
    if '--md' in sys.argv:
        write_md(upstream, out, game)


def diff(upstream, live):
    """upstream の数値と、手元のゲームの数値を突き合わせる"""
    rows = []
    for u in upstream:
        an = u.get('attribName')
        lv = live['units'].get(an)
        if not lv:
            continue
        name = f"{u['name']} ({','.join(u['civs'])})"
        if lv['hp'] is not None and u.get('hitpoints') is not None and \
                abs(lv['hp'] - u['hitpoints']) > 0.01:
            rows.append((name, 'HP', u['hitpoints'], lv['hp']))
        c = u.get('costs') or {}
        for k in ('food', 'wood', 'gold', 'stone'):
            a, b = c.get(k) or 0, lv['cost'].get(k) or 0
            if abs(a - b) > 0.01:
                rows.append((name, k, a, b))
        if c.get('time') and lv['time'] and abs(c['time'] - lv['time']) > 0.01:
            rows.append((name, 'time', c['time'], lv['time']))
        am = {x['type']: x['value'] for x in (u.get('armor') or [])}
        for k, key in (('melee', 'melee'), ('ranged', 'ranged')):
            a, b = am.get(k, 0), lv['armor'].get(key) or 0
            if abs(a - b) > 0.01:
                rows.append((name, f'{k} armor', a, b))
        for w in u.get('weapons') or []:
            lw = live['weapons'].get(w.get('attribName'))
            if not lw:
                continue
            if lw['damage'] is not None and abs((w.get('damage') or 0) - lw['damage']) > 0.01:
                rows.append((f'{name} [{w["name"]}]', 'damage', w.get('damage'), lw['damage']))
            if lw['interval'] and abs((w.get('speed') or 0) - lw['interval']) > 0.02:
                rows.append((f'{name} [{w["name"]}]', 'interval', w.get('speed'), lw['interval']))
    print(f'\n=== 差分 {len(rows)} 件 ===')
    for r in rows[:60]:
        print(f'  {r[0][:52]:54} {r[1]:12} {r[2]} -> {r[3]}')
    if len(rows) > 60:
        print(f'  ... 他 {len(rows)-60} 件')




def write_md(upstream, live, game):
    """上書きした値の一覧を docs/attrib-diff.md に書く"""
    import datetime
    arch = os.path.join(game, 'cardinal', 'archives', 'Attrib.sga')
    stamp = datetime.date.fromtimestamp(os.path.getmtime(arch)).isoformat()
    hp, dmg, arm, other = [], [], [], {'cost': 0, 'time': 0, 'interval': 0}
    for u in upstream:
        lv = live['units'].get(u.get('attribName'))
        if not lv:
            continue
        name = f"{u['name']}（{'/'.join(u['civs'])}）"
        if lv['hp'] and u.get('hitpoints') and round(lv['hp']) != u['hitpoints']:
            hp.append((name, u['hitpoints'], round(lv['hp'])))
        for a in (u.get('armor') or []):
            v = (lv.get('armor') or {}).get(a['type'])
            if v is not None and round(v) != a['value']:
                arm.append((f"{name} {a['type']}", a['value'], round(v)))
        c = u.get('costs') or {}
        for k in ('food', 'wood', 'gold', 'stone'):
            if abs((c.get(k) or 0) - (lv['cost'].get(k) or 0)) > 0.01:
                other['cost'] += 1
        if c.get('time') and lv['time'] and abs(c['time'] - lv['time']) > 0.01:
            other['time'] += 1
        for w in (u.get('weapons') or []):
            lw = live['weapons'].get(w.get('attribName'))
            if not lw:
                continue
            if lw['damage'] is not None and round(lw['damage'], 2) != w.get('damage'):
                dmg.append((f"{name} [{w['name']}]", w.get('damage'), round(lw['damage'], 2)))
            if lw['interval'] and abs((w.get('speed') or 0) - lw['interval']) > 0.02:
                other['interval'] += 1

    def table(rows, head):
        if not rows:
            return [f'{head}: なし', '']
        out = [head, '', '| ユニット | upstream | 手元のゲーム |', '| --- | --- | --- |']
        out += [f'| {a} | {b} | **{c}** |' for a, b, c in rows]
        return out + ['']

    md = [f'# ゲーム本体との差分', '',
          f'- upstream: [aoe4world/data](https://github.com/aoe4world/data) '
          f'（Season 13 / 16.1.9737、2026-05-04 更新）',
          f'- 手元のゲーム: `Attrib.sga` {stamp} 版',
          f'- 生成: `python3 tools/extract_attrib.py --diff --md`', '',
          '## サイトに反映している差分', '',
          'HP・攻撃力・防御は生の値をそのまま読めるので、**手元のゲームの値で上書きしている**。', '']
    md += table(hp, '### HP')
    md += table(dmg, '### 攻撃力')
    md += table(arm, '### 防御')
    md += ['## 反映していない差分', '',
           f'- コスト: {other["cost"]} 件 / 生産時間: {other["time"]} 件 / '
           f'攻撃間隔: {other["interval"]} 件', '',
           'これらは upstream 側が**文明ボーナスを織り込んだ値**を持っていることがあり'
           '（中国の造船が速い、フランスの騎兵が安い、など）、',
           'こちらが読んでいる生値と食い違う。どちらが「表示すべき値」かは項目ごとに'
           '判断が要るので、いまは触っていない。', '',
           '攻撃間隔については、連射武器（諸葛弩など）や設置が要る攻城兵器の扱いも'
           'まだ upstream と揃っていない。', '']
    path = os.path.join(ROOT, 'docs', 'attrib-diff.md')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write('\n'.join(md))
    print(f'docs/attrib-diff.md: HP {len(hp)} / 攻撃力 {len(dmg)} / 防御 {len(arm)} 件')


if __name__ == '__main__':
    main()
