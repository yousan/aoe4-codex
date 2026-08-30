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

# ゲーム内に対応する文字列が無いラベルだけ、こちらで補う
TERM_FALLBACK = {
    'i-dps': {'ja': 'DPS', 'en': 'DPS'},
    'i-time': {'ja': '生産時間', 'en': 'Build Time'},
    'i-fire': {'ja': '焼夷攻撃', 'en': 'Fire Attack'},
    'a-eleph': {'ja': '象', 'en': 'Elephant'},
}

# 生産施設の日本語名（fallback。通常は data/locale-raw のゲーム内表記を使う）
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


# ---- 表示ラベル（ゲーム内表記に合わせる。UI文言だけは自前）
# en: ゲーム内の英語表記（unit名・建物名は upstream のデータから取る）
# ja: ゲーム内の日本語表記（AoE4攻略wiki / AoE Haul wiki で確認したもの）
ATTR_I18N = {
    'a-heavy': ('重装', 'Heavy'), 'a-light': ('軽装', 'Light'),
    'a-melee': ('近接', 'Melee'), 'a-ranged': ('遠隔', 'Ranged'),
    'a-inf': ('歩兵', 'Infantry'), 'a-cav': ('騎兵', 'Cavalry'),
    'a-camel': ('ラクダ', 'Camel'), 'a-eleph': ('象', 'Elephant'),
    'a-siege': ('攻城兵器', 'Siege'), 'a-ship': ('艦船', 'Ship'),
    'a-relig': ('宗教', 'Religious'), 'a-worker': ('労働者', 'Worker'),
    'a-gun': ('火薬', 'Gunpowder'), 'a-massive': ('巨大', 'Massive'),
    'a-scout': ('斥候', 'Scout'), 'a-spear': ('槍兵', 'Spearman'),
    'a-xbow': ('弩兵', 'Crossbowman'), 'a-bow': ('弓兵', 'Archer'),
}
STAT_I18N = {
    'i-hp': ('HP', 'Hitpoints'), 'i-melee': ('近接攻撃', 'Melee Attack'),
    'i-ranged': ('遠隔攻撃', 'Ranged Attack'), 'i-siege': ('攻城攻撃', 'Siege Attack'),
    'i-fire': ('焼夷攻撃', 'Fire Attack'), 'i-dps': ('DPS', 'DPS'),
    'i-int': ('攻撃間隔', 'Rate of Fire'), 'i-range': ('射程', 'Range'),
    'i-armm': ('近接防御', 'Melee Armor'), 'i-armr': ('遠隔防御', 'Ranged Armor'),
    'i-speed': ('移動速度', 'Movement Speed'), 'i-pop': ('人口', 'Population'),
    'i-time': ('生産時間', 'Build Time'), 'i-food': ('食料', 'Food'),
    'i-wood': ('木材', 'Wood'), 'i-gold': ('金', 'Gold'), 'i-stone': ('石', 'Stone'),
}
UI = {
    'ja': {
        'title': 'AoE4 ユニット', 'pickCiv': '文明を選ぶ', 'units': 'ユニット',
        'view.matrix': '生産施設 × 時代', 'view.table': '表', 'unitsFilter': 'ユニット', 'otherBuilding': 'その他',
        'print': '印刷（A4横）', 'buildings': '生産施設', 'all': 'すべて', 'none': 'なし',
        'age': '時代', 'ageN': '第 {n} 時代', 'home': '文明一覧へ',
        'colUnit': 'ユニット', 'colAge': '時代', 'colTot': '資源計', 'colAtk': '攻撃',
        'noUnits': '該当するユニットがありません。',
        'tip.dps': 'DPS（自爆ユニットは出さない）', 'tip.atk': '攻撃力（{t}）',
        'tip.int': '攻撃間隔（秒）', 'tip.range': '射程（–は近接）',
        'tip.charge': '突進（チャージ）攻撃の威力', 'tip.prov': '仮訳 — 公式の日本語名は未確認',
        'tip.cost': '合計 {n}', 'tip.vs': '対 {c} +{v}', 'builtByUnits': '歩兵ユニットが建設',
        'legend': 'アイコン凡例', 'note': '数値は基礎値。アップグレード・文明ボーナスは含まない。',
        'report': '間違いを報告', 'reportTip': 'この文明のデータの誤りを GitHub の Issue で知らせる',
        'report.title': '[データ] {civ}: ',
        'report.body': ('## 何が違っていたか\n\n'
                        '（ユニット名 / 項目 / このサイトの値 → ゲーム内の値 の順で書いてもらえると助かります）\n\n'
                        '例: 竜軍兵（第III時代）/ 攻撃力 / 18 → 17\n\n\n'
                        '## スクリーンショット（あれば）\n\n\n'
                        '## 環境\n\n'
                        '- 文明: {civ} (`{code}`)\n'
                        '- 見ていたページ: {url}\n'
                        '- 対応パッチ: {patch}\n'
                        '- 表示言語: {lang}\n'),
    },
    'en': {
        'title': 'AoE4 Units', 'pickCiv': 'Choose a civilization', 'units': 'units',
        'view.matrix': 'Building × Age', 'view.table': 'Table', 'unitsFilter': 'Units', 'otherBuilding': 'Other',
        'print': 'Print (A4 landscape)', 'buildings': 'Buildings', 'all': 'All', 'none': 'None',
        'age': 'Age', 'ageN': 'Age {n}', 'home': 'All civilizations',
        'colUnit': 'Unit', 'colAge': 'Age', 'colTot': 'Total', 'colAtk': 'Attack',
        'noUnits': 'No units match.',
        'tip.dps': 'DPS (not shown for self-destructing units)', 'tip.atk': 'Attack ({t})',
        'tip.int': 'Rate of fire (seconds)', 'tip.range': 'Range (– means melee)',
        'tip.charge': 'Charge attack damage', 'tip.prov': 'Unofficial translation',
        'tip.cost': 'Total {n}', 'tip.vs': 'vs {c} +{v}', 'builtByUnits': 'Built by infantry',
        'legend': 'Icons', 'note': 'Base values. Upgrades and civ bonuses are not included.',
        'report': 'Report an error', 'reportTip': 'Open a GitHub issue about this civilization\'s data',
        'report.title': '[data] {civ}: ',
        'report.body': ('## What is wrong\n\n'
                        '(Unit / stat / value on this site -> value in game)\n\n'
                        'Example: Gilded Man-at-Arms (Age III) / attack / 18 -> 17\n\n\n'
                        '## Screenshot (optional)\n\n\n'
                        '## Context\n\n'
                        '- Civilization: {civ} (`{code}`)\n'
                        '- Page: {url}\n'
                        '- Game patch of the data: {patch}\n'
                        '- Language: {lang}\n'),
    },
}
DISCLAIMER_I18N = {
    'ja': ('Age Of Empires 4 © Microsoft Corporation. — aoe4units は Microsoft の '
           '<a href="https://www.xbox.com/en-US/developers/rules" target="_blank" rel="noopener">'
           'Game Content Usage Rules</a> に基づき Age of Empires IV のアセットを利用して作成された'
           '非公式のファンツールで、Microsoft によって承認・提携されたものではありません。 '
           'データ: <a href="https://github.com/aoe4world/data" target="_blank" rel="noopener">aoe4world/data</a>'),
    'en': ('Age Of Empires 4 © Microsoft Corporation. — aoe4units was created under Microsoft\'s '
           '<a href="https://www.xbox.com/en-US/developers/rules" target="_blank" rel="noopener">'
           'Game Content Usage Rules</a> using assets from Age of Empires IV, and it is not endorsed by '
           'or affiliated with Microsoft. Data: '
           '<a href="https://github.com/aoe4world/data" target="_blank" rel="noopener">aoe4world/data</a>'),
}

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
            'id': u['id'], 'base': u['b'], 'n': u['n'],
            'age': u['a'], 'civs': u['cv'], 'at': u['at'], 'uq': u.get('uq', False),
            'hp': u['hp'], 'w': w, 'ch': u['ch'], 'bo': u['bo'],
            'am': u['am'], 'ar': u['ar'], 'mv': u['mv'],
            'cost': {'f': u['f'], 'w': u['wd'], 'g': u['g'], 's': u['st'],
                     'tot': u['tot'], 'pop': u['pop'], 't': u['bt']},
            'ic': u['ic'], 'pb': u['pb'],
        })
    civs = sorted({c for u in units for c in u['civs']})
    buildings = sorted({b for u in units for b in u['pb']})

    bl = json.load(open(os.path.join(ROOT, 'data', 'buildings-all.json')))['data']
    bname = {}
    for b in bl:
        bname.setdefault(b.get('baseId'), b.get('name'))
        bname[b.get('id')] = b.get('name')
    civs_idx = json.load(open(os.path.join(ROOT, 'data', 'civs-index.json')))

    def blabel(slug):
        return {'ja': slug_label(slug), 'en': bname.get(slug) or
                ' '.join(w.capitalize() for w in slug.split('-'))}

    civs_idx = json.load(open(os.path.join(ROOT, 'data', 'civs-index.json')))
    raw_dir = os.path.join(ROOT, 'data', 'locale-raw')
    langs = sorted(f[:-5] for f in os.listdir(raw_dir)) if os.path.isdir(raw_dir) else ['en']
    langs.sort(key=lambda l: (l != 'ja', l != 'en', l))

    meta = {
        'source': 'https://github.com/aoe4world/data',
        'patch': ('Season 13 / 16.1.9737（構造）+ ゲーム本体 2026-07-05 版'
                  '（HP・攻撃力・防御）' if os.path.exists(os.path.join(ROOT, 'data', 'attrib-live.json'))
                  else 'Season 13 / 16.1.9737'),
        'langs': langs,
        'civs': {c: {'flag': f'assets/flags/{c}.png',
                     'en': (civs_idx.get(c) or {}).get('name', c)} for c in civs},
        'buildingOrder': BUILDING_ORDER,
        # pb に出てくるもののうち、実在する建物（残りはユニットが建てるもの）
        'buildingSet': sorted(b for b in buildings if b in bname),
        'landmarks': [b for b in buildings if b not in BUILDING_ORDER],
        'unitBuilt': sorted(UNIT_BUILT),
        'classIcon': L.CLASS_ICON,
        'atkIcon': L.ATK_ICON,
        'roman': L.ROMAN,
        'repo': 'https://github.com/yousan/aoe4units',
    }

    # ---- 言語ごとのファイル: ゲーム内表記（locale-raw）＋ UI文言
    i18n_dir = os.path.join(ROOT, 'data', 'i18n')
    os.makedirs(i18n_dir, exist_ok=True)
    for lang in langs:
        raw = json.load(open(os.path.join(raw_dir, f'{lang}.json'), encoding='utf-8'))
        terms = dict(raw.get('terms') or {})
        for k, v in TERM_FALLBACK.items():
            terms.setdefault(k, v.get(lang, v['en']))
        out = {
            'units': raw.get('units') or {},
            'buildings': raw.get('buildings') or {},
            'civs': raw.get('civs') or {},
            'terms': terms,
            'ui': UI.get(lang, UI['en']),
            'uiIsFallback': lang not in UI,
            'disclaimer': DISCLAIMER_I18N.get(lang, DISCLAIMER_I18N['en']),
        }
        json.dump(out, open(os.path.join(i18n_dir, f'{lang}.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, separators=(',', ':'))
    print(f'i18n     : {len(langs)} langs ->', ', '.join(langs))

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
