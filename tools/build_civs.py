# -*- coding: utf-8 -*-
"""各文明の「特性」と「固有テクノロジー」を集めて data/civs.json を作る。

    python3 tools/build_civs.py [ゲームのインストール先]

構造（どの文明の固有技術か・時代・コスト・研究施設）は upstream の
aoe4world/data から。**表記はゲーム本体から取る**（ユニット名と同じ方針）。

1. テクノロジー名は `Attrib.sga` の `attrib\\upgrade\\**\\*.rgd` を開いて
   `ui_info.screen_name` の文字列IDを読み、各言語の `Locale*.sga` で引く
2. 説明文は同じ rgd の `help_text_formatter.formatter`。ゲーム側のテンプレートは
   `%1%` のようなプレースホルダ入りなので、**英語テンプレートを upstream の
   解決済み英文に突き合わせて数値を取り出し**、各言語のテンプレートに埋める
3. 文明特性（ゲーム内の文明概要パネルの項目）は、upstream の overview の
   タイトル・本文を英語ロケールから引き当てて、同じIDの各言語版に差し替える

ゲーム側で引き当てられなかった文言は英語のまま出す（`f: 1` を付ける）。
勝手に訳さない。

出力:
  data/civs.json            構造（言語に依存しない部分）
  data/civs-i18n/<lang>.json  文明特性・テクノロジーの各言語の文字列
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sga import Sga, read_rgd            # noqa: E402
from extract_locale import read_ucs, LOCALES, find_game_dir  # noqa: E402

AGES = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}

# 表示するコストの種類。silver はマケドニア朝、vizier はオスマン固有
COST_KEYS = ('food', 'wood', 'gold', 'stone', 'silver', 'vizier')
# ゲーム内の資源名（英語表記 → ロケールで引く）
TERMS = {'i-food': 'Food', 'i-wood': 'Wood', 'i-gold': 'Gold', 'i-stone': 'Stone',
         'i-silver': 'Silver', 'i-vizier': 'Vizier Points'}

# このページの UI 文言。ja / en 以外は en にフォールバックする（units 側と同じ）
UI = {
    'ja': {
        'title': 'AoE4 文明特性とテクノロジー',
        'pickCiv': '文明を選ぶ', 'home': '文明一覧へ',
        'traits': '文明特性', 'techs': '固有テクノロジー',
        'techsOf': '固有テクノロジー（{n}件）',
        'ageN': '第 {n} 時代', 'noTechs': '固有テクノロジーはありません。',
        'buildings': '研究施設', 'all': 'すべて', 'none': 'なし',
        'print': '印刷（A4横）', 'time': '研究時間', 'sec': '{n}秒',
        'repeat': '全{all}段階', 'repeatAge': 'この時代で{n}回',
        'free': '無償', 'units': 'ユニット一覧', 'maps': 'ランクマップ',
        'note': 'テクノロジーの効果はゲーム内の説明文そのまま。'
                '数値が説明文に出てこない効果は書かれていないことがある。',
        'enOnly': 'ゲーム内の対応する文言が見つからなかったので英語のまま',
        'report': '間違いを報告',
        'report.title': '[データ] {civ}: ',
        'report.body': '## 何が違っていたか\n\n'
                       '（特性名 / テクノロジー名 / このサイトの内容 → ゲーム内の内容 の順で'
                       '書いてもらえると助かります）\n\n\n'
                       '## スクリーンショット（あれば）\n\n\n'
                       '## 環境\n\n- 文明: {civ} (`{code}`)\n- 見ていたページ: {url}\n'
                       '- 対応パッチ: {patch}\n- 表示言語: {lang}\n',
    },
    'en': {
        'title': 'AoE4 Civilization Bonuses & Technologies',
        'pickCiv': 'Pick a civilization', 'home': 'All civilizations',
        'traits': 'Civilization Bonuses', 'techs': 'Unique Technologies',
        'techsOf': 'Unique Technologies ({n})',
        'ageN': 'Age {n}', 'noTechs': 'No unique technologies.',
        'buildings': 'Researched at', 'all': 'All', 'none': 'None',
        'print': 'Print (A4 landscape)', 'time': 'Research time', 'sec': '{n}s',
        'repeat': '{all} tiers total', 'repeatAge': '{n} in this Age',
        'free': 'Free', 'units': 'Units', 'maps': 'Ranked maps',
        'note': 'Effects are the in-game tooltips as-is. '
                'Numbers that the tooltip omits are not shown here either.',
        'enOnly': 'No matching in-game string was found, so this is left in English',
        'report': 'Report an error',
        'report.title': '[data] {civ}: ',
        'report.body': '## What was wrong\n\n'
                       '(bonus / technology name, what this site says, what the game says)\n\n\n'
                       '## Screenshot (if any)\n\n\n'
                       '## Environment\n\n- Civilization: {civ} (`{code}`)\n- Page: {url}\n'
                       '- Patch: {patch}\n- Language: {lang}\n',
    },
}


# ---------------------------------------------------------------- 文字列の突き合わせ

def norm(s):
    """ロケールの生文字列と upstream の文章を比べられる形に均す"""
    s = (s or '').replace('\\r\\n', '\n').replace('\r\n', '\n').replace('\\n', '\n')
    s = re.sub(r'\n+', '\n', s)
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()


def loose(s):
    """突き合わせ用。符号やダッシュの揺れは無視する"""
    return s.replace('+', '').replace('—', '-').replace('–', '-').replace('’', "'")


PH = re.compile(r'%\d+%')
# 「20」「1.5」「20/25/30/30」のような数値。読点だけを拾わないよう必ず数字で始める
NUM = r'(-?\d+(?:[.,/]\d+)*)'
# upstream 側だけに付く「Level 3 option」のような見出し行
LEVEL = re.compile(r'^Level \d+ option\s*', re.I)


def to_regex(tmpl):
    out = ''
    for p in re.split(r'(%\d+%|%%)', tmpl):
        if PH.fullmatch(p):
            out += NUM
        elif p == '%%':
            out += '%'
        else:
            out += re.escape(p)
    return out


def fill(tmpl, values):
    """%1% … を values（1始まり）で埋める。%% は素の % に戻す"""
    def rep(m):
        i = int(m.group(0).strip('%'))
        return values.get(i, m.group(0))
    return PH.sub(rep, tmpl).replace('%%', '%')


def extract_values(tmpl_en, resolved_en, args):
    """英語テンプレートと解決済みの英文を突き合わせて %N% の中身を取り出す。

    upstream 側の文章はゲームのテンプレートと完全一致しないことがある
    （語尾の句点が無い、頭に "Level 3 option" が付く、言い回しが古いなど）ので、
    厳密な突き合わせ → 地の文を順に探す → 数字の並びで当てる、の順に試す。
    プレースホルダの番号は %1% から始まるとは限らないので、出現順に対応づける。
    """
    slots = [int(p.strip('%')) for p in PH.findall(tmpl_en)]
    if not slots:
        return {}
    n = len(slots)

    def pair(vals):
        return {slot: v for slot, v in zip(slots, vals)}

    if resolved_en:
        tmpl = loose(norm(tmpl_en))
        target = LEVEL.sub('', loose(norm(resolved_en)))
        rx = to_regex(tmpl)
        m = re.match('^' + rx + r'\.?$', target) or re.match('^' + rx, target)
        if m and len(m.groups()) == n:
            return pair(m.groups())
        # 地の文を順に探して、その直後の数字を拾う
        segs = PH.split(tmpl)
        vals, pos, ok = [], 0, True
        for seg in segs[:-1]:
            seg = seg.replace('%%', '%').rstrip('.')
            at = target.find(seg, pos) if seg.strip() else pos
            if at < 0:
                ok = False
                break
            pos = at + len(seg)
            m = re.match(r'\s*' + NUM, target[pos:])
            if not m:
                ok = False
                break
            vals.append(m.group(1))
            pos += m.end()
        if ok and len(vals) == n:
            return pair(vals)
        # 最後の手段。言い回しが変わっていても数値の並び順は変わらないので、
        # 出てくる数字の個数がプレースホルダの数とちょうど同じなら順に当てる
        nums = re.findall(NUM, target)
        if len(nums) == n:
            return pair(nums)
    # 突き合わせできないときは、rgd に入っている引数で埋められる分だけ埋める
    v = args.get('int_value', args.get('float_value'))
    if n == 1 and v is not None:
        v = int(v) if float(v) == int(v) else v
        return pair([str(v)])
    return None


class Locale:
    """全言語のロケールと、英語文字列 → ID の逆引き"""

    def __init__(self, arch):
        self.tbl = {}
        for lang, loc in LOCALES.items():
            p = os.path.join(arch, f'Locale{loc}.sga')
            if os.path.exists(p):
                self.tbl[lang] = read_ucs(p)
                print(f'  {lang:8} {len(self.tbl[lang])} strings')
        self.en = self.tbl['en']
        self.exact = {}
        self.all_ids = {}
        self.tmpl = []
        for k, v in self.en.items():
            n = norm(v)
            self.exact.setdefault(n, k)
            self.all_ids.setdefault(n, []).append(k)
            if '%' in n and len(n) > 12:
                try:
                    self.tmpl.append((k, re.compile('^' + to_regex(loose(n)) + r'\.?$')))
                except re.error:
                    pass

    def find(self, text):
        """英文からロケールの文字列IDを探す。テンプレートなら値も返す"""
        n = norm(text)
        if n in self.exact:
            return self.exact[n], {}
        t = loose(n)
        for k, rx in self.tmpl:
            m = rx.match(t)
            if m:
                return k, {i + 1: g for i, g in enumerate(m.groups())}
        return None, None

    def term(self, text):
        """同じ英語に複数IDがあるので、訳が一番多いものを採る（extract_locale と同じ）"""
        ids = self.all_ids.get(norm(text), [])
        out = {}
        for lang, tbl in self.tbl.items():
            vals = [tbl[i] for i in ids if tbl.get(i)]
            if vals:
                out[lang] = max(set(vals), key=vals.count)
        return out

    def neighbour_text(self, sid):
        """タイトルのIDの隣にある、説明文らしい文字列を拾う"""
        for i in (sid - 1, sid + 1):
            v = self.en.get(i)
            if v and len(norm(v)) > 40 and not PH.search(norm(v)) and not norm(v).startswith('•'):
                return self.by_id(i, {})
        return {}

    def by_id(self, sid, values=None):
        """文字列ID → {lang: 文字列}。値があれば %N% を埋める"""
        out = {}
        for lang, tbl in self.tbl.items():
            s = tbl.get(sid)
            if not s:
                continue
            s = norm(s)
            if PH.search(s):
                if values is None:
                    continue
                s = fill(s, values)
                if PH.search(s):
                    continue          # 埋め残し。中途半端に出すより英語のままにする
            else:
                s = s.replace('%%', '%')
            out[lang] = s
        return out


# ---------------------------------------------------------------- 収集

def upgrade_index(sga):
    """attribName → rgd のパス。attrib\\upgrade を優先し、無いものは他も見る
    （ジャンヌ・ダルクの能力選択は ebps の codex_dummy に入っている）"""
    idx, other = {}, {}
    for n in sga.names():
        if not n.endswith('.rgd'):
            continue
        base = os.path.basename(n)[:-4]
        (idx if n.startswith('attrib\\upgrade') else other).setdefault(base, []).append(n)
    for base, paths in other.items():
        idx.setdefault(base, paths)
    return idx


def ui_info(sga, path):
    """rgd から表示用の情報（screen_name / help_text_formatter）を取り出す。

    置き場所が種類ごとに違う（upgrade は `upgrade_bag/ui_info`、能力は
    `ability_bag/ui_info`、codex の見出しは `ui_ext`）ので、
    `screen_name` を持つ最初の辞書を拾う。
    """
    def walk(o):
        if not isinstance(o, dict):
            return None
        if 'screen_name' in o:
            return o
        for v in o.values():
            hit = walk(v)
            if hit:
                return hit
        return None
    return walk(read_rgd(sga.read(path))) or {}


REPEAT = re.compile(r'\s*\((\d+)/(\d+)\)\s*$')
# 「Castle Age King」のように、時代到達で自動的に付くだけで研究できないもの
AUTO = re.compile(r'^(Dark|Feudal|Castle|Imperial) Age ')


def researchable(t):
    if AUTO.match(t['name']) and not t.get('producedBy') and not (t.get('costs') or {}).get('total'):
        return False
    return True


def collapse_repeats(techs):
    """「Blade Inlaying (1/6)」のような段階研究を、時代ごとに1件へまとめる。

    マケドニア朝のヴァリャーグ造兵廠の技術は全6段階で、第II・III・IV時代に
    2回ずつ研究する。段階ごとに別IDだが名前も効果も同じなので、
    「この時代で2回」「全6段階」として1行にする。
    """
    out, seen = [], {}
    for t in techs:
        m = REPEAT.search(t['name'])
        if not m:
            out.append(t)
            continue
        base = (REPEAT.sub('', t['name']), t['age'])
        if base in seen:
            seen[base]['repeatAge'] += 1
            continue
        t = dict(t, name=REPEAT.sub('', t['name']), repeatAge=1,
                 repeatAll=int(m.group(2)))
        seen[base] = t
        out.append(t)
    return out


def unique_filter(techs_all):
    """「固有テクノロジー」の判定を作る。

    upstream の `unique` フラグだけだと、アッバース朝／アイユーブの知恵の館の
    ウィング技術のように**その文明にしか無いのにフラグが立っていない**ものが
    こぼれる。逆に、ファランクス（ビザンティン＋マケドニア朝）のように
    **派生文明と共有していてフラグだけ立っている**ものもある。
    そこで「フラグが立っている」か「その技術を持つ文明が1つだけ」の
    どちらかを満たすものを固有として扱う。
    """
    owners = collections.defaultdict(set)
    for t in techs_all:
        owners[t['baseId']].add(t['civs'][0])
    return lambda t: bool(t.get('unique')) or len(owners[t['baseId']]) == 1


def main():
    game = find_game_dir(sys.argv)
    if not game:
        sys.exit('ゲームのインストール先が見つからない。引数で渡してください。')
    arch = os.path.join(game, 'cardinal', 'archives')
    print('game:', game)

    civs_index = json.load(open(os.path.join(ROOT, 'data', 'civs-index.json')))
    meta = json.load(open(os.path.join(ROOT, 'data', 'meta.json')))
    techs_all = json.load(open(os.path.join(ROOT, 'data', 'technologies-all.json')))['data']
    is_unique = unique_filter(techs_all)

    print('locales:')
    loc = Locale(arch)
    sga = Sga(os.path.join(arch, 'Attrib.sga'))
    upg = upgrade_index(sga)
    print(f'Attrib.sga: {len(upg)} upgrades')

    out = {
        'source': 'https://github.com/aoe4world/data',
        'patch': meta.get('patch'),
        'langs': meta.get('langs'),
        'civs': {},
    }
    strings = {lang: {'civDesc': {}, 'traits': {}, 'techs': {}, 'terms': {}}
               for lang in loc.tbl}
    for key, word in TERMS.items():
        for lang, v in loc.term(word).items():
            strings[lang]['terms'][key] = v
    stat = {'traitOk': 0, 'traitEn': 0, 'techOk': 0, 'techEn': 0}

    for code, ci in civs_index.items():
        ov = json.load(open(os.path.join(ROOT, 'data', 'civ-overviews', f'{ci["slug"]}.json')))

        # --- 文明の短い説明（racebps） ---
        try:
            rb = read_rgd(sga.read(f'attrib\\racebps/{ci["attribName"]}.rgd'))
            did = rb['default']['race_bag'].get('description')
            for lang, s in loc.by_id(did, {}).items():
                strings[lang]['civDesc'][code] = s
        except Exception as e:
            print(f'  ! {code}: racebps 読めず ({e})')
        for lang in strings:
            strings[lang]['civDesc'].setdefault(code, ov.get('description', ''))

        # --- 文明特性 ---
        traits = []
        for i, o in enumerate(ov.get('overview', [])):
            if 'description' not in o:
                continue          # 箇条書きのまとめ（Civilization Bonuses）は下の項目と重複する
            key = f'{code}-{i}'
            raw = o['description']
            if 'translation not found' in raw:
                raw = ''      # upstream 側の翻訳漏れ。そのまま出しても意味が無い
            tid, _ = loc.find(o['title'])
            did, vals = loc.find(raw) if raw else (None, None)
            title = loc.by_id(tid, {}) if tid else {}
            desc = loc.by_id(did, vals) if did else {}
            if not desc and not raw and tid:
                # upstream 側が説明文を丸ごと持っていないことがある（翻訳漏れ）。
                # 文明概要の項目は「説明文のID → タイトルのID」と続けて並んでいるので、
                # タイトルの隣を見て、それらしい長さの文があれば採る。
                # **upstream に文章がある場合には使わない**（隣が別項目の説明文のことがあり、
                # 突き合わせる相手が無いと正しさを確かめられないため）。
                near = loc.neighbour_text(tid)
                if near:
                    desc = near
                    print(f'    {code}: 「{o["title"]}」の説明文をIDの隣から拾った')
            fallback = not desc
            if fallback:
                stat['traitEn'] += 1
            else:
                stat['traitOk'] += 1
            for lang in strings:
                strings[lang]['traits'][key] = {
                    't': title.get(lang) or o['title'],
                    'd': desc.get(lang) or norm(raw),
                }
            traits.append({'k': key, 'f': 1} if fallback else {'k': key})

        # --- 固有テクノロジー ---
        mine = collapse_repeats([t for t in techs_all
                                 if t.get('civs') == [code] and is_unique(t)
                                 and researchable(t)])
        rows = []
        for t in sorted(mine, key=lambda x: (x['age'], x['name'])):
            an = t['attribName']
            paths = upg.get(an)
            name, desc, fallback = {}, {}, True
            if paths:
                ui = ui_info(sga, paths[0])
                sn = ui.get('screen_name')
                if sn:
                    name = loc.by_id(sn, {})
                htf = ui.get('help_text_formatter') or {}
                fid = htf.get('formatter') or ui.get('help_text')
                tmpl_en = loc.en.get(fid)
                if tmpl_en:
                    vals = extract_values(tmpl_en, t.get('description'),
                                          htf.get('formatter_arguments') or {})
                    if vals is not None:
                        desc = loc.by_id(fid, vals)
                        fallback = False
            if not name:
                sid, _ = loc.find(t['name'])
                if sid:
                    name = loc.by_id(sid, {})
            if fallback and t.get('description'):
                sid, vals = loc.find(t['description'])
                if sid:
                    desc = loc.by_id(sid, vals)
                    fallback = not desc
            if fallback:
                stat['techEn'] += 1
            else:
                stat['techOk'] += 1
            for lang in strings:
                strings[lang]['techs'][an] = {
                    'n': name.get(lang) or t['name'],
                    'd': desc.get(lang) or norm(t.get('description')),
                }
            c = t.get('costs') or {}
            row = {
                'k': an, 'id': t['id'], 'age': t['age'],
                'cost': {k: c[k] for k in COST_KEYS if c.get(k)},
                'time': c.get('time') or 0,
                'from': t.get('producedBy') or [],
                'icon': f'assets/techs/{t["id"]}.png',
            }
            if t.get('repeatAge'):
                row['rep'] = t['repeatAge']
                row['repAll'] = t['repeatAll']
            if fallback:
                row['f'] = 1
            rows.append(row)

        out['civs'][code] = {
            'flag': (meta['civs'].get(code) or {}).get('flag', f'assets/flags/{code}.png'),
            'en': (meta['civs'].get(code) or {}).get('en', ci['name']),
            'traits': traits,
            'techs': rows,
        }
        print(f'  {code:4} {ci["slug"]:18} 特性 {len(traits):2}  固有技術 {len(rows):2}')

    os.makedirs(os.path.join(ROOT, 'data', 'civs-i18n'), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, 'data', 'civs.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, sort_keys=True)
    for lang, s in strings.items():
        s['ui'] = UI.get(lang, UI['en'])
        s['uiIsFallback'] = lang not in UI
        json.dump(s, open(os.path.join(ROOT, 'data', 'civs-i18n', f'{lang}.json'),
                          'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)

    n_tech = sum(len(c['techs']) for c in out['civs'].values())
    n_trait = sum(len(c['traits']) for c in out['civs'].values())
    print(f'\ncivs.json : {len(out["civs"])} civs, 特性 {n_trait}, 固有技術 {n_tech}')
    print(f'  ゲーム内の文言で出せたもの: 特性 {stat["traitOk"]}/{n_trait}, '
          f'技術 {stat["techOk"]}/{n_tech}')
    if stat['traitEn'] or stat['techEn']:
        print(f'  英語のまま: 特性 {stat["traitEn"]}, 技術 {stat["techEn"]}')


if __name__ == '__main__':
    main()
