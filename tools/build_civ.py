# -*- coding: utf-8 -*-
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'units-all.json')
"""1文明分のユニット一覧ページを作る"""
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aoe4lib as L

CIV = sys.argv[1] if len(sys.argv) > 1 else 'od'
CIV_JP = {'od': ('ドラゴン騎士団', 'Order of the Dragon')}
name_jp, name_en = CIV_JP.get(CIV, (CIV, CIV))

FAM_ORDER = ['a-inf', 'a-cav', 'a-camel', 'a-eleph', 'a-siege', 'a-ship', 'a-relig', 'a-worker']
# 属性名は aoe4lib.ATTR_JP（＝ゲーム本体のロケール）だけを出典にする。
# ここに書き写していた頃は 攻囲→「攻城兵器」、らくだ→「ラクダ」と表示していた。
FAM_JP = {k: L.ATTR_JP[k] for k in FAM_ORDER}
FAM_JP[''] = 'その他'


def family(u):
    for f in FAM_ORDER:
        if f in u['at']:
            return f
    return ''


units = [u for u in L.UNITS if CIV in u['cv']]
units.sort(key=lambda u: (u['a'], FAM_ORDER.index(family(u)) if family(u) else 99, u['n']))

secs = []
for age in (1, 2, 3, 4):
    us = [u for u in units if u['a'] == age]
    if not us:
        continue
    body, cur = [], None
    for u in us:
        f = family(u)
        if f != cur:
            cur = f
            body.append(f'</div><div class="famlab">{L.ico(f) if f else ""}{FAM_JP[f]}</div><div class="row">')
        body.append(L.card(u, 'kanji'))
    secs.append(f'''<div class="sec"><h2>第 {L.ROMAN[age]} 時代 <small>{len(us)} ユニット</small></h2>
<div class="row">{"".join(body)}</div></div>''')

legend_attrs = ''.join(
    f'<div class="lg">{"<span class=kj>"+("重" if k=="a-heavy" else "軽")+"</span>" if k in ("a-heavy","a-light") else L.ico(k)}<span>{v}</span></div>'
    for k, v in L.ATTR_JP.items())
legend_stats = ''.join(f'<div class="lg">{L.ico(k)}<span>{v}</span></div>'
                       for k, v in L.STAT_JP.items() if k != 'i-fire')
prov = sorted({u['jp'] for u in units if u.get('prov')})
prov_txt = ('「黄金の〜」系すべてと ' + '、'.join(x for x in prov if '黄金' not in x)) \
    if any('黄金' in x for x in prov) else '、'.join(prov)
nojp = sorted({u['n'] for u in units if not u['jp']})

HTML = f'''<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name_jp} ユニット一覧 - AoE4</title><style>{L.CSS}
h1{{font-size:20px;color:var(--gold2, #f0d49a);margin:0 0 2px;letter-spacing:.04em}}
h1 small{{font-size:12px;color:var(--dim);margin-left:10px;letter-spacing:0}}
.head{{margin-bottom:22px;padding-bottom:14px;border-bottom:1px solid var(--line)}}
.head p{{margin:6px 0 0;color:var(--dim);font-size:11.5px;line-height:1.7}}
.pbtn{{float:right;background:var(--gold);color:#1d1710;border:none;border-radius:7px;
padding:7px 14px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit}}
.pbtn:hover{{background:#f0d49a}}
@media print{{ .head p{{font-size:9.5px}} .famlab{{break-after:avoid}} body{{zoom:.82}} }}
.famlab{{width:100%;display:flex;align-items:center;gap:6px;color:var(--gold);font-size:11px;
letter-spacing:.1em;margin:6px 0 2px}}
.famlab svg.ic{{width:14px;height:14px}}
.row{{display:flex;gap:11px;flex-wrap:wrap;align-items:flex-start}}
</style></head><body>
{L.SPRITE}
<div class="head"><button class="pbtn noprint" onclick="window.print()">🖨 印刷（A4横）</button>
<h1>{name_jp}<small>{name_en} — 全 {len(units)} ユニット</small></h1>
<p>数値はアップグレード・文明ボーナス未適用の基礎値。上段の属性アイコンがダメージボーナスの判定対象。
コスト行はホバーで内訳、属性アイコンもホバーで名前が出る。<br>
データ: data.aoe4world.com（ゲームファイル由来）／日本語名: AoE4攻略wiki・AoE Haul wiki 準拠。
点線の名前は<b>仮訳</b>（公式日本語名を確認できなかったもの）: {prov_txt if prov else "なし"}。
{("英語のままのもの: " + "、".join(nojp)) if nojp else ""}</p></div>
{"".join(secs)}
<div class="sec"><h2>属性アイコン</h2><div class="lgwrap">{legend_attrs}</div></div>
<div class="sec"><h2>ステータスアイコン</h2><div class="lgwrap">{legend_stats}</div></div>
<footer class="disc">{L.DISCLAIMER}</footer>
</body></html>'''

out = os.path.join(ROOT, f'aoe4-{CIV}.html')
open(out, 'w', encoding='utf-8').write(HTML)
print(out, len(units), 'prov:', prov, 'noJP:', nojp)
