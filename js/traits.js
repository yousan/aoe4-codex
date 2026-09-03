// 文明特性（civ bonus）と固有テクノロジーの描画。ユニット一覧と文明ページで共有する。
// 文言はゲーム本体から抽出したもので、こちらでは訳さない（英語のままのものは EN 印を付ける）。

const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const ico = (id) => `<svg class="ic"><use href="#${id}"/></svg>`;

const AGES = [1, 2, 3, 4];
const ROMAN = { 1: 'I', 2: 'II', 3: 'III', 4: 'IV' };
const RES = [['food', 'i-food', 'f'], ['wood', 'i-wood', 'wd'],
  ['gold', 'i-gold', 'g'], ['stone', 'i-stone', 'st']];
const EXTRA = [['silver', 'i-silver'], ['vizier', 'i-vizier']];

let DB = null;              // data/civs.json
const I18N = new Map();     // lang → data/civs-i18n/<lang>.json

/** 文明特性のデータを読む。2回目からはキャッシュを返す */
export async function loadCivInfo(lang) {
  if (!DB) DB = await fetch('data/civs.json').then((r) => r.json());
  if (!I18N.has(lang)) {
    const r = await fetch(`data/civs-i18n/${lang}.json`);
    I18N.set(lang, r.ok ? await r.json() : null);
  }
  return { db: DB, L: I18N.get(lang) };
}

export function traitCard(tr, L, enOnlyTip) {
  const s = (L.traits && L.traits[tr.k]) || { t: tr.k, d: '' };
  const en = tr.f ? `<span class="enmark" data-tip="${esc(enOnlyTip)}">EN</span>` : '';
  return `<article class="tcard trait">
    <div class="thd"><span class="tnm">${esc(s.t)}</span>${en}</div>
    <p class="tdesc">${esc(s.d).replaceAll('\n', '<br>')}</p></article>`;
}

export function traitGrid(civ, db, L, enOnlyTip) {
  const c = db.civs[civ];
  if (!c || !c.traits) return '';
  return `<div class="tgrid">${c.traits.map((tr) => traitCard(tr, L, enOnlyTip)).join('')}</div>`;
}

/** 固有テクノロジー1件。ctx = { t, bldName, termName }（ページごとの言語ヘルパ） */
export function techCard(r, L, ctx) {
  const s = (L.techs && L.techs[r.k]) || { n: r.k, d: '' };
  const from = r.from.length
    ? `<span class="tfrom">${r.from.map((b) => esc(ctx.bldName(b))).join(' / ')}</span>` : '';
  const rep = r.rep
    ? `<span class="trep">${esc(ctx.t('repeat', { all: r.repAll }))} ・ ${
      esc(ctx.t('repeatAge', { n: r.rep }))}</span>` : '';
  const en = r.f ? `<span class="enmark" data-tip="${esc(ctx.t('enOnly'))}">EN</span>` : '';
  const parts = RES.filter(([k]) => r.cost[k])
    .map(([k, icn, cls]) => `<span class="c r-${cls}">${ico(icn)}${r.cost[k]}</span>`);
  for (const [k, term] of EXTRA) {
    if (r.cost[k]) parts.push(`<span class="c r-g">${r.cost[k]} ${esc(ctx.termName(term, k))}</span>`);
  }
  if (!parts.length) parts.push(`<span class="c dim">${esc(ctx.t('free'))}</span>`);
  if (r.time) {
    parts.push(`<span class="c dim" data-tip="${esc(ctx.t('time'))}">${ico('i-time')}${
      esc(ctx.t('sec', { n: r.time }))}</span>`);
  }
  return `<article class="tcard a${r.age}">
    <div class="thd"><img src="${r.icon}" alt="" loading="lazy">
      <span class="tnm">${esc(s.n)}${from}</span>${en}
      <span class="age">${ROMAN[r.age]}</span></div>
    <p class="tdesc">${esc(s.d).replaceAll('\n', '<br>')}</p>
    ${rep}<div class="tft">${parts.join('')}</div></article>`;
}

/** 固有テクノロジーを時代ごとに並べる */
export function techAges(rows, L, ctx) {
  return AGES.map((a) => {
    const list = rows.filter((r) => r.age === a);
    if (!list.length) return '';
    return `<h3 class="ageh a${a}">${esc(ctx.t('ageN', { n: a }))}</h3>
      <div class="tgrid">${list.map((r) => techCard(r, L, ctx)).join('')}</div>`;
  }).join('');
}
