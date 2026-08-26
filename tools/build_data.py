# -*- coding: utf-8 -*-
"""upstream の units/all.json から、表示用の JSON を生成する。

出力:
  data/units.json  全ユニット（同一ステータスはまとめた派生データ）
  data/meta.json   文明名・施設名・アイコンのラベル
表示側（js/）はこの2つだけを読む。加工のルール（突進の分離・派生武器の判定・
松明の除外など）はすべてここに集約する。
"""
import json
import collections
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aoe4lib as L  # noqa: E402  データ整形は既存のロジックを使う

CIV_JP = {
    "ab": ("アッバース朝", "アッバース"), "ay": ("アイユーブ朝", "アイユーブ"),
    "by": ("ビザンツ", "ビザンツ"), "ch": ("中国", "中国"),
    "de": ("デリー・スルタン朝", "デリー"), "en": ("イングランド", "イングランド"),
    "fr": ("フランス", "フランス"), "gol": ("ジョチ・ウルス", "ジョチ"),
    "hr": ("神聖ローマ帝国", "神聖ローマ"), "hl": ("ランカスター家", "ランカスター"),
    "ja": ("日本", "日本"), "je": ("ジャンヌ・ダルク", "ジャンヌ"),
    "jin": ("金朝", "金"), "kt": ("テンプル騎士団", "テンプル"),
    "ma": ("マリ", "マリ"), "mac": ("マケドニア朝", "マケドニア"),
    "mo": ("モンゴル", "モンゴル"), "od": ("ドラゴン騎士団", "竜騎士団"),
    "ot": ("オスマン", "オスマン"), "ru": ("ルーシ", "ルーシ"),
    "sen": ("戦国日本", "戦国"), "tug": ("トゥグルク朝", "トゥグルク"),
    "zx": ("朱熹の遺産", "朱熹"),
}

# 生産施設の日本語名（ゲーム内表記）。ここに無いものは英語のまま出す
BUILDING_JP = {
    'town-center': '町の中心', 'capital-town-center': '町の中心（首都）',
    'barracks': '戦士育成所', 'archery-range': '弓兵育成所', 'stable': '騎兵育成所',
    'siege-workshop': '攻囲兵器工房', 'dock': '港', 'monastery': '修道所',
    'mosque': 'モスク', 'market': '市場', 'keep': '要塞', 'outpost': '前哨基地',
    'military-school': '軍事学校', 'prayer-tent': '祈祷テント', 'ger': 'ゲル',
    'pasture': '牧草地', 'farm': '農場', 'mill': '製粉所', 'blacksmith': '鍛冶場',
    'university': '大学', 'madrasa': 'マドラサ', 'house-of-wisdom': '知恵の館',
    'castle': '城', 'wonder': '驚異',
}
# 歴史的建造物など（列にはしないが「＋」で併記する）
LANDMARK_JP = {
    'burgrave-palace': '城伯の宮殿', 'palace-of-swabia': 'シュヴァーベン宮殿',
    'regnitz-cathedral': 'レグニッツ大聖堂', 'berkshire-palace': 'バークシャー宮殿',
    'the-white-tower': 'ホワイトタワー', 'council-hall': '参事議事堂',
    'school-of-cavalry': '騎兵学校', 'red-palace': '赤の宮殿',
    'the-royal-institute': '王立研究所', 'chamber-of-commerce': '商工会議所',
}

# 列に出す施設の順番（右端に町の中心）
BUILDING_ORDER = ['barracks', 'archery-range', 'stable', 'siege-workshop',
                  'dock', 'monastery', 'mosque', 'market', 'military-school',
                  'town-center']

UNIT_BUILT = {'gilded-archer', 'gilded-crossbowman', 'gilded-handcannoneer',
              'gilded-landsknecht', 'gilded-man-at-arms', 'gilded-spearman'}


def slug_label(slug):
    return BUILDING_JP.get(slug) or LANDMARK_JP.get(slug) or \
        ' '.join(w.capitalize() for w in slug.split('-'))


def main():
    units = []
    for u in L.UNITS:
        w = dict(u['w']) if u['w'] else None
        if w and w.get('s') and w['s'] < 0.5:
            w['dps'] = None   # 爆破船などの自爆は DPS 換算しても意味がない
        units.append({
            'id': u['id'], 'base': u['b'], 'n': u['n'], 'jp': u['jp'], 'prov': u['prov'],
            'age': u['a'], 'civs': u['cv'], 'at': u['at'], 'uq': u.get('uq', False),
            'hp': u['hp'], 'w': w, 'ch': u['ch'], 'bo': u['bo'],
            'am': u['am'], 'ar': u['ar'], 'mv': u['mv'],
            'cost': {'f': u['f'], 'w': u['wd'], 'g': u['g'], 's': u['st'],
                     'tot': u['tot'], 'pop': u['pop'], 't': u['bt']},
            'ic': u['ic'], 'pb': u['pb'],
        })
    civs = sorted({c for u in units for c in u['civs']})
    buildings = sorted({b for u in units for b in u['pb']})

    meta = {
        'source': 'https://github.com/aoe4world/data',
        'patch': 'Season 13 / 16.1.9737',
        'civs': {c: {'jp': CIV_JP.get(c, (c, c))[0], 'sh': CIV_JP.get(c, (c, c))[1]} for c in civs},
        'buildings': {b: slug_label(b) for b in buildings},
        'buildingOrder': BUILDING_ORDER,
        'landmarks': {b: slug_label(b) for b in buildings if b not in BUILDING_ORDER},
        'unitBuilt': sorted(UNIT_BUILT),
        'attrs': L.ATTR_JP,
        'stats': L.STAT_JP,
        'classIcon': L.CLASS_ICON,
        'atkIcon': L.ATK_ICON,
        'roman': L.ROMAN,
        'disclaimer': L.DISCLAIMER,
    }

    os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
    up = os.path.join(ROOT, 'data', 'units.json')
    mp = os.path.join(ROOT, 'data', 'meta.json')
    json.dump({'units': units}, open(up, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    json.dump(meta, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    by_civ = collections.Counter(c for u in units for c in u['civs'])
    print(f'units.json: {len(units)} units, {os.path.getsize(up)//1024} KB')
    print(f'meta.json : {len(civs)} civs, {len(buildings)} buildings, '
          f'{os.path.getsize(mp)//1024} KB')
    print('per civ   :', dict(sorted(by_civ.items())))


if __name__ == '__main__':
    main()
