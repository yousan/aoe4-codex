# -*- coding: utf-8 -*-
"""ゲーム本体のロケールファイルから、各言語の公式表記を取り出す。

AoE4 の `cardinal/archives/Locale*.sga` には全言語の文字列が入っている。
英語の文字列 → その文字列ID → 各言語の文字列、と辿ると、
ユニット名・建物名・文明名の**公式表記**が機械的に得られる。

    python3 tools/extract_locale.py [ゲームのインストール先]

出力: data/locale-raw/<lang>.json  （ゲーム内表記のみ。UI文言は build_data.py 側）

ゲーム本体が必要。手元に無い場合はこのスクリプトを動かす必要はない
（生成済みの data/locale-raw/*.json がリポジトリに入っている）。
"""
import json
import os
import re
import sys
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DIRS = [
    '/mnt/c/Program Files (x86)/Steam/steamapps/common/Age of Empires IV',
    'C:/Program Files (x86)/Steam/steamapps/common/Age of Empires IV',
    os.path.expanduser('~/.steam/steam/steamapps/common/Age of Empires IV'),
]

# 出力する言語 → ゲームのロケール名
LOCALES = {
    'en': 'English', 'ja': 'Japanese', 'ko': 'Korean',
    'zh-Hans': 'SimplifiedChinese', 'zh-Hant': 'TraditionalChinese',
    'de': 'German', 'fr': 'French', 'es': 'Spanish', 'it': 'Italian',
    'pt-BR': 'BrazilianPortuguese', 'ru': 'Russian', 'tr': 'Turkish',
    'vi': 'Vietnamese', 'pl': 'Polish',
}

# ラベル → ゲーム内の英語表記。ID を直に指定したいものは (英語, ID) で書く
TERMS = {
    'i-hp': 'Health', 'i-melee': 'Melee', 'i-ranged': 'Ranged', 'i-siege': 'Siege',
    'i-int': 'Attack Speed', 'i-range': ('Range', 11252521),
    'i-armm': 'Melee Armor', 'i-armr': 'Ranged Armor', 'i-speed': 'Movement Speed',
    'i-pop': 'Population', 'i-food': 'Food', 'i-wood': 'Wood', 'i-gold': 'Gold',
    'i-stone': 'Stone',
    'a-heavy': 'Heavy', 'a-light': 'Light', 'a-melee': 'Melee', 'a-ranged': 'Ranged',
    'a-inf': 'Infantry', 'a-cav': 'Cavalry', 'a-camel': 'Camel', 'a-siege': 'Siege',
    'a-ship': 'Ship', 'a-relig': 'Religious', 'a-worker': 'Worker',
    'a-gun': 'Gunpowder', 'a-massive': 'Massive', 'a-scout': 'Scout',
    'a-spear': 'Spearman', 'a-xbow': 'Crossbowman', 'a-bow': 'Archer',
}


def find_game_dir(argv):
    if len(argv) > 1:
        return argv[1]
    for d in DEFAULT_DIRS:
        if os.path.isdir(os.path.join(d, 'cardinal', 'archives')):
            return d
    return None


def read_ucs(sga_path):
    """SGA の中の zlib ストリームから UCS（UTF-16LE の "ID<TAB>文字列"）を拾う"""
    raw = open(sga_path, 'rb').read()
    out = {}
    for m in re.finditer(b'\x78[\x01\x9c\xda]', raw):
        try:
            data = zlib.decompressobj().decompress(raw[m.start():])
        except zlib.error:
            continue
        if len(data) < 2000 or not data.startswith(b'\xff\xfe'):
            continue
        for line in data.decode('utf-16-le', 'replace').splitlines():
            if '\t' not in line:
                continue
            k, v = line.split('\t', 1)
            if k.strip().isdigit():
                out[int(k)] = v
    return out


def pick(ids, table):
    """同じ英語に複数IDがあるので、訳が一番多い方を採る"""
    vals = [table[i] for i in ids if i in table and table[i]]
    if not vals:
        return None
    return max(set(vals), key=vals.count)


def main():
    game = find_game_dir(sys.argv)
    if not game:
        sys.exit('ゲームのインストール先が見つからない。引数で渡してください。\n'
                 '例: python3 tools/extract_locale.py "/mnt/c/Program Files (x86)/Steam/'
                 'steamapps/common/Age of Empires IV"')
    arch = os.path.join(game, 'cardinal', 'archives')
    print('game:', game)

    units = json.load(open(os.path.join(ROOT, 'data', 'units.json')))['units']
    buildings = json.load(open(os.path.join(ROOT, 'data', 'buildings-all.json')))['data']
    civs = json.load(open(os.path.join(ROOT, 'data', 'civs-index.json')))

    unit_names = sorted({u['n'] for u in units})
    bld_names = {}
    for b in buildings:
        bld_names.setdefault(b.get('baseId'), b.get('name'))
        bld_names[b.get('id')] = b.get('name')
    civ_names = {c: v['name'] for c, v in civs.items()}

    en = read_ucs(os.path.join(arch, 'LocaleEnglish.sga'))
    rev = {}
    for k, v in en.items():
        rev.setdefault(v, []).append(k)
    print(f'English strings: {len(en)}')

    outdir = os.path.join(ROOT, 'data', 'locale-raw')
    os.makedirs(outdir, exist_ok=True)

    for lang, loc in LOCALES.items():
        path = os.path.join(arch, f'Locale{loc}.sga')
        if not os.path.exists(path):
            print(f'  {lang}: {loc} が無い。とばす')
            continue
        tbl = read_ucs(path)
        data = {'units': {}, 'buildings': {}, 'civs': {}, 'terms': {}}
        miss = []
        for n in unit_names:
            v = pick(rev.get(n, []), tbl)
            if v:
                data['units'][n] = v
            else:
                miss.append(n)
        for slug, n in bld_names.items():
            if not n:
                continue
            v = pick(rev.get(n, []), tbl)
            if v:
                data['buildings'][slug] = v
        for code, n in civ_names.items():
            v = pick(rev.get(n, []), tbl)
            if v:
                data['civs'][code] = v
        for key, spec in TERMS.items():
            if isinstance(spec, tuple):
                v = tbl.get(spec[1])
            else:
                v = pick(rev.get(spec, []), tbl)
            if v:
                data['terms'][key] = v
        json.dump(data, open(os.path.join(outdir, f'{lang}.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1, sort_keys=True)
        print(f'  {lang:8} units {len(data["units"])}/{len(unit_names)}  '
              f'buildings {len(data["buildings"])}  civs {len(data["civs"])}  '
              f'terms {len(data["terms"])}'
              + (f'  未取得: {miss[:3]}' if miss else ''))


if __name__ == '__main__':
    main()
