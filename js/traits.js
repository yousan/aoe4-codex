// 文明特性（civ bonus）の描画。ユニット一覧と文明ページで共有する。
// 文言はゲーム本体から抽出したもので、こちらでは訳さない（英語のままのものは EN 印を付ける）。

const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

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
