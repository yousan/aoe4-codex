// ユニットカードの描画。全ビューで共通して使う。
import { t, lang, term, unitName, techName, bldName } from './i18n.js';
import { applyTechs, effectsFor, fxText, PROP_ICON } from './techs.js';

export const IMG_BASE = 'assets/units/';

export function ico(name, cls = '') {
  return `<svg class="ic ${cls}"><use href="#${name}"/></svg>`;
}

const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** 効果の対象になっている数値の名前 */
function propLabel(p) {
  const icon = PROP_ICON[p] || p;
  return p.endsWith('Attack') ? t('tip.atk', { t: term(icon) }) : term(icon);
}

/** テク適用前の値（ツールチップの「基礎値」用） */
function unitVal(u, field) {
  if (field === 'd') return u.w ? u.w.d : '–';
  if (field === 's') return u.w ? u.w.s : '–';
  if (field === 'r1') return u.w ? u.w.r1 : '–';
  if (field === 'dps') return u.w ? u.w.dps : '–';
  if (field === 't') return u.cost.t;
  return u[field];
}

/** 系統名。同じ系統の中でいちばん短い名前を使う（言語ごとの接頭辞に依存しない） */
export function lineLabel(units) {
  const list = Array.isArray(units) ? units : [units];
  const names = list.map(unitName);
  return names.reduce((a, b) => (b.length < a.length ? b : a), names[0]);
}

/** 属性の行（重装/軽装 は漢字チップ、それ以外はアイコン） */
function attrRow(u, meta) {
  const out = u.at.map((a) => {
    const tip = esc(term(a));
    if ((a === 'a-heavy' || a === 'a-light') && lang() === 'ja') {
      const heavy = a === 'a-heavy';
      return `<span class="kj ${heavy ? 'hv' : 'lt'}" data-tip="${tip}">${heavy ? '重' : '軽'}</span>`;
    }
    return `<span class="at" data-tip="${tip}">${ico(a)}</span>`;
  }).join('');
  return `<div class="attrs">${out}</div>`;
}

/** ダメージボーナス（対建物・対動物は build_data.py の時点で落としてある） */
function bonusRow(u, meta) {
  if (!u.bo || !u.bo.length) return '';
  const items = u.bo.map((b) => {
    const icons = b.c.map((c) => {
      if ((c === 'heavy' || c === 'light') && lang() === 'ja') {
        return `<span class="kj ${c === 'heavy' ? 'hv' : 'lt'}">${c === 'heavy' ? '重' : '軽'}</span>`;
      }
      return ico(meta.classIcon[c] || 'a-inf');
    }).join('');
    const names = b.c.map((c) => term(meta.classIcon[c] || c)).join(lang() === 'ja' ? '・' : ', ');
    return `<span class="bo up" data-tip="${esc(t('tip.vs', { c: names, v: b.v }))}">+${b.v}${icons}</span>`;
  }).join('');
  return `<div class="bonus">${items}</div>`;
}

const RES = [['f', 'i-food'], ['w', 'i-wood'], ['g', 'i-gold'], ['s', 'i-stone']];

export function renderCard(unit, meta, techs, civ) {
  const { u, mods } = applyTechs(unit, techs);
  const tline = (tech, tail) => `　${meta.roman[tech.age]}  ${techName(tech)}`
    + `（${bldName((tech.bld && tech.bld[civ]) || '-')}）  ${tail}`;
  const w = u.w || {};
  const rng = (w.r1 && w.r1 >= 1) ? w.r1 : null;
  const atk = meta.atkIcon[w.t] || 'i-melee';
  const row = (icon, val, tip, field, label) => {
    const m = field && mods && mods[field];
    if (!m) return `<div class="r" data-tip="${esc(tip)}">${ico(icon)}<span class="v">${val ?? '–'}</span></div>`;
    const base = unitVal(unit, field);
    const d = Math.round((val - base) * 1000) / 1000;
    const lines = [`${label || tip}　${base} → ${val}`,
      ...m.map((x) => tline(x.t, x.txt))];
    const detail = esc(lines.join('\n')).replaceAll('\n', '&#10;');
    return `<div class="r" data-tip="${detail}">${ico(icon)}`
      + `<span class="v">${base}</span>`
      + `<span class="up">${d > 0 ? '+' : ''}${d}</span></div>`;
  };

  const st = (k) => term(k);
  const left = [
    row('i-hp', u.hp || '–', st('i-hp'), 'hp'),
    row(atk, w.d ?? '–', t('tip.atk', { t: st(atk) }), 'd'),
    row('i-dps', w.dps ?? '–', t('tip.dps'), 'dps', 'DPS'),
    row('i-int', w.s || '–', t('tip.int'), 's', term('i-int')),
  ];
  if (u.ch) left.push(row('a-spear', u.ch.d, t('tip.charge')));

  const right = [
    row('i-range', rng ?? '–', t('tip.range'), 'r1', term('i-range')),
    row('i-armm', u.am, st('i-armm'), 'am'),
    row('i-armr', u.ar, st('i-armr'), 'ar'),
    row('i-speed', u.mv ?? '–', st('i-speed'), 'mv'),
  ];

  const paid = RES.filter(([k]) => u.cost[k]);
  const tip = (paid.length ? paid.map(([k, icn]) => `${term(icn)} ${u.cost[k]}`).join(' / ') + ' / ' : '')
    + t('tip.cost', { n: u.cost.tot });
  const cost = paid.length
    ? paid.map(([k, icn]) => `<span class="c r-${k}">${ico(icn)}${u.cost[k]}</span>`).join('')
    : `<span class="c r-g">${ico('i-gold')}${u.cost.tot}</span>`;

  const shown = unitName(u);
  const name = esc(shown);
  const sub = shown !== u.n ? `<span class="en">${esc(u.n)}</span>` : '';

  const applied = (techs || []).filter((tech) => effectsFor(unit, tech).length);
  const cardTip = applied.length
    ? esc([`${unitName(unit)}　${t('techs')} ${applied.length}`,
        ...applied.map((tech) => tline(tech,
          effectsFor(unit, tech).map((e) => `${propLabel(e.p)} ${fxText(e)}`).join(' / ')))]
      .join('\n')).replaceAll('\n', '&#10;')
    : '';

  return `<div class="card a${u.age}"${cardTip ? ` data-tip="${cardTip}"` : ''}>
  <div class="hd"><img src="${IMG_BASE}${u.ic}" alt="" loading="lazy"><div class="nm">${name}${sub}</div>
    <div class="age">${meta.roman[u.age]}</div></div>
  ${attrRow(u, meta)}
  <div class="body"><div class="col">${left.join('')}</div><div class="col">${right.join('')}</div></div>
  ${bonusRow(u, meta)}
  <div class="ft up" data-tip="${esc(tip)}">${cost}<span class="sp"></span>
    <span class="c dim"${mods && mods.t ? ` data-tip="${
      esc([`${term('i-time')}　${unit.cost.t} → ${u.cost.t}`,
        ...mods.t.map((x) => tline(x.t, x.txt))].join('\n'))
        .replaceAll('\n', '&#10;')}"` : ''}>${
      ico('i-time')}${u.cost.t}${mods && mods.t
        ? `<b class="up">${Math.round((u.cost.t - unit.cost.t) * 100) / 100}</b>` : ''}</span><span class="c dim">${ico('i-pop')}${u.cost.pop}</span></div>
</div>`;
}
