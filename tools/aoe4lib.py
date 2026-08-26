# -*- coding: utf-8 -*-
"""v3: 属性を細かくアイコン化 / 重装・軽装の見せ方3案 / 日本語名"""
import json
import collections
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'units-all.json')

RAW = json.load(open(DATA))['data']

# ゲーム本体から抜いた数値があれば、HP・防御・攻撃力だけ上書きする。
# （コスト・生産時間・攻撃間隔は upstream 側が文明ボーナスを織り込んでいることがあり、
#   こちらの生値と食い違うので触らない）
LIVE_PATH = os.path.join(ROOT, 'data', 'attrib-live.json')
LIVE_PATCHED = 0
if os.path.exists(LIVE_PATH):
    _live = json.load(open(LIVE_PATH, encoding='utf-8'))
    for _u in RAW:
        _lv = _live['units'].get(_u.get('attribName'))
        if _lv:
            if _lv.get('hp'):
                if round(_lv['hp']) != _u.get('hitpoints'):
                    LIVE_PATCHED += 1
                _u['hitpoints'] = round(_lv['hp'])
            for _a in (_u.get('armor') or []):
                _v = (_lv.get('armor') or {}).get(_a['type'])
                if _v is not None:
                    if round(_v) != _a.get('value'):
                        LIVE_PATCHED += 1
                    _a['value'] = round(_v)
        for _w in (_u.get('weapons') or []):
            _lw = _live['weapons'].get(_w.get('attribName'))
            if _lw and _lw.get('damage') is not None:
                if round(_lw['damage'], 2) != _w.get('damage'):
                    LIVE_PATCHED += 1
                _w['damage'] = round(_lw['damage'], 2)
IMG = 'https://data.aoe4world.com/images/units/'   # 元データ側のURL（接頭辞の除去に使う）
IMG_BASE = 'assets/units/'                          # 表示はリポジトリ内のミラーを使う

# ---------------------------------------------------------------- 日本語名
# 出典: AoE4攻略Wiki(AoE Haul) の日本語ユニット名 + ゲーム内表記
BASE_JP = {
    'Villager': '農民', 'Imperial Official': '役人', 'Trader': '商人', 'Scout': '斥候',
    'Spearman': '槍兵', 'Man-at-Arms': '軍兵', 'Archer': '弓兵', 'Crossbowman': '弩兵',
    'Longbowman': 'ロングボウ兵', 'Handcannoneer': '砲撃手', 'Streltsy': 'ストレリツィ',
    'Horseman': '騎乗兵', 'Knight': '騎士', 'Lancer': '槍騎兵', 'Royal Knight': '近衛騎士',
    'Camel Rider': 'らくだ騎兵', 'Camel Archer': 'らくだ弓兵', 'War Elephant': '戦象',
    'Monk': '修道士', 'Prelate': '高位聖職者', 'Mangonel': '投石機',
    'Springald': 'スプリンガルド', 'Battering Ram': '破城槌', 'Siege Tower': '攻城塔',
    'Trebuchet': 'トレビュシェット', 'Counterweight Trebuchet': '平衡錘投石機',
    'Culverin': 'カルバリン砲', 'Bombard': '射石砲',
    'Landsknecht': 'ランツクネヒト', 'Zhuge Nu': '諸葛弩兵', 'Palace Guard': '近衛兵',
    'Sofa': 'ソファ', 'Donso': 'ドンソ', 'Javelin Thrower': '投槍兵', 'Sipahi': 'シパーヒー',
    'Fire Lancer': '火炎槍騎兵', 'Galleass': 'ガレアス船', 'Fishing Boat': '漁船',
    'Transport Ship': '輸送船', 'Trade Ship': '交易船', 'Arbalétrier': 'アーバトリエ',
    'Musofadi Warrior': 'ムソファディ戦士', 'Mehter': 'メフテル', 'Samurai': '侍',
    'Galley': 'ガレー船', 'Hulk': 'ハルク船', 'Demolition Ship': '爆破船',
    'Carrack': 'カラック船', 'Baghlah': 'バグラ船', 'Dhow': 'ダウ船',
}
# 公式日本語名を確認できなかったもの（仮訳）
PROV = {'Carrack', 'Counterweight Trebuchet', 'Bombard'}
PROV_PREFIX = set()
PREFIX_JP = [('Vanguard ', '黎明'), ('Early ', '初期'), ('Hardened ', '熟練'),
             ('Veteran ', 'ベテラン'), ('Elite ', '精鋭'), ('Gilded ', '竜')]


def jp_name(en):
    """(日本語名 or None, 仮訳かどうか)"""
    if en in BASE_JP:
        return BASE_JP[en], en in PROV
    for pre, jp in PREFIX_JP:
        if en.startswith(pre):
            sub, prov = jp_name(en[len(pre):])
            if sub:
                return jp + sub, prov or (pre in PROV_PREFIX)
            return None, False
    return None, False


# ---------------------------------------------------------------- 属性
ATTR_JP = {
    'a-heavy': '重装', 'a-light': '軽装', 'a-melee': '近接', 'a-ranged': '遠隔',
    'a-inf': '歩兵', 'a-cav': '騎兵', 'a-camel': 'ラクダ', 'a-eleph': '象',
    'a-siege': '攻城兵器', 'a-ship': '艦船', 'a-worker': '労働者', 'a-relig': '宗教',
    'a-gun': '火薬', 'a-massive': '巨大', 'a-scout': '斥候', 'a-spear': '槍兵',
    'a-xbow': '弩兵', 'a-bow': '弓兵',
}
LIGHT_TOKENS = ('light', 'infantry_light', 'cavalry_light',
                'light_melee_infantry', 'light_gunpowder_infantry')


def attrs(cls):
    c = set(cls)
    out = []
    if 'heavy' in c:
        out.append('a-heavy')
    elif c & set(LIGHT_TOKENS):
        out.append('a-light')
    if 'melee' in c or 'melee_infantry' in c:
        out.append('a-melee')
    if 'ranged' in c:
        out.append('a-ranged')
    for tok, ic in (('infantry', 'a-inf'), ('cavalry', 'a-cav'), ('camel', 'a-camel'),
                    ('elephant', 'a-eleph'), ('siege', 'a-siege'), ('worker', 'a-worker'),
                    ('monk', 'a-relig'), ('gunpowder', 'a-gun'), ('massive', 'a-massive'),
                    ('scout', 'a-scout'), ('spearman', 'a-spear'),
                    ('crossbowman', 'a-xbow'), ('archer', 'a-bow')):
        if tok in c:
            out.append(ic)
    if ('ship' in c or 'naval_unit' in c) and 'a-ship' not in out:
        out.insert(2 if len(out) > 2 else len(out), 'a-ship')
    return out


# ---------------------------------------------------------------- データ整形
def stat_key(u):
    return json.dumps([u.get('hitpoints'), u.get('costs'), u.get('armor'),
                       [(w.get('name'), w.get('damage'), w.get('speed')) for w in u.get('weapons', [])],
                       u.get('movement')], sort_keys=True)


groups = collections.OrderedDict()
for u in RAW:
    groups.setdefault((u['id'], stat_key(u)), []).append(u)

UNITS = []
for (uid, _), members in groups.items():
    u = members[0]
    ws = u.get('weapons') or []
    # 松明（対建物）と突進（チャージ）は通常攻撃と混ぜない
    chg = [w for w in ws if 'charge' in (w.get('attribName') or '')]
    norm = [w for w in ws if w not in chg and w.get('type') != 'fire']
    prio = [w for w in norm if w.get('type') in ('melee', 'ranged', 'siege')] or norm
    main = None
    if prio:
        top = max(w.get('damage') or 0 for w in prio)
        # 同格（威力が近い）の中では、派生武器ではなく基本武器＝attribName が短い方をゲームは表示する
        same = [w for w in prio if (w.get('damage') or 0) >= top * 0.6]
        main = min(same, key=lambda w: (len(w.get('attribName') or ''), -(w.get('damage') or 0)))
    charge = max(chg, key=lambda w: (w.get('damage') or 0)) if chg else None

    # --- ダメージボーナス（対建物・対動物は出さない）
    SKIP = {'building', 'wall', 'gaia', 'animal', 'huntable', 'unit', 'war', 'formation'}
    bonus, seen_b = [], set()
    for w in norm + chg:
        for m in (w.get('modifiers') or []):
            if m.get('property') == 'fireAttack' or m.get('effect') != 'change':
                continue
            for grp in ((m.get('target') or {}).get('class') or []):
                cls = [c for c in grp if c not in SKIP]
                if not cls:
                    continue
                key = (m.get('value'), tuple(sorted(cls)))
                if key in seen_b:
                    continue
                seen_b.add(key)
                bonus.append({'v': m.get('value'), 'c': cls})
    bonus.sort(key=lambda b: -(b['v'] or 0))
    armor = {a.get('type'): a.get('value') for a in (u.get('armor') or [])}
    c = u.get('costs') or {}
    w = {}
    if main:
        spd = main.get('speed') or 0
        dmg = main.get('damage') or 0
        w = {'t': main.get('type'), 'd': dmg, 's': spd,
             'dps': round(dmg / spd, 2) if spd else None,
             'r1': (main.get('range') or {}).get('max')}
    jpn, prov = jp_name(u['name'])
    UNITS.append({'id': uid, 'n': u['name'], 'jp': jpn, 'prov': prov, 'a': u['age'],
                  'cv': sorted({c for m in members for c in m.get('civs', [])}),
                  'at': attrs(u.get('classes', [])), 'hp': u.get('hitpoints'), 'w': w,
                  'am': armor.get('melee') or 0, 'ar': armor.get('ranged') or 0,
                  'f': c.get('food') or 0, 'wd': c.get('wood') or 0, 'g': c.get('gold') or 0,
                  'st': c.get('stone') or 0, 'tot': c.get('total') or 0,
                  'pop': c.get('popcap') or 0, 'bt': c.get('time') or 0,
                  'mv': (u.get('movement') or {}).get('speed'),
                  'ic': (u.get('icon') or '').replace(IMG, ''),
                  'pb': u.get('producedBy') or [], 'b': u.get('baseId'),
                  'ch': ({'d': charge.get('damage'), 's': charge.get('speed')} if charge else None),
                  'bo': bonus})

BY = {}
for u in UNITS:
    BY.setdefault((u['n'], u['a']), u)

# ---------------------------------------------------------------- アイコン
SPRITE = '''<svg style="display:none" xmlns="http://www.w3.org/2000/svg">
<symbol id="i-hp" viewBox="0 0 24 24"><path d="M12 21C5 16.5 3 13 3 9.8A4.6 4.6 0 0 1 12 7.4 4.6 4.6 0 0 1 21 9.8C21 13 19 16.5 12 21Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-melee" viewBox="0 0 24 24"><path d="M12 1.8 14.4 6.5V13.5H9.6V6.5Z" fill="currentColor" stroke="none"/><path d="M7 14.2h10M12 14.2v4.4"/><circle cx="12" cy="20.4" r="1.7" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-ranged" viewBox="0 0 24 24"><path d="M4 20 19 5M13 4.5h6.5V11M4 20l.2-4M4 20l4-.2"/></symbol>
<symbol id="i-siege" viewBox="0 0 24 24"><path d="M2.5 20C5 9.5 13 5.5 19 8.5"/><circle cx="19.5" cy="10.5" r="2.6" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-fire" viewBox="0 0 24 24"><path d="M12 2.5c4 5 6 7.5 6 11a6 6 0 0 1-12 0c0-2 1-3.5 2.5-5 .3 1.6 1 2.5 2 2.5 1.2 0 1.8-1.6 1.5-8.5Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-dps" viewBox="0 0 24 24"><path d="M13.5 2 4 13.5h6L9 22l10-12h-6.5Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-int" viewBox="0 0 24 24"><circle cx="12" cy="14" r="7.5"/><path d="M12 14V9.5M9 2h6M19.5 7 21 5.5"/></symbol>
<symbol id="i-range" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3.8"/><circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-armm" viewBox="0 0 24 24"><path d="M12 2.4 20 6v5.6c0 5-4.4 8.2-8 10-3.6-1.8-8-5-8-10V6Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-armr" viewBox="0 0 24 24"><path d="M12 2.4 20 6v5.6c0 5-4.4 8.2-8 10-3.6-1.8-8-5-8-10V6Z"/><path d="M9.2 14.8 14.8 9.2M11.5 9.2h3.3v3.3" stroke-width="1.7"/></symbol>
<symbol id="i-speed" viewBox="0 0 24 24"><path d="M3 7.5h11M3 12h7.5M3 16.5h9.5"/><path d="M15.5 6.5 21 12l-5.5 5.5"/></symbol>
<symbol id="i-pop" viewBox="0 0 24 24"><circle cx="12" cy="7.5" r="3.7"/><path d="M4.5 20.5c0-4.2 3.4-6.5 7.5-6.5s7.5 2.3 7.5 6.5"/></symbol>
<symbol id="i-time" viewBox="0 0 24 24"><path d="M6.5 2.5h11M6.5 21.5h11M8.5 2.5v3.6L12 10.4l3.5-4.3V2.5M8.5 21.5v-3.6L12 13.6l3.5 4.3v3.6"/></symbol>
<symbol id="i-food" viewBox="0 0 24 24"><path d="M12 22V8"/><path d="M12 16.5c-3.4 0-5.4-2.2-5.4-5.2 3.4 0 5.4 2.2 5.4 5.2Zm0 0c3.4 0 5.4-2.2 5.4-5.2-3.4 0-5.4 2.2-5.4 5.2Z" fill="currentColor" stroke="none"/><path d="M12 10.5c-3 0-4.8-2-4.8-4.6 3 0 4.8 2 4.8 4.6Zm0 0c3 0 4.8-2 4.8-4.6-3 0-4.8 2-4.8 4.6Z" fill="currentColor" stroke="none"/><path d="M12 6.4c1.7-1.6 1.7-3.4 0-4.8-1.7 1.4-1.7 3.2 0 4.8Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="i-wood" viewBox="0 0 24 24"><path d="M12 2.5 6 11h3.2L4.5 18.5h15L14.8 11H18Z" fill="currentColor" stroke="none"/><path d="M12 18.5v3"/></symbol>
<symbol id="i-gold" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.5" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="3.6" fill="#1b1713" stroke="none"/></symbol>
<symbol id="i-stone" viewBox="0 0 24 24"><path d="M4 16.5 8 7l7-2.5 5.5 6-2.5 8-9 1Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-inf" viewBox="0 0 24 24"><path d="M4.5 16.8a7.5 7.5 0 0 1 15 0v3.7h-5.6v-3.7h-3.8v3.7H4.5Z" fill="currentColor" stroke="none"/><path d="M12 9V4.5" stroke-width="2"/></symbol>
<symbol id="a-cav" viewBox="0 0 24 24"><path d="M6.5 21.5V13a5.5 5.5 0 0 1 11 0v8.5"/><circle cx="8" cy="17.5" r="1.2" fill="currentColor" stroke="none"/><circle cx="16" cy="17.5" r="1.2" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-camel" viewBox="0 0 24 24"><path d="M2.5 19.5v-1.8c0-2 1.4-3.6 3.2-3.6s3.2 1.6 3.2 3.6c0-2 1.4-3.6 3.2-3.6s3.2 1.6 3.2 3.6v1.8"/><path d="M15.3 17.7V9.4c0-1.6 1.2-2.9 2.8-2.9h2.4"/></symbol>
<symbol id="a-eleph" viewBox="0 0 24 24"><path d="M3.5 20.5V14a6.2 6.2 0 0 1 12.4 0v6.5"/><path d="M15.9 15c2.9.5 3.7 3.4 1.8 5.5"/><circle cx="7.8" cy="13.2" r="2.4"/><path d="M13.4 19l2.2 1.6"/></symbol>
<symbol id="a-siege" viewBox="0 0 24 24"><path d="M2.5 21h16"/><circle cx="7.5" cy="17.2" r="3.4"/><path d="M5.8 14.4 16.5 5.2"/><path d="M14.6 3h6v5.2h-6Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-ship" viewBox="0 0 24 24"><path d="M2.5 16.5h19l-3 4.5H5.5Z" fill="currentColor" stroke="none"/><path d="M12 16V3M12.8 4.5 19 14.5h-6.2"/></symbol>
<symbol id="a-relig" viewBox="0 0 24 24"><path d="M12 3v18M6 9.5h12"/></symbol>
<symbol id="a-worker" viewBox="0 0 24 24"><path d="M3 21 11 13"/><path d="M11.5 5.5 19 13l-2.8 2.8L8.7 8.3Z"/></symbol>
<symbol id="a-gun" viewBox="0 0 24 24"><circle cx="10" cy="15.5" r="6.2" fill="currentColor" stroke="none"/><path d="M14.6 11c1.5-1.6 2-3 1.6-4.6"/><path d="M18.2 4.4l2.6-1.4M19.6 7.4h3M18.6 1.6l.8 2.4"/></symbol>
<symbol id="a-melee" viewBox="0 0 24 24"><path d="M12 1.8 14.4 6.5V13.5H9.6V6.5Z" fill="currentColor" stroke="none"/><path d="M7 14.2h10M12 14.2v4.4"/><circle cx="12" cy="20.4" r="1.7" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-ranged" viewBox="0 0 24 24"><path d="M4 20 19 5M13 4.5h6.5V11M4 20l.2-4M4 20l4-.2"/></symbol>
<symbol id="a-massive" viewBox="0 0 24 24"><path d="M7.5 7.5h9v9h-9Z" fill="currentColor" stroke="none"/><path d="M4 8.5V4h4.5M15.5 4H20v4.5M20 15.5V20h-4.5M8.5 20H4v-4.5"/></symbol>
<symbol id="a-scout" viewBox="0 0 24 24"><path d="M2 12s3.8-6 10-6 10 6 10 6-3.8 6-10 6-10-6-10-6Z"/><circle cx="12" cy="12" r="2.6" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-spear" viewBox="0 0 24 24"><path d="M3.5 20.5 15.5 8.5"/><path d="M22 2 14 5.5 18.5 10Z" fill="currentColor" stroke="none"/><path d="M9 12.5 11.5 15"/></symbol>
<symbol id="a-xbow" viewBox="0 0 24 24"><path d="M3 6Q12 13 21 6"/><path d="M3 6H21"/><path d="M12 3.5V21M9.2 21h5.6"/></symbol>
<symbol id="a-bow" viewBox="0 0 24 24"><path d="M6 3.5a13 13 0 0 1 0 17"/><path d="M6 3.5 6 20.5"/><path d="M6 12h13M15.5 8.5 19 12l-3.5 3.5"/></symbol>
<symbol id="a-heavy" viewBox="0 0 24 24"><path d="M12 2.4 20 6v5.6c0 5-4.4 8.2-8 10-3.6-1.8-8-5-8-10V6Z" fill="currentColor" stroke="none"/></symbol>
<symbol id="a-light" viewBox="0 0 24 24"><path d="M19.5 3.5C10 4 4.5 9.5 4.5 18v2.5"/><path d="M19.5 3.5c.5 8-4.5 13-11.5 13.5"/></symbol>
</svg>'''

ATK_ICON = {'melee': 'i-melee', 'ranged': 'i-ranged', 'siege': 'i-siege', 'fire': 'i-fire'}
CLASS_ICON = {'heavy': 'a-heavy', 'light': 'a-light', 'melee': 'a-melee', 'ranged': 'a-ranged',
              'infantry': 'a-inf', 'cavalry': 'a-cav', 'camel': 'a-camel', 'elephant': 'a-eleph',
              'siege': 'a-siege', 'ship': 'a-ship', 'naval': 'a-ship', 'fireship': 'a-ship',
              'worker': 'a-worker', 'gunpowder': 'a-gun', 'massive': 'a-massive',
              'scout': 'a-scout', 'spearman': 'a-spear', 'crossbowman': 'a-xbow',
              'archer': 'a-bow', 'monk': 'a-relig'}
STAT_JP = {'i-hp': 'HP', 'i-melee': '近接攻撃', 'i-ranged': '遠隔攻撃', 'i-siege': '攻城攻撃',
           'i-fire': '焼夷攻撃', 'i-dps': 'DPS', 'i-int': '攻撃間隔', 'i-range': '射程',
           'i-armm': '近接防御', 'i-armr': '遠隔防御', 'i-speed': '移動速度',
           'i-pop': '人口', 'i-time': '生産時間', 'i-food': '食料', 'i-wood': '木材',
           'i-gold': '金', 'i-stone': '石'}
ROMAN = ['', 'I', 'II', 'III', 'IV']

DISCLAIMER = ('Age Of Empires 4 © Microsoft Corporation. — '
              'aoe4units は Microsoft の <a href="https://www.xbox.com/en-US/developers/rules" '
              'target="_blank" rel="noopener">Game Content Usage Rules</a> に基づき '
              'Age of Empires IV のアセットを利用して作成された非公式のファンツールで、'
              'Microsoft によって承認・提携されたものではありません。 '
              'データ: <a href="https://github.com/aoe4world/data" target="_blank" rel="noopener">aoe4world/data</a>')



def ico(name, cls=''):
    return f'<svg class="ic {cls}"><use href="#{name}"/></svg>'


def attr_row(u, mode='kanji'):
    """mode: kanji=重/軽の文字, stroke=線の太さ, badge=塗りバッジ"""
    out = []
    for a in u['at']:
        tip = ATTR_JP[a]
        if a in ('a-heavy', 'a-light'):
            if mode == 'kanji':
                out.append(f'<span class="kj {"hv" if a=="a-heavy" else "lt"}" data-tip="{tip}">'
                           f'{"重" if a=="a-heavy" else "軽"}</span>')
                continue
            if mode == 'badge':
                out.append(f'<span class="bdg {"on" if a=="a-heavy" else ""}" data-tip="{tip}">'
                           f'{ico("a-heavy" if a=="a-heavy" else "a-light")}</span>')
                continue
        cls = ''
        if mode == 'stroke':
            cls = 'sw-hv' if 'a-heavy' in u['at'] else ('sw-lt' if 'a-light' in u['at'] else '')
        out.append(f'<span class="at" data-tip="{tip}">{ico(a, cls)}</span>')
    return f'<div class="attrs">{"".join(out)}</div>'


def card(u, mode='kanji', big=False):
    w = u['w'] or {}
    rng = w.get('r1') if (w.get('r1') or 0) >= 1 else None
    atk = ATK_ICON.get(w.get('t'), 'i-melee')
    name = u['jp'] or u['n']
    if u['jp'] and u.get('prov'):
        name = f'<span class="prov" data-tip="仮訳 — 公式の日本語名は未確認">{name}</span>'
    sub = f'<span class="en">{u["n"]}</span>' if u['jp'] else ''

    def row(icon, val, tip):
        return f'<div class="r" data-tip="{tip}">{ico(icon)}<span class="v">{val}</span></div>'

    dps = w.get('dps')
    if w.get('s') and w['s'] < 0.5:   # 爆破船などの自爆は DPS 換算しても意味がない
        dps = None
    left = [row('i-hp', u['hp'] or '–', 'HP'),
            row(atk, w.get('d', '–'), f'攻撃力（{STAT_JP[atk]}）'),
            row('i-dps', dps if dps is not None else '–', 'DPS（自爆ユニットは出さない）'),
            row('i-int', w.get('s') or '–', '攻撃間隔（秒）')]
    if u.get('ch'):
        left.append(row('a-spear', u['ch']['d'], '突進（チャージ）攻撃の威力'))
    right = [row('i-range', rng or '–', '射程（–は近接）'),
             row('i-armm', u['am'], '近接防御'),
             row('i-armr', u['ar'], '遠隔防御'),
             row('i-speed', u['mv'] if u['mv'] is not None else '–', '移動速度')]
    bo = ''
    for b in (u.get('bo') or []):
        icons = ''.join(
            f'<span class="kj {"hv" if c=="heavy" else "lt"}">{"重" if c=="heavy" else "軽"}</span>'
            if c in ('heavy', 'light') else ico(CLASS_ICON.get(c, 'a-inf'))
            for c in b['c'])
        tip = '対 ' + '・'.join(ATTR_JP.get(CLASS_ICON.get(c, ''), c) for c in b['c']) + f' +{b["v"]}'
        bo += f'<span class="bo up" data-tip="{tip}">+{b["v"]}{icons}</span>'
    bo = f'<div class="bonus">{bo}</div>' if bo else ''

    costs = [(k, c, lbl) for k, c, lbl in (('f', 'i-food', '食料'), ('wd', 'i-wood', '木材'),
                                           ('g', 'i-gold', '金'), ('st', 'i-stone', '石')) if u[k]]
    tip = (' / '.join(f'{lbl} {u[k]}' for k, _, lbl in costs) or '資源内訳なし') + f' / 合計 {u["tot"]}'
    cost_html = (''.join(f'<span class="c r-{k}">{ico(c)}{u[k]}</span>' for k, c, _ in costs)
                 if costs else f'<span class="c r-g">{ico("i-gold")}{u["tot"]}</span>')
    return f'''<div class="card a{u['a']}{' big' if big else ''}">
  <div class="hd"><img src="{IMG_BASE}{u['ic']}" alt=""><div class="nm">{name}{sub}</div>
    <div class="age">{ROMAN[u['a']]}</div></div>
  {attr_row(u, mode)}
  <div class="body"><div class="col">{''.join(left)}</div><div class="col">{''.join(right)}</div></div>
  {bo}
  <div class="ft up" data-tip="{tip}">{cost_html}<span class="sp"></span>
    <span class="c dim">{ico('i-time')}{u['bt']}</span><span class="c dim">{ico('i-pop')}{u['pop']}</span></div>
</div>'''



CSS = r'''
:root{--bg:#100e0b;--card:#1b1713;--card2:#231d17;--line:#3a3128;--fg:#efe7da;--dim:#9b8e79;
--gold:#d8b06a;--a1:#7fae98;--a2:#78a3d4;--a3:#bf90da;--a4:#dfae5c;
--food:#e08a70;--wood:#9ec27a;--gold2:#e0c469;--stone:#93a0ab}
*{box-sizing:border-box}
body{margin:0;padding:24px 26px;background:var(--bg);color:var(--fg);font-size:13px;
font-family:"Segoe UI","Hiragino Kaku Gothic ProN","Noto Sans JP",system-ui,sans-serif;
font-variant-numeric:tabular-nums}
h2{font-size:12px;color:var(--gold);letter-spacing:.14em;margin:0 0 12px;font-weight:600}
h2 small{color:var(--dim);letter-spacing:0;font-weight:400;margin-left:10px}
.sec{margin-bottom:30px}
.row{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-start}
.ic{width:13px;height:13px;flex:none;fill:none;stroke:currentColor;stroke-width:2;
stroke-linecap:round;stroke-linejoin:round;viewBox:0 0 24 24}
svg.ic{width:13px;height:13px}
.card{width:208px;background:var(--card);border:1px solid var(--line);border-radius:9px}
.a1{border-top:2px solid var(--a1)}.a2{border-top:2px solid var(--a2)}
.a3{border-top:2px solid var(--a3)}.a4{border-top:2px solid var(--a4)}
.card .hd{display:flex;align-items:center;gap:6px;padding:6px 7px;background:var(--card2);
border-radius:8px 8px 0 0}
.card .hd img{width:30px;height:30px;border-radius:5px;flex:none;background:#0d0b09}
.card .nm{flex:1;min-width:0;font-weight:700;color:#fff;font-size:12.5px;line-height:1.2;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card .en{display:block;color:var(--dim);font-weight:400;font-size:9px;line-height:1.25;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card .age{flex:none;width:19px;height:19px;line-height:19px;text-align:center;border-radius:50%;
font-size:9.5px;font-weight:700;color:#17130f}
.a1 .age{background:var(--a1)}.a2 .age{background:var(--a2)}.a3 .age{background:var(--a3)}.a4 .age{background:var(--a4)}
.attrs{display:flex;align-items:center;gap:5px;padding:4px 8px;background:#191512;
border-top:1px solid #2b241d;border-bottom:1px solid #2b241d;color:var(--gold);flex-wrap:wrap}
.attrs .at{display:inline-flex}
.attrs svg.ic{width:14px;height:14px}
.sw-hv{stroke-width:3.2} .sw-lt{stroke-width:1.3}
.kj{font-size:10px;line-height:1.35;padding:0 3px;border-radius:3px;font-weight:700}
.kj.hv,.kj{background:var(--gold);color:#1d1710}
.kj.lt{background:none;color:var(--dim);border:1px solid var(--line);font-weight:400}
.bdg{display:inline-flex;padding:1px;border-radius:3px;border:1px solid var(--gold);color:var(--gold)}
.bdg.on{background:var(--gold);color:#1d1710}
.card .body{display:grid;grid-template-columns:1fr 1fr}
.card .col{padding:4px 0} .card .col+.col{border-left:1px solid #2b241d}
.card .r{display:flex;align-items:center;gap:5px;padding:2px 8px}
.card .r .ic{color:var(--dim)}
.card .v{font-weight:600;font-size:12.5px;margin-left:auto}
.bonus{display:flex;flex-wrap:wrap;gap:5px 11px;padding:6px 8px;border-top:1px solid #2b241d;
background:#1e1912}
.bo{display:inline-flex;align-items:center;gap:4px;color:var(--gold2,#f0d49a);
font-size:13px;font-weight:700;line-height:1.2}
.bo svg.ic{width:17px;height:17px;color:var(--gold)}
.bo .kj{font-size:11px;padding:0 3px;line-height:1.3}
.card .ft{display:flex;align-items:center;gap:8px;padding:5px 8px;border-top:1px solid #2b241d;
background:#171310;font-size:12px;border-radius:0 0 8px 8px}
.card .ft .sp{flex:1}
.card .c{display:inline-flex;align-items:center;gap:3px;font-weight:600}
.card .c.dim{color:var(--dim);font-weight:400;font-size:11px}
.r-f .ic{color:var(--food)}.r-wd .ic{color:var(--wood)}
.r-g .ic{color:var(--gold2)}.r-st .ic{color:var(--stone)}
.card.big .hd img{width:46px;height:46px}
.zoom{transform:scale(2.1);transform-origin:top left;width:208px}
.zwrap{display:flex;gap:18px;margin-bottom:14px}
.zcol{width:410px;height:430px} .zcol h3{font-size:12px;color:var(--gold);margin:0 0 8px;font-weight:600}
.lgwrap{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:7px 14px;max-width:900px;
background:var(--card);border:1px solid var(--line);border-radius:9px;padding:12px 14px}
.lg{display:flex;align-items:center;gap:7px;color:var(--dim);font-size:11.5px}
.lg .ic{width:15px;height:15px;color:var(--gold)}
.prov{border-bottom:1px dotted var(--dim)}
/* ---- ツールチップ（待ち時間なし・大きめ） ---- */
[data-tip]{position:relative}
[data-tip]:hover{z-index:120}
[data-tip]:hover::after{
 content:attr(data-tip);position:absolute;left:0;top:calc(100% + 5px);
 background:#2f2820;color:#f7f1e6;border:1px solid var(--gold);border-radius:7px;
 padding:6px 11px;font-size:14px;font-weight:500;line-height:1.35;letter-spacing:.02em;
 white-space:nowrap;pointer-events:none;z-index:200;box-shadow:0 6px 18px #000b}
[data-tip].up:hover::after{top:auto;bottom:calc(100% + 5px)}
.card .r[data-tip]:hover::after{left:4px}
.attrs [data-tip]:hover::after{left:-2px}

/* ================= 印刷（A4横） ================= */
@page{size:A4 landscape;margin:8mm}
@media print{
 :root{--bg:#fff;--card:#fff;--card2:#f4efe6;--line:#a99b84;--fg:#191510;--dim:#5b5344;
  --gold:#7a5a1e;--gold2:#5a4212;--a1:#3f7d64;--a2:#35608f;--a3:#6f458c;--a4:#8f6512;
  --food:#b04a2c;--wood:#4d7a2e;--stone:#4d5a66}
 body{background:#fff;color:#191510;padding:0;font-size:12px}
 .noprint{display:none !important}
 a{color:#191510;text-decoration:none}
 .card{break-inside:avoid;page-break-inside:avoid;border-color:#b5a68e;box-shadow:none}
 .card .hd{background:#f0e9dd}
 .card .hd img{background:#231e16}
 .card .nm,.card .v{color:#000}
 .attrs{background:#f7f2e9;border-color:#cdc0a8}
 .bonus{background:#fbf5e9;border-color:#cdc0a8}
 .card .ft{background:#f7f2e9;border-color:#cdc0a8}
 .card .col+.col{border-color:#d8ccb5}
 .card .r .ic{color:#5b5344}
 .kj{background:#7a5a1e;color:#fff}
 .kj.lt{background:#fff;color:#3d372c;border-color:#8a7c66}
 [data-tip]:hover::after{display:none !important}
 .lgwrap{border-color:#b5a68e;break-inside:avoid}
 h1,h2{color:#4a3609}
}
.disc{margin-top:26px;padding-top:12px;border-top:1px solid var(--line);
color:var(--dim);font-size:10.5px;line-height:1.7}
.disc a{color:var(--gold)}
.note{color:var(--dim);font-size:11.5px;line-height:1.7;margin-top:8px;max-width:900px}
'''
