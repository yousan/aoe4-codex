// ユニットカードの描画。全ビューで共通して使う。
import { t, L, lang } from './i18n.js';

export const IMG_BASE = 'assets/units/';

export function ico(name, cls = '') {
  return `<svg class="ic ${cls}"><use href="#${name}"/></svg>`;
}

const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const TIERS = ['黎明', '初期', '熟練', 'ベテラン', '精鋭'];

/** 系統名（ティアの接頭辞を落とした名前） */
export function lineLabel(u) {
  const n = u.jp || u.n;
  for (const t of TIERS) if (n.startsWith(t)) return n.slice(t.length);
  return n;
}

/** 属性の行（重装/軽装 は漢字チップ、それ以外はアイコン） */
function attrRow(u, meta) {
  const out = u.at.map((a) => {
    if (a === 'a-heavy' || a === 'a-light') {
      const heavy = a === 'a-heavy';
      return `<span class="kj ${heavy ? 'hv' : 'lt'}" data-tip="${esc(L(meta.attrs[a]))}">${heavy ? '重' : '軽'}</span>`;
    }
    return `<span class="at" data-tip="${esc(L(meta.attrs[a]) || a)}">${ico(a)}</span>`;
  }).join('');
  return `<div class="attrs">${out}</div>`;
}

/** ダメージボーナス（対建物・対動物は build_data.py の時点で落としてある） */
function bonusRow(u, meta) {
  if (!u.bo || !u.bo.length) return '';
  const items = u.bo.map((b) => {
    const icons = b.c.map((c) => {
      if (c === 'heavy' || c === 'light') {
        return `<span class="kj ${c === 'heavy' ? 'hv' : 'lt'}">${c === 'heavy' ? '重' : '軽'}</span>`;
      }
      return ico(meta.classIcon[c] || 'a-inf');
    }).join('');
    const names = b.c.map((c) => L(meta.attrs[meta.classIcon[c]]) || c).join(lang() === 'ja' ? '・' : ', ');
    return `<span class="bo up" data-tip="${esc(t('tip.vs', { c: names, v: b.v }))}">+${b.v}${icons}</span>`;
  }).join('');
  return `<div class="bonus">${items}</div>`;
}

const RES = [['f', 'i-food'], ['w', 'i-wood'], ['g', 'i-gold'], ['s', 'i-stone']];

export function renderCard(u, meta) {
  const w = u.w || {};
  const rng = (w.r1 && w.r1 >= 1) ? w.r1 : null;
  const atk = meta.atkIcon[w.t] || 'i-melee';
  const row = (icon, val, tip) =>
    `<div class="r" data-tip="${esc(tip)}">${ico(icon)}<span class="v">${val ?? '–'}</span></div>`;

  const st = (k) => L(meta.stats[k]);
  const left = [
    row('i-hp', u.hp || '–', st('i-hp')),
    row(atk, w.d ?? '–', t('tip.atk', { t: st(atk) })),
    row('i-dps', w.dps ?? '–', t('tip.dps')),
    row('i-int', w.s || '–', t('tip.int')),
  ];
  if (u.ch) left.push(row('a-spear', u.ch.d, t('tip.charge')));

  const right = [
    row('i-range', rng ?? '–', t('tip.range')),
    row('i-armm', u.am, st('i-armm')),
    row('i-armr', u.ar, st('i-armr')),
    row('i-speed', u.mv ?? '–', st('i-speed')),
  ];

  const paid = RES.filter(([k]) => u.cost[k]);
  const tip = (paid.length ? paid.map(([k, icn]) => `${L(meta.stats[icn])} ${u.cost[k]}`).join(' / ') + ' / ' : '')
    + t('tip.cost', { n: u.cost.tot });
  const cost = paid.length
    ? paid.map(([k, icn]) => `<span class="c r-${k}">${ico(icn)}${u.cost[k]}</span>`).join('')
    : `<span class="c r-g">${ico('i-gold')}${u.cost.tot}</span>`;

  const ja = lang() === 'ja';
  const shown = (ja && u.jp) ? u.jp : u.n;
  const name = (ja && u.jp && u.prov)
    ? `<span class="prov" data-tip="${esc(t('tip.prov'))}">${esc(shown)}</span>`
    : esc(shown);
  const sub = (ja && u.jp) ? `<span class="en">${esc(u.n)}</span>` : '';

  return `<div class="card a${u.age}">
  <div class="hd"><img src="${IMG_BASE}${u.ic}" alt="" loading="lazy"><div class="nm">${name}${sub}</div>
    <div class="age">${meta.roman[u.age]}</div></div>
  ${attrRow(u, meta)}
  <div class="body"><div class="col">${left.join('')}</div><div class="col">${right.join('')}</div></div>
  ${bonusRow(u, meta)}
  <div class="ft up" data-tip="${esc(tip)}">${cost}<span class="sp"></span>
    <span class="c dim">${ico('i-time')}${u.cost.t}</span><span class="c dim">${ico('i-pop')}${u.cost.pop}</span></div>
</div>`;
}
