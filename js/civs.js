// 文明特性と固有テクノロジーの一覧。data/civs.json + data/civs-i18n/<lang>.json を読む。
// 文言はすべてゲーム本体から抽出したもので、こちらでは訳さない（英語のままのものは印を付ける）。
import { SPRITE } from './icons.js';
import { traitCard } from './traits.js';

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const ico = (id) => `<svg class="ic"><use href="#${id}"/></svg>`;

const AGES = [1, 2, 3, 4];
const ROMAN = { 1: 'I', 2: 'II', 3: 'III', 4: 'IV' };
const RES = [['food', 'i-food', 'f'], ['wood', 'i-wood', 'wd'],
  ['gold', 'i-gold', 'g'], ['stone', 'i-stone', 'st']];
const EXTRA = [['silver', 'i-silver'], ['vizier', 'i-vizier']];

const state = { civ: null, lang: 'ja', blds: null };
let DB = null;      // data/civs.json
let L = null;       // data/civs-i18n/<lang>.json
let BL = {};        // 建物名（ユニット一覧と同じ data/i18n/<lang>.json から）

const t = (key, vars) => {
  let s = (L.ui && L.ui[key]) || key;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.replaceAll(`{${k}}`, v);
  return s;
};
const civName = (c) => (BL.civs && BL.civs[c]) || DB.civs[c].en;
const bldName = (slug) => (BL.buildings && BL.buildings[slug])
  || slug.split('-').map((w) => w[0].toUpperCase() + w.slice(1)).join(' ');
const termName = (key, dflt) => (L.terms && L.terms[key]) || dflt;

/* ---------------- URL ---------------- */
function readURL() {
  const p = new URLSearchParams(location.search);
  state.civ = p.get('civ');
  state.blds = p.get('b') ? p.get('b').split(',').filter(Boolean) : null;
  state.lang = p.get('lang') || localStorage.getItem('aoe4units.lang') || pickBrowserLang();
}

function writeURL(push = false) {
  const p = new URLSearchParams();
  if (state.civ) p.set('civ', state.civ);
  if (state.blds) p.set('b', state.blds.join(','));
  if (state.lang !== 'ja') p.set('lang', state.lang);
  const url = p.toString() ? `${location.pathname}?${p}` : location.pathname;
  if (push) history.pushState(null, '', url); else history.replaceState(null, '', url);
}

function pickBrowserLang() {
  const langs = DB.langs || ['ja'];
  for (const raw of navigator.languages || [navigator.language || '']) {
    if (langs.includes(raw)) return raw;
    const hit = langs.find((l) => l.split('-')[0] === raw.split('-')[0]);
    if (hit) return hit;
  }
  return 'ja';
}

/* ---------------- 読み込み ---------------- */
async function loadLang(lang) {
  const [a, b] = await Promise.all([
    fetch(`data/civs-i18n/${lang}.json`).then((r) => (r.ok ? r.json() : null)),
    fetch(`data/i18n/${lang}.json`).then((r) => (r.ok ? r.json() : null)),
  ]);
  if (!a) throw new Error(`no locale: ${lang}`);
  L = a;
  BL = b || {};
  state.lang = lang;
  document.documentElement.lang = lang;
  localStorage.setItem('aoe4units.lang', lang);
}

/* ---------------- 研究施設フィルタ ---------------- */
const techBlds = (civ) => {
  const seen = [];
  for (const r of DB.civs[civ].techs) {
    for (const b of r.from) if (!seen.includes(b)) seen.push(b);
  }
  return seen.sort((a, b) => bldName(a).localeCompare(bldName(b), state.lang));
};

const activeBlds = (civ) => {
  const all = techBlds(civ);
  return state.blds ? state.blds.filter((b) => all.includes(b)) : all;
};

function filterUI(civ) {
  const all = techBlds(civ);
  if (all.length < 2) return '';
  const on = new Set(activeBlds(civ));
  const chips = all.map((b) => `<label class="bchip${on.has(b) ? ' on' : ''}">
    <input type="checkbox" name="b" value="${b}"${on.has(b) ? ' checked' : ''}>${esc(bldName(b))}</label>`).join('');
  return `<div class="bfilter"><span class="blab">${esc(t('buildings'))}</span>${chips}
    <button class="mini" data-all="1">${esc(t('all'))}</button>
    <button class="mini" data-none="1">${esc(t('none'))}</button></div>`;
}

/* ---------------- 描画 ---------------- */
function picker() {
  const codes = Object.keys(DB.civs)
    .sort((a, b) => civName(a).localeCompare(civName(b), state.lang));
  const tiles = codes.map((c) => `<a class="civtile" href="?civ=${c}" data-civ="${c}">
    <img src="${DB.civs[c].flag}" alt="" loading="lazy">
    <span class="cn">${esc(civName(c))}</span>
    <span class="cu">${esc(t('techs'))} ${DB.civs[c].techs.length}</span></a>`).join('');
  return `<h2 class="pickh">${esc(t('pickCiv'))}</h2><div class="civgrid">${tiles}</div>`;
}

function cost(r) {
  const parts = RES.filter(([k]) => r.cost[k])
    .map(([k, icn, cls]) => `<span class="c r-${cls}">${ico(icn)}${r.cost[k]}</span>`);
  for (const [k, term] of EXTRA) {
    if (r.cost[k]) parts.push(`<span class="c r-g">${r.cost[k]} ${esc(termName(term, k))}</span>`);
  }
  if (!parts.length) parts.push(`<span class="c dim">${esc(t('free'))}</span>`);
  if (r.time) {
    parts.push(`<span class="c dim" data-tip="${esc(t('time'))}">${ico('i-time')}${
      esc(t('sec', { n: r.time }))}</span>`);
  }
  return parts.join('');
}

function techCard(r) {
  const s = L.techs[r.k] || { n: r.k, d: '' };
  const from = r.from.length
    ? `<span class="tfrom">${r.from.map((b) => esc(bldName(b))).join(' / ')}</span>` : '';
  const rep = r.rep
    ? `<span class="trep">${esc(t('repeat', { all: r.repAll }))} ・ ${
      esc(t('repeatAge', { n: r.rep }))}</span>` : '';
  const en = r.f ? `<span class="enmark" data-tip="${esc(t('enOnly'))}">EN</span>` : '';
  return `<article class="tcard a${r.age}">
    <div class="thd"><img src="${r.icon}" alt="" loading="lazy">
      <span class="tnm">${esc(s.n)}${from}</span>${en}
      <span class="age">${ROMAN[r.age]}</span></div>
    <p class="tdesc">${esc(s.d).replaceAll('\n', '<br>')}</p>
    ${rep}<div class="tft">${cost(r)}</div></article>`;
}

function civPage(civ) {
  const c = DB.civs[civ];
  const on = new Set(activeBlds(civ));
  const shown = c.techs.filter((r) => !r.from.length || r.from.some((b) => on.has(b)));
  const traits = c.traits.map((tr) => traitCard(tr, L, t('enOnly'))).join('');

  const ages = AGES.map((a) => {
    const rows = shown.filter((r) => r.age === a);
    if (!rows.length) return '';
    return `<h3 class="ageh a${a}">${esc(t('ageN', { n: a }))}</h3>
      <div class="tgrid">${rows.map(techCard).join('')}</div>`;
  }).join('');

  return `<div class="civhead"><img src="${c.flag}" alt="">
      <div><h2 class="civh">${esc(civName(civ))}</h2>
      <p class="civdesc">${esc(L.civDesc[civ] || '')}</p></div></div>
    <section class="sec"><h2>${esc(t('traits'))}</h2><div class="tgrid">${traits}</div></section>
    <section class="sec"><h2>${esc(t('techsOf', { n: c.techs.length }))}</h2>
      ${ages || `<p class="empty">${esc(t('noTechs'))}</p>`}</section>
    <p class="note">${esc(t('note'))}</p>`;
}

/* ---------------- 外枠 ---------------- */
function chrome() {
  const sel = $('#civ');
  const codes = Object.keys(DB.civs)
    .sort((a, b) => civName(a).localeCompare(civName(b), state.lang));
  sel.innerHTML = codes.map((c) =>
    `<option value="${c}"${c === state.civ ? ' selected' : ''}>${esc(civName(c))}</option>`).join('');

  const ls = $('#langs');
  ls.innerHTML = (DB.langs || ['ja']).map((l) =>
    `<option value="${l}"${l === state.lang ? ' selected' : ''}>${l}</option>`).join('');

  $('#chrome').hidden = !state.civ;
  $('#civname').textContent = state.civ ? civName(state.civ) : t('title');
  $('#home').textContent = t('home');
  $('#print').textContent = t('print');
  $('#lnk-units').textContent = t('units');
  $('#lnk-maps').textContent = t('maps');

  const civ = state.civ ? civName(state.civ) : '';
  const q = new URLSearchParams({
    labels: 'data',
    title: t('report.title', { civ }),
    body: t('report.body', {
      civ, code: state.civ || '-', url: location.href,
      patch: DB.patch || '-', lang: state.lang,
    }),
  });
  document.querySelectorAll('a.report').forEach((a) => {
    a.href = `https://github.com/yousan/aoe4units/issues/new?${q}`;
    a.textContent = `⚑ ${t('report')}`;
  });
}

function render() {
  chrome();
  $('#filter').innerHTML = state.civ ? filterUI(state.civ) : '';
  $('#main').innerHTML = state.civ ? civPage(state.civ) : picker();
  document.title = state.civ ? `${civName(state.civ)} — ${t('title')}` : t('title');
}

/* ---------------- イベント ---------------- */
function wire() {
  $('#civ').addEventListener('change', (e) => {
    state.civ = e.target.value; state.blds = null; writeURL(true); render();
  });
  $('#langs').addEventListener('change', async (e) => {
    await loadLang(e.target.value); writeURL(); render();
  });
  $('#print').addEventListener('click', () => window.print());
  $('#main').addEventListener('click', (e) => {
    const a = e.target.closest('a.civtile');
    if (!a) return;
    e.preventDefault();
    state.civ = a.dataset.civ; state.blds = null; writeURL(true); render();
  });
  $('#filter').addEventListener('change', () => {
    const on = [...document.querySelectorAll('#filter input[name=b]:checked')].map((i) => i.value);
    state.blds = on.length === techBlds(state.civ).length ? null : on;
    writeURL(); render();
  });
  $('#filter').addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    state.blds = b.dataset.all ? null : [];
    writeURL(); render();
  });
  addEventListener('popstate', async () => {
    readURL();
    if (state.lang !== L.lang) await loadLang(state.lang);
    render();
  });
}

(async function main() {
  document.body.insertAdjacentHTML('afterbegin', SPRITE);
  DB = await (await fetch('data/civs.json')).json();
  readURL();
  try {
    await loadLang(state.lang);
  } catch {
    await loadLang('ja');
  }
  if (state.civ && !DB.civs[state.civ]) state.civ = null;
  wire();
  render();
  writeURL();
}());
