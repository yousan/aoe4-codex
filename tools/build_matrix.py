# -*- coding: utf-8 -*-
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'units-all.json')
"""縦=時代 / 横=生産施設・ユニット系統 のマトリクス"""
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aoe4lib as L

CIV = sys.argv[1] if len(sys.argv) > 1 else 'od'
CIV_JP = {'od': ('ドラゴン騎士団', 'Order of the Dragon')}
civ_jp, civ_en = CIV_JP.get(CIV, (CIV, CIV))

COLS = [('barracks', '戦士育成所'), ('archery-range', '弓兵育成所'),
        ('stable', '騎兵育成所'), ('town-center', '町の中心')]
COL_SLUGS = [c for c, _ in COLS]
LANDMARK_JP = {'burgrave-palace': '城伯の宮殿', 'palace-of-swabia': 'シュヴァーベン宮',
               'regnitz-cathedral': 'レグニッツ大聖堂'}
TIERS = ('黎明', '初期', '熟練', '古参', '精鋭')


def primary(u):
    """町の中心は右端だが、割り当ての優先度は町の中心が先（農民・斥候のため）"""
    for slug in ['town-center'] + COL_SLUGS:
        if slug in u['pb']:
            return slug
    return None


def extras(u):
    out = [LANDMARK_JP.get(b, b) for b in u['pb']
           if b in LANDMARK_JP]
    return sorted(set(out))


def line_label(u):
    n = u['jp'] or u['n']
    for t in TIERS:
        if n.startswith(t):
            return n[len(t):]
    return n


units = [u for u in L.UNITS if CIV in u['cv'] and primary(u) in COL_SLUGS]
ages = sorted({u['a'] for u in units})

# 施設ごとの系統（サブ列）を、登場時代 → 名前 の順に並べる
sub = {}
for c, _ in COLS:
    us = [u for u in units if primary(u) == c]
    lines = {}
    for u in us:
        lines.setdefault(u['b'], []).append(u)
    order = sorted(lines, key=lambda b: (min(x['a'] for x in lines[b]),
                                         line_label(min(lines[b], key=lambda x: x['a']))))
    sub[c] = [(b, line_label(min(lines[b], key=lambda x: x['a'])), lines[b]) for b in order]

cell = {}
for c, _ in COLS:
    for b, _lbl, us in sub[c]:
        for u in us:
            cell[(u['a'], c, b)] = u

h1 = ''.join(f'<th class="bld" colspan="{len(sub[c])}">{jp}<span>{sum(len(x[2]) for x in sub[c])}</span></th>'
             for c, jp in COLS)
h2 = ''.join(f'<th class="ln">{lbl}</th>' for c, _ in COLS for _b, lbl, _us in sub[c])

rows = ''
for a in ages:
    tds = ''
    for ci, (c, _) in enumerate(COLS):
        for si, (b, _lbl, _us) in enumerate(sub[c]):
            u = cell.get((a, c, b))
            edge = ' bl' if si == 0 and ci > 0 else ''
            if u:
                ex = extras(u)
                tds += (f'<td class="{edge}">{L.card(u, "kanji")}'
                        f'{f"<div class=alt>＋ {chr(12539).join(ex)}</div>" if ex else ""}</td>')
            else:
                tds += f'<td class="{edge}"><span class="e">·</span></td>'
    rows += f'<tr><th class="age a{a}"><span>第</span>{L.ROMAN[a]}<span>時代</span></th>{tds}</tr>'

# 印刷用: 1施設 = 1ページ（A4横に収まる幅）
psecs = ''
for c, jp in COLS:
    if not sub[c]:
        continue
    ph = ''.join(f'<th class="ln">{lbl}</th>' for _b, lbl, _u in sub[c])
    prows = ''
    for a in ages:
        tds = ''
        for b, _lbl, _u in sub[c]:
            u = cell.get((a, c, b))
            if u:
                ex = extras(u)
                tds += (f'<td>{L.card(u, "kanji")}'
                        f'{f"<div class=alt>＋ {chr(12539).join(ex)}</div>" if ex else ""}</td>')
            else:
                tds += '<td><span class="e">·</span></td>'
        prows += f'<tr><th class="age a{a}"><span>第</span>{L.ROMAN[a]}<span>時代</span></th>{tds}</tr>'
    psecs += (f'<section class="psec"><h2 class="pt">{civ_jp} — {jp}</h2>'
              f'<table class="mx"><thead><tr><th class="corner age">時代</th>{ph}</tr></thead>'
              f'<tbody>{prows}</tbody></table></section>')

legend_attrs = ''.join(
    f'<div class="lg">{"<span class=kj>"+("重" if k=="a-heavy" else "軽")+"</span>" if k in ("a-heavy","a-light") else L.ico(k)}<span>{v}</span></div>'
    for k, v in L.ATTR_JP.items())
legend_stats = ''.join(f'<div class="lg">{L.ico(k)}<span>{v}</span></div>'
                       for k, v in L.STAT_JP.items() if k != 'i-fire')

HTML = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{civ_jp} 生産施設 × 時代 - AoE4</title><style>{L.CSS}
body{{padding:18px 20px}}
h1{{font-size:19px;color:#f0d49a;margin:0 0 3px;letter-spacing:.04em}}
h1 small{{font-size:12px;color:var(--dim);margin-left:10px;letter-spacing:0}}
.head{{margin-bottom:14px}}
.head p{{margin:5px 0 0;color:var(--dim);font-size:11.5px;line-height:1.7}}
.head a{{color:var(--gold)}}
.mxwrap{{overflow:auto;border:1px solid var(--line);border-radius:10px;background:#141210}}
table.mx{{border-collapse:separate;border-spacing:0}}
table.mx th{{white-space:nowrap;text-align:left;background:#26201a;color:var(--gold)}}
th.bld{{position:sticky;top:0;z-index:22;font-size:12.5px;font-weight:600;padding:8px 10px;
 border-bottom:1px solid var(--line);border-right:2px solid #100e0b}}
th.bld span{{color:var(--dim);font-weight:400;font-size:10.5px;margin-left:6px}}
th.ln{{position:sticky;top:33px;z-index:21;font-size:11px;font-weight:400;
 padding:5px 10px;background:#1f1a15;color:#cbbb9c;border-bottom:1px solid var(--line)}}
th.age{{position:sticky;left:0;z-index:25;background:#1d1813;color:#fff;font-size:15px;
 text-align:center;width:54px;min-width:54px;border-right:1px solid var(--line)}}
th.age span{{display:block;font-size:9.5px;color:var(--dim)}}
thead th.corner{{position:sticky;left:0;top:0;z-index:30;background:#26201a;
 border-right:1px solid var(--line);border-bottom:1px solid var(--line)}}
table.mx td{{vertical-align:top;padding:9px;border-bottom:1px solid #241e18;
 border-right:1px solid #241e18;min-width:226px}}
table.mx td.bl{{border-left:2px solid #100e0b}}
table.mx tbody tr:nth-child(odd) td{{background:#171411}}
.alt{{color:var(--dim);font-size:10px;margin:4px 0 0 2px;line-height:1.4}}
.e{{color:#3a332b}}
.a1.age{{border-left:3px solid var(--a1)}}.a2.age{{border-left:3px solid var(--a2)}}
.a3.age{{border-left:3px solid var(--a3)}}.a4.age{{border-left:3px solid var(--a4)}}
.sec{{margin-top:24px}}
.pbtn{{float:right;background:var(--gold);color:#1d1710;border:none;border-radius:7px;
 padding:7px 14px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit}}
.pbtn:hover{{background:var(--gold2,#f0d49a)}}
.printonly{{display:none}}
@media print{{
 .screenonly{{display:none}}
 .printonly{{display:block}}
 .psec{{break-after:page;page-break-after:always}}
 .psec:last-of-type{{break-after:auto;page-break-after:auto}}
 h2.pt{{font-size:15px;margin:0 0 8px;letter-spacing:.06em}}
 table.mx th{{position:static;background:#efe8dc;color:#4a3609;border-color:#b5a68e}}
 table.mx th.age{{background:#efe8dc;color:#191510}}
 table.mx td{{border-color:#cfc3ab;background:#fff !important}}
 table.mx tbody tr:nth-child(odd) td{{background:#fff !important}}
 .head{{display:none}}
 .printonly{{zoom:.72}}
 .card .hd{{padding:4px 6px}}
 .card .hd img{{width:26px;height:26px}}
 .card .r{{padding:1px 8px}}
 .card .col{{padding:2px 0}}
 .attrs{{padding:2px 8px}}
 .bonus{{padding:3px 8px}}
 .card .ft{{padding:3px 8px}}
 table.mx td{{padding:5px}}
 .lgsec{{break-before:page;zoom:.9}}
 .alt{{font-size:9px;margin:2px 0 0 2px}}
}}
</style></head><body>
{L.SPRITE}
<div class="head"><button class="pbtn noprint" onclick="window.print()">🖨 印刷（A4横）</button>
<h1>{civ_jp}<small>{civ_en} — 戦士 / 弓 / 騎兵 育成所 × 時代</small></h1>
<p>横が生産施設（施設の中はユニット系統ごとに列を分けてある）、縦が時代。縦に見れば同じ系統の強化、横に見ればその時代に出せる兵の並び。
カードの「＋」はその歴史的建造物でも生産できるという意味。数値は基礎値、点線の名前は仮訳。
&nbsp;/&nbsp;<a href="aoe4-od.html">時代ごとの一覧</a></p></div>
<div class="screenonly"><div class="mxwrap"><table class="mx">
<thead><tr><th class="corner age" rowspan="2">時代</th>{h1}</tr><tr>{h2}</tr></thead>
<tbody>{rows}</tbody></table></div></div>
<div class="printonly">{psecs}</div>
<div class="sec lgsec"><h2>属性アイコン</h2><div class="lgwrap">{legend_attrs}</div></div>
<div class="sec"><h2>ステータスアイコン</h2><div class="lgwrap">{legend_stats}</div></div>
<footer class="disc">{L.DISCLAIMER}</footer>
</body></html>'''

out = os.path.join(ROOT, f'aoe4-{CIV}-matrix.html')
open(out, 'w', encoding='utf-8').write(HTML)
print(out, len(units), {jp: [x[1] for x in sub[c]] for c, jp in COLS})
