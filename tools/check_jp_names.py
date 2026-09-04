#!/usr/bin/env python3
"""tools/ にハードコードした日本語名が、ゲーム本体のロケールとズレていないか検査する。

日本語名はロケール（data/locale-raw/ja.json）と各ツールの辞書の2箇所にある。
辞書はロケールに無い建物のためのフォールバックなので消せないが、値が食い違ったまま
放置されると slug_label() 経由で誤った名前が生成物に載る（issue #38）。

    python3 tools/check_jp_names.py

ズレがあれば一覧を出して exit 1。
"""
import ast
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ロケールに存在しない（＝突き合わせようがない）ので検査から外すもの
EXEMPT = {'capital-town-center', 'wonder'}


def load_locale():
    raw = json.loads((ROOT / 'data/locale-raw/ja.json').read_text())
    return raw['buildings']


def load_dict(path, name):
    src = (ROOT / path).read_text()
    m = re.search(name + r'\s*=\s*(\{.*?\n?\})', src, re.S)
    if not m:
        raise SystemExit(f'{path} に {name} が見つからない')
    return ast.literal_eval(m.group(1))


def check(locale, path, name, problems):
    for slug, jp in load_dict(path, name).items():
        if slug in EXEMPT:
            continue
        # ロケール側は age サフィックス付き（barracks-1 など）でも入っている
        found = {v for k, v in locale.items()
                 if k == slug or re.fullmatch(re.escape(slug) + r'-\d', k)}
        if not found:
            problems.append(f'{path}:{name} {slug!r} → ロケールに該当なし（slug 自体が誤り？）')
        elif jp not in found:
            problems.append(
                f'{path}:{name} {slug!r} = {jp!r} → 正: ' + ' / '.join(sorted(found)))


def check_tiers(problems):
    """時代接頭辞。ユニット名から実際に剥がせるかで確かめる。"""
    src = (ROOT / 'tools/build_matrix.py').read_text()
    m = re.search(r'TIERS\s*=\s*(\(.*?\))', src, re.S)
    tiers = ast.literal_eval(m.group(1))
    names = json.loads((ROOT / 'data/locale-raw/ja.json').read_text())['units'].values()
    for t in tiers:
        if not any(n.startswith(t) for n in names):
            problems.append(
                f'tools/build_matrix.py:TIERS {t!r} で始まるユニットが1つも無い（誤訳？）')


def main():
    problems = []
    locale = load_locale()
    check(locale, 'tools/build_data.py', 'BUILDING_JP', problems)
    check(locale, 'tools/build_data.py', 'LANDMARK_JP', problems)
    check(locale, 'tools/build_matrix.py', 'LANDMARK_JP', problems)
    check_tiers(problems)

    if problems:
        print(f'ゲーム内表記とズレている箇所が {len(problems)} 件:\n')
        for p in problems:
            print('  ❌', p)
        return 1
    print('OK: ハードコードした日本語名はすべてロケールと一致している')
    return 0


if __name__ == '__main__':
    sys.exit(main())
