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
  const hasTechTip = (techs || []).some((tech) => effectsFor(unit, tech).length);
  const bslug = (tech) => (tech.bld && tech.bld[civ]) || '-';
  const tline = (tech, tail) => `　${meta.roman[tech.age]}  ${techName(tech)}`
    + `（${bldName(bslug(tech))}）  ${tail}`;
  // [マーク, 数値, 時代, 施設スラッグ, 施設名, テク名, 詳細]
  const trow = (icon, val, tech, detail) => [icon, val, meta.roman[tech.age],
    bslug(tech), bldName(bslug(tech)), techName(tech), detail || ''];
  const tipData = (head, rows) => ` data-tiph='${
    JSON.stringify({ h: head, r: rows }).replaceAll("'", '&#39;').replaceAll('&', '&amp;')
      .replaceAll('&amp;#39;', '&#39;')}'`;
  const w = u.w || {};
  const rng = (w.r1 && w.r1 >= 1) ? w.r1 : null;
  const atk = meta.atkIcon[w.t] || 'i-melee';
  // 増分は小数2桁まで。3桁だと桁が伸びてカードからはみ出す（移動速度の ×1.15 など）
  const dnum = (n) => Math.round(n * 100) / 100;
  const dtxt = (n) => (n > 0 ? `+${dnum(n)}` : `${dnum(n)}`);
  const row = (icon, val, tip, field, label) => {
    // 表示しない項目（近接ユニットの射程など）にテクが乗ることがある。増分は出さない
    const m = field && mods && mods[field]
      && Number.isFinite(val) && Number.isFinite(unitVal(unit, field)) ? mods[field] : null;
    // 強化ぶんを出しているときは、カード全体の一覧ツールチップに任せる（行ごとに出すと煩い）
    if (hasTechTip) {
      // 「基礎値 + 増分」で揃える。強化後の値を出すと +N と二重に見える
      const b = m ? unitVal(unit, field) : val;
      // 増分の無い行にも空の枠を置く。置かないと基礎値の右端が行ごとにずれる
      return `<div class="r">${ico(icon)}<span class="v">${b ?? '–'}</span>`
        + `<span class="dlt">${m ? dtxt(val - b) : ''}</span></div>`;
    }
    if (!m) return `<div class="r" data-tip="${esc(tip)}">${ico(icon)}<span class="v">${val ?? '–'}</span></div>`;
    const base = unitVal(unit, field);
    const head = `${label || tip}　${base} → ${val}`;
    const lines = [head, ...m.map((x) => tline(x.t, x.txt))];
    const detail = esc(lines.join('\n')).replaceAll('\n', '&#10;');
    const rows = m.map((x) => trow(icon, x.txt, x.t, ''));
    return `<div class="r" data-tip="${detail}"${tipData(head, rows)}>${ico(icon)}`
      + `<span class="v">${base}</span>`
      + `<span class="dlt">${dtxt(val - base)}</span></div>`;
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
  const cardHead = `${unitName(unit)}　${t('techs')} ${applied.length}`;
  const cardTip = applied.length
    ? esc([cardHead, ...applied.map((tech) => tline(tech,
        effectsFor(unit, tech).map((e) => `${propLabel(e.p)} ${fxText(e)}`).join(' / ')))]
      .join('\n')).replaceAll('\n', '&#10;')
    : '';
  const cardRows = applied.flatMap((tech) => effectsFor(unit, tech)
    .map((e) => trow(PROP_ICON[e.p] || 'i-hp', fxText(e), tech, propLabel(e.p))));

  return `<div class="card a${u.age}"${cardTip
    ? ` data-tip="${cardTip}"${tipData(cardHead, cardRows)}` : ''}>
  <div class="hd"><img src="${IMG_BASE}${u.ic}" alt="" loading="lazy"><div class="nm">${name}${sub}</div>
    <div class="age">${meta.roman[u.age]}</div></div>
  ${attrRow(u, meta)}
  <div class="body"><div class="col">${left.join('')}</div><div class="col">${right.join('')}</div></div>
  ${bonusRow(u, meta)}
  <div class="ft up" data-tip="${esc(tip)}"><span class="res">${cost}</span><span class="mk">
    <span class="c dim"${mods && mods.t && !hasTechTip ? ` data-tip="${
      esc([`${term('i-time')}　${unit.cost.t} → ${u.cost.t}`,
        ...mods.t.map((x) => tline(x.t, x.txt))].join('\n'))
        .replaceAll('\n', '&#10;')}"` : ''}>${
      ico('i-time')}${mods && mods.t ? unit.cost.t : u.cost.t}${mods && mods.t
        ? `<b class="dlt">${dtxt(u.cost.t - unit.cost.t)}</b>` : ''}</span><span class="c dim">${ico('i-pop')}${u.cost.pop}</span></span></div>
</div>`;
}
