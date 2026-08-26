// 画面の組み立て: 文明選択、ビュー切り替え、生産施設フィルタ、言語、URL同期
import { SPRITE } from './icons.js';
import { renderMatrix, renderList, renderTable, renderPrintMatrix,
         availableBuildings, MAIN_COLS } from './views.js';
import { setLang, t, L, lang } from './i18n.js';

const $ = (s) => document.querySelector(s);
const VIEWS = ['matrix', 'list', 'table'];
const state = { civ: null, view: 'matrix', blds: null, sort: 'age', asc: true };
let DB = null;
let META = null;

const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/* ---------------- URL ---------------- */
function readURL() {
  const p = new URLSearchParams(location.search);
  state.civ = p.get('civ');
  if (VIEWS.includes(p.get('view'))) state.view = p.get('view');
  state.blds = p.get('b') ? p.get('b').split(',').filter(Boolean) : null;
  const l = p.get('lang') || localStorage.getItem('aoe4units.lang')
    || (navigator.language || '').slice(0, 2);
  setLang(META && META.langs.includes(l) ? l : 'ja', META && META.ui);
}

function writeURL(push = false) {
  const p = new URLSearchParams();
  if (state.civ) p.set('civ', state.civ);
  if (state.civ) p.set('view', state.view);
  if (state.blds) p.set('b', state.blds.join(','));
  if (lang() !== 'ja') p.set('lang', lang());
  const url = p.toString() ? `${location.pathname}?${p}` : location.pathname;
  if (push) history.pushState(null, '', url); else history.replaceState(null, '', url);
}

const unitsOfCiv = () => DB.units.filter((u) => u.civs.includes(state.civ));
const civName = (c) => L(META.civs[c]);

/* ---------------- 文明選択（トップ） ---------------- */
function renderPicker() {
  const codes = Object.keys(META.civs)
    .sort((a, b) => civName(a).localeCompare(civName(b), lang()));
  const tiles = codes.map((c) => {
    const n = DB.units.filter((u) => u.civs.includes(c)).length;
    return `<a class="civtile" href="?civ=${c}" data-civ="${c}">
      <img src="${META.civs[c].flag}" alt="" loading="lazy">
      <span class="cn">${esc(civName(c))}</span>
      <span class="cu">${n} ${esc(t('units'))}</span></a>`;
  }).join('');
  return `<h2 class="pickh">${esc(t('pickCiv'))}</h2><div class="civgrid">${tiles}</div>`;
}

/* ---------------- 生産施設フィルタ ---------------- */
function buildingFilter(units) {
  const avail = availableBuildings(units, META);
  const on = new Set(state.blds || avail.filter((b) => MAIN_COLS.includes(b)));
  const chips = avail.map((b) => `<label class="bchip${on.has(b) ? ' on' : ''}">
    <input type="checkbox" value="${b}"${on.has(b) ? ' checked' : ''}>${esc(L(META.buildings[b]))}</label>`).join('');
  return `<div class="bfilter"><span class="blab">${esc(t('buildings'))}</span>${chips}
    <button class="mini" data-all="1">${esc(t('all'))}</button>
    <button class="mini" data-all="0">${esc(t('none'))}</button></div>`;
}

function activeBlds(units) {
  const avail = availableBuildings(units, META);
  const on = state.blds || avail.filter((b) => MAIN_COLS.includes(b));
  return avail.filter((b) => on.includes(b));
}

/* ---------------- 描画 ---------------- */
function render() {
  document.querySelectorAll('.langbtn').forEach((b) =>
    b.classList.toggle('on', b.dataset.lang === lang()));
  $('#disc').innerHTML = L(META.disclaimer);
  $('#print').textContent = `🖨 ${t('print')}`;
  $('#home').textContent = t('home');

  if (!state.civ || !META.civs[state.civ]) {
    document.title = t('title');
    $('#civname').textContent = t('title');
    $('#chrome').hidden = true;
    $('#main').innerHTML = renderPicker();
    return;
  }

  const units = unitsOfCiv();
  document.title = `${civName(state.civ)} - ${t('title')}`;
  $('#civname').textContent = civName(state.civ);
  $('#chrome').hidden = false;
  $('#civ').value = state.civ;
  $('#count').textContent = `${units.length} ${t('units')}`;
  $('#views').innerHTML = VIEWS.map((v) =>
    `<button class="vtab${v === state.view ? ' on' : ''}" data-view="${v}">${esc(t('view.' + v))}</button>`).join('');
  $('#filter').innerHTML = state.view === 'matrix' ? buildingFilter(units) : '';

  let html;
  if (state.view === 'matrix') html = renderMatrix(units, META, { blds: activeBlds(units) });
  else if (state.view === 'list') html = renderList(units, META);
  else html = renderTable(units, META, { sort: state.sort, asc: state.asc });
  $('#main').innerHTML = html;

  if (state.view === 'table') {
    $('#main').querySelectorAll('th[data-sort]').forEach((th) => {
      th.onclick = () => {
        const k = th.dataset.sort;
        if (state.sort === k) state.asc = !state.asc;
        else { state.sort = k; state.asc = (k === 'jp' || k === 'age'); }
        render();
      };
    });
  }
}

function go(patch, push = true) {
  Object.assign(state, patch);
  writeURL(push);
  render();
  window.scrollTo({ top: 0 });
}

/* ---------------- 印刷 ---------------- */
function preparePrint() {
  if (state.civ && state.view === 'matrix') {
    const units = unitsOfCiv();
    $('#print-area').innerHTML = renderPrintMatrix(units, META, civName(state.civ),
      { blds: activeBlds(units) }) + legendHTML();
    document.body.classList.add('pm');
  } else {
    $('#print-area').innerHTML = '';
    document.body.classList.remove('pm');
  }
}

function legendHTML() {
  const row = (obj, kanji) => Object.entries(obj).map(([k, v]) => {
    const mark = (kanji && lang() === 'ja' && (k === 'a-heavy' || k === 'a-light'))
      ? `<span class="kj">${k === 'a-heavy' ? '重' : '軽'}</span>`
      : `<svg class="ic"><use href="#${k}"/></svg>`;
    return `<div class="lg">${mark}<span>${esc(L(v))}</span></div>`;
  }).join('');
  return `<section class="psec lgsec"><h2 class="pt">${esc(t('legend'))}</h2>
    <div class="lgwrap">${row(META.attrs, true)}</div>
    <div class="lgwrap" style="margin-top:10px">${row(META.stats, false)}</div></section>`;
}

/* ---------------- 初期化 ---------------- */
function wire() {
  $('#civ').innerHTML = Object.keys(META.civs)
    .sort((a, b) => civName(a).localeCompare(civName(b), lang()))
    .map((c) => `<option value="${c}">${esc(civName(c))}</option>`).join('');
  $('#civ').onchange = () => go({ civ: $('#civ').value, blds: null });

  $('#views').onclick = (e) => {
    const b = e.target.closest('.vtab');
    if (b) go({ view: b.dataset.view });
  };
  $('#home').onclick = (e) => { e.preventDefault(); go({ civ: null }); };

  $('#filter').onchange = (e) => {
    if (e.target.type !== 'checkbox') return;
    const on = [...$('#filter').querySelectorAll('input:checked')].map((i) => i.value);
    go({ blds: on }, false);
  };
  $('#filter').onclick = (e) => {
    const b = e.target.closest('button[data-all]');
    if (!b) return;
    const avail = availableBuildings(unitsOfCiv(), META);
    go({ blds: b.dataset.all === '1' ? avail : [] }, false);
  };

  $('#langs').onclick = (e) => {
    const b = e.target.closest('.langbtn');
    if (!b) return;
    setLang(b.dataset.lang, META.ui);
    localStorage.setItem('aoe4units.lang', b.dataset.lang);
    wireLabels();
    go({}, false);
  };

  $('#main').addEventListener('click', (e) => {
    const a = e.target.closest('a.civtile');
    if (!a) return;
    e.preventDefault();
    go({ civ: a.dataset.civ, blds: null });
  });

  $('#print').onclick = () => { preparePrint(); window.print(); };
  window.onpopstate = () => { readURL(); render(); };
  if (new URLSearchParams(location.search).get('print') === '1') setTimeout(preparePrint, 0);
}

function wireLabels() {
  $('#civ').innerHTML = Object.keys(META.civs)
    .sort((a, b) => civName(a).localeCompare(civName(b), lang()))
    .map((c) => `<option value="${c}"${c === state.civ ? ' selected' : ''}>${esc(civName(c))}</option>`).join('');
  $('#home').textContent = t('home');
}

(async function main() {
  document.body.insertAdjacentHTML('afterbegin', SPRITE);
  const [units, meta] = await Promise.all([
    fetch('data/units.json').then((r) => r.json()),
    fetch('data/meta.json').then((r) => r.json()),
  ]);
  DB = units; META = meta;
  readURL();
  $('#langs').innerHTML = META.langs
    .map((l) => `<button class="langbtn" data-lang="${l}">${l === 'ja' ? '日本語' : 'English'}</button>`).join('');
  wire();
  wireLabels();
  writeURL();
  render();
})();
