# -*- coding: utf-8 -*-
"""ランクマッププールと、各マップの資源配置を集めて data/maps.json を作る。

AoE4 のランクマップは 2026-07-02 以降、**毎月1日に自動でローテーション**する。
パッチノートに「今月はこれ」という告知が出ないので、公式発表を追う方法が無い。
そこで進行中の対戦を実際にサンプリングして、今どのマップが回っているかを数える。

    python3 tools/build_maps.py [ゲームのインストール先]

やっていること:

1. aoe4world の対戦APIから直近の試合を拾い、`leaderboard` が rm_solo / rm_team の
   ものだけマップ名で集計する → これが今月のプール
2. 各マップの資源データを Age of Empires Series Wiki の MediaWiki API から取る。
   `Infobox AoE4 map` に 聖地・集落交易所・聖遺物・羊・鹿・イノシシ・果実・金・石 が入っていて、
   数値は `a/b/c/d` = 1v1/2v2/3v3/4v4 の形式。1v1とチーム戦の差がそのまま取れる
3. 資源配置のサンプル画像（`AoE4 <Map> 1p2p Map Spawns.png`）を落として、
   上半分（＝1v1の生成例2つ）だけ切り出して assets/maps/ に置く
4. マップ名の日本語表記は、ユニット名と同じくゲーム本体のロケールから取る
   （extract_locale.py と同じ仕組み。ゲームが無ければ既存の data/maps.json の値を使い回す）
5. tools/maps-notes.ja.json の手書き解説をマージする

出力: data/maps.json, assets/maps/<slug>-1v1.jpg
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {'User-Agent': 'aoe4units/1.0 (+https://github.com/yousan/aoe4units) map data builder'}

WIKI = 'https://ageofempires.fandom.com/api.php'
GAMES = 'https://aoe4world.com/api/v0/games'

# 鹿の群れサイズ（頭数）。ゲーム内の生成タグに対応する
HERD = {'micro': 2, 'small': 3, 'medium': 5, 'large': 7, 'extra large': 10}
SIZES = ['1v1', '2v2', '3v3', '4v4']
PLAYERS = {'1v1': 2, '2v2': 4, '3v3': 6, '4v4': 8}

# infobox のキー → data/maps.json でのキー
FIELDS = [
    ('SacredSites', 'sacredSites'), ('TradePosts', 'tradePosts'), ('Relics', 'relics'),
    ('Sheep', 'sheep'), ('Deer', 'deer'), ('Boar', 'boar'), ('Berries', 'berries'),
    ('Gold', 'gold'), ('Stone', 'stone'), ('Features', 'features'),
]


def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def get(url, binary=False, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                data = r.read()
            return data if binary else json.loads(data)
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))
            print(f'    retry ({e})')


# ---------------------------------------------------------------- 1. プール

def current_pool(pages=40):
    """進行中／直近の対戦をサンプリングして、今回っているマップを数える"""
    pool = {'rm_solo': {}, 'rm_team': {}}
    seen = set()
    for p in range(1, pages + 1):
        try:
            d = get(f'{GAMES}?limit=50&page={p}')
        except Exception as e:
            print(f'  page {p}: {e}')
            break
        games = d.get('games', [])
        if not games:
            break
        for g in games:
            if g['game_id'] in seen:
                continue
            seen.add(g['game_id'])
            lb = g.get('leaderboard')
            if lb in pool and g.get('map'):
                pool[lb][g['map']] = pool[lb].get(g['map'], 0) + 1
        time.sleep(0.2)
    for lb, c in pool.items():
        print(f'  {lb}: {sum(c.values())} 試合 / {len(c)} マップ')
    return {lb: dict(sorted(c.items(), key=lambda kv: -kv[1])) for lb, c in pool.items()}


# ---------------------------------------------------------------- 2. wiki

def wikitext(page):
    q = urllib.parse.urlencode({'action': 'parse', 'page': page, 'prop': 'wikitext',
                                'format': 'json', 'formatversion': '2'})
    d = get(f'{WIKI}?{q}')
    return d.get('parse', {}).get('wikitext', '')


def clean(v):
    """{{tt|表示|注釈}} は表示側だけ、リンクや小タグは落とす"""
    v = re.sub(r'\{\{tt\|([^|}]*)\|[^}]*\}\}', r'\1', v)
    v = re.sub(r'\[\[[^|\]]*\|([^\]]*)\]\]', r'\1', v)
    v = re.sub(r'\[\[([^\]]*)\]\]', r'\1', v)
    v = re.sub(r'<small>|</small>', '', v)
    v = re.sub(r'<br\s*/?>', ' / ', v)
    v = re.sub(r'<[^>]+>', ' ', v)
    return re.sub(r'\s+', ' ', v).strip(' /').strip()


def infobox(wt):
    if 'Infobox AoE4 map' not in wt:
        return {}
    body = wt.split('Infobox AoE4 map', 1)[1].split('\n}}', 1)[0]
    out = {}
    for line in body.split('\n|')[1:]:
        if '=' in line:
            k, v = line.split('=', 1)
            out[k.strip()] = clean(v)
    return out


def prose(wt, heading):
    if heading not in wt:
        return ''
    return clean(wt.split(heading, 1)[1].split('\n== ', 1)[0])


def slash4(s):
    """'20/38/56/74' → {'1v1':20,...}。無ければ None"""
    m = re.search(r'\b(\d+)/(\d+)/(\d+)/(\d+)\b', s or '')
    if not m:
        return None
    return dict(zip(SIZES, (int(x) for x in m.groups())))


def per_player(s):
    """'2 per player' / '12 per player' → 1人あたりの数"""
    m = re.search(r'(\d+)\s*(?:per player|/人)', s or '')
    return int(m.group(1)) if m else None


def count_for(s, size):
    """4値表記なら該当サイズ、per player 表記なら人数倍、単独の数字ならそのまま"""
    if not s:
        return None
    four = slash4(s)
    if four:
        return four[size]
    pp = per_player(s)
    if pp is not None:
        return pp * PLAYERS[size]
    m = re.fullmatch(r'(\d+)', s.strip())
    return int(m.group(1)) if m else None


def parse_relics(s, size):
    """'Default: 3 Per player: 1' → 3 + 1×人数。'1 vs 1: 5 2 vs 2: 6' 形式にも対応"""
    m = re.search(rf'{size.replace("v", " vs ")}\s*:?\s*(\d+)', s or '', re.I)
    if m:
        return int(m.group(1))
    base = re.search(r'Default\s*:?\s*(\d+)', s or '', re.I)
    pp = re.search(r'Per player\s*:?\s*(\d+)', s or '', re.I)
    if base and pp:
        return int(base.group(1)) + int(pp.group(1)) * PLAYERS[size]
    return count_for(s, size)


def parse_deer(s, size):
    """'Large: 2 per player' / '2 large per player' / 'Medium: 3 per player Small: 2 per player'
    → [{size, herds, head}]。頭数まで出す"""
    if not s:
        return []
    out = []
    pat = (r'(micro|small|medium|large|extra large)\s*:?\s*(\d+)\s*(per player)?'
           r'|(\d+)\s*(micro|small|medium|large|extra large)\s*(per player)?')
    for m in re.finditer(pat, s, re.I):
        if m.group(1):
            sz, n, pp = m.group(1).lower(), int(m.group(2)), bool(m.group(3))
        else:
            sz, n, pp = m.group(5).lower(), int(m.group(4)), bool(m.group(6))
        herds = n * PLAYERS[size] if pp else n
        out.append({'size': sz, 'herds': herds, 'head': herds * HERD[sz]})
    if not out:
        four = slash4(s)
        if four:
            out.append({'size': 'large', 'herds': four[size], 'head': four[size] * HERD['large']})
    return out


# ---------------------------------------------------------------- 3. 画像

def spawn_image(name, dest):
    """1p2p の資源配置図を落として、上半分（1v1の生成例2つ）だけ切り出す"""
    title = f'File:AoE4 {name} 1p2p Map Spawns.png'
    q = urllib.parse.urlencode({'action': 'query', 'titles': title, 'prop': 'imageinfo',
                                'iiprop': 'url|size', 'format': 'json', 'formatversion': '2'})
    pages = get(f'{WIKI}?{q}').get('query', {}).get('pages', [])
    if not pages or 'imageinfo' not in pages[0]:
        return None
    ii = pages[0]['imageinfo'][0]
    url = ii['url'].split('/revision/')[0] + '/revision/latest/scale-to-width-down/1400'
    raw = get(url, binary=True)
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        w, h = im.size
        im.crop((0, 0, w, h // 2)).save(dest, 'JPEG', quality=86, optimize=True)
    except ImportError:
        print('    Pillow が無いので原寸のまま保存する（1v1の切り出しはされない）')
        dest = dest.replace('.jpg', '.png')
        open(dest, 'wb').write(raw)
    return os.path.relpath(dest, ROOT).replace(os.sep, '/')


# ---------------------------------------------------------------- 4. 日本語名

def jp_names(game, names):
    """ゲーム本体のロケールからマップ名の公式日本語表記を引く"""
    arch = os.path.join(game, 'cardinal', 'archives')
    if not os.path.isdir(arch):
        return {}
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from extract_locale import read_ucs, pick
    en = read_ucs(os.path.join(arch, 'LocaleEnglish.sga'))
    ja = read_ucs(os.path.join(arch, 'LocaleJapanese.sga'))
    rev = {}
    for k, v in en.items():
        rev.setdefault(v, []).append(k)
    return {n: pick(rev.get(n, []), ja) for n in names if pick(rev.get(n, []), ja)}


# ---------------------------------------------------------------- main

def main():
    game = sys.argv[1] if len(sys.argv) > 1 else None
    if not game:
        for d in ['/mnt/c/Program Files (x86)/Steam/steamapps/common/Age of Empires IV',
                  os.path.expanduser('~/.steam/steam/steamapps/common/Age of Empires IV')]:
            if os.path.isdir(os.path.join(d, 'cardinal', 'archives')):
                game = d
                break

    print('1. 今回っているマッププールを数える')
    pool = current_pool()
    names = list(pool['rm_solo']) + [m for m in pool['rm_team'] if m not in pool['rm_solo']]
    if not names:
        sys.exit('プールが取れなかった。aoe4world のAPIが落ちている可能性がある')

    prev = {}
    prev_path = os.path.join(ROOT, 'data', 'maps.json')
    if os.path.exists(prev_path):
        prev = json.load(open(prev_path, encoding='utf-8')).get('maps', {})

    print('2. wiki から資源データを取る')
    imgdir = os.path.join(ROOT, 'assets', 'maps')
    os.makedirs(imgdir, exist_ok=True)
    maps = {}
    for n in names:
        s = slug(n)
        try:
            wt = wikitext(n)
        except Exception as e:
            print(f'  {n}: 取得失敗 {e}')
            wt = ''
        ib = infobox(wt)
        raw = {key: ib.get(k, '') for k, key in FIELDS}
        rec = {
            'name': n,
            'slug': s,
            'raw': {k: v for k, v in raw.items() if v},
            'features': [f.strip() for f in re.split(r'\s*/\s*|\s{2,}', raw['features']) if f.strip()],
            'wiki': f'https://ageofempires.fandom.com/wiki/{urllib.parse.quote(n.replace(" ", "_"))}',
            'stub': 'Infobox AoE4 map' not in wt or not raw['sheep'],
            'prose': {'features': prose(wt, '== Features =='), 'resources': prose(wt, '== Resources ==')},
            'bySize': {},
        }
        for size in SIZES:
            deer = parse_deer(raw['deer'], size)
            rec['bySize'][size] = {
                'sacredSites': count_for(raw['sacredSites'], size),
                'tradePosts': count_for(raw['tradePosts'], size),
                'relics': parse_relics(raw['relics'], size),
                'sheep': count_for(raw['sheep'], size),
                'boar': count_for(raw['boar'], size),
                'deer': deer,
                'deerHead': sum(d['head'] for d in deer) or None,
            }
        img = os.path.join(imgdir, f'{s}-1v1.jpg')
        if os.path.exists(img):
            rec['img'] = f'assets/maps/{s}-1v1.jpg'
        else:
            try:
                rec['img'] = spawn_image(n, img)
            except Exception as e:
                print(f'  {n}: 画像取得失敗 {e}')
                rec['img'] = None
        flag = ' [stub]' if rec['stub'] else ''
        print(f'  {n:18} 聖地{rec["bySize"]["1v1"]["sacredSites"]} '
              f'聖遺物{rec["bySize"]["1v1"]["relics"]} 羊{rec["bySize"]["1v1"]["sheep"]} '
              f'鹿{rec["bySize"]["1v1"]["deerHead"]}頭 '
              f'{"画像あり" if rec["img"] else "画像なし"}{flag}')
        maps[s] = rec
        time.sleep(0.3)

    print('3. マップ名の日本語表記')
    ja = jp_names(game, names) if game else {}
    for s, rec in maps.items():
        rec['ja'] = ja.get(rec['name']) or prev.get(s, {}).get('ja')
    print(f'  {sum(1 for r in maps.values() if r["ja"])}/{len(maps)} 件'
          + ('（ゲーム本体から）' if ja else '（既存 data/maps.json から流用）'))

    notes = json.load(open(os.path.join(ROOT, 'tools', 'maps-notes.ja.json'), encoding='utf-8'))
    for s, rec in maps.items():
        rec['notes'] = notes['notes'].get(s, [])

    out = {
        'generated': time.strftime('%Y-%m-%d'),
        'rotation': time.strftime('%Y-%m'),
        'herdSizes': HERD,
        'pools': {'rm_solo': list(pool['rm_solo']), 'rm_team': list(pool['rm_team'])},
        'samples': pool,
        'sources': {
            'pool': 'https://aoe4world.com/api/v0/games',
            'stats': 'https://ageofempires.fandom.com/ (Age of Empires Series Wiki, CC BY-SA)',
            'names': 'ゲーム本体 cardinal/archives/Locale*.sga',
        },
        'maps': maps,
    }
    json.dump(out, open(prev_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\ndata/maps.json を書いた（{len(maps)} マップ）')


if __name__ == '__main__':
    main()
