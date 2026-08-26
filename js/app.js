// 画面の組み立て: 文明のプルダウン、ビュー切り替え、URL 同期
import { SPRITE } from './icons.js';
import { renderMatrix, renderList, renderTable, renderPrintMatrix } from './views.js';

const VIEWS = [
  ['matrix', '生産施設 × 時代'],
  ['list', '時代別一覧'],
  ['table', '表'],
];

const $ = (s) => document.querySelector(s);
const state = { civ: 'od', view: 'matrix', onlyMain: true, sort: 'age', asc: true };
let DB = null;
let META = null;

function readURL() {
  const p = new URLSearchParams(location.search);
  if (p.get('civ')) state.civ = p.get('civ');
  if (p.get('view')) state.view = p.get('view');
  if (p.get('all') === '1') state.onlyMain = false;
}

function writeURL(push = false) {
  const p = new URLSearchParams({ civ: state.civ, view: state.view });
  if (!state.onlyMain) p.set('all', '1');
  const url = `${location.pathname}?${p}`;
  if (push) history.pushState(null, '', url); else history.replaceState(null, '', url);
}

function unitsOfCiv() {
  return DB.units.filter((u) => u.civs.includes(state.civ));
}

function render() {
  const units = unitsOfCiv();
  const civ = META.civs[state.civ];
  document.title = `${civ.jp} - AoE4 ユニット`;
  $('#civname').textContent = civ.jp;
  $('#count').textContent = `${units.length} ユニット`;
  $('#opt-all').hidden = state.view !== 'matrix';
  document.querySelectorAll('.vtab').forEach((b) => {
    b.classList.toggle('on', b.dataset.view === state.view);
  });

  const t0 = performance.now();
  let html = '';
  if (state.view === 'matrix') html = renderMatrix(units, META, { onlyMain: state.onlyMain });
  else if (state.view === 'list') html = renderList(units, META);
  else html = renderTable(units, META, { sort: state.sort, asc: state.asc });
  $('#main').innerHTML = html;
  $('#ms').textContent = `${Math.round(performance.now() - t0)}ms`;

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
  window.scrollTo({ top: 0 });
}

/** 印刷の最後に付けるアイコン凡例 */
function legendHTML() {
  const row = (obj, kanji) => Object.entries(obj).map(([k, v]) => {
    const mark = (kanji && (k === 'a-heavy' || k === 'a-light'))
      ? `<span class="kj">${k === 'a-heavy' ? '重' : '軽'}</span>`
      : `<svg class="ic"><use href="#${k}"/></svg>`;
    return `<div class="lg">${mark}<span>${v}</span></div>`;
  }).join('');
  return `<section class="psec lgsec"><h2 class="pt">アイコン凡例</h2>
    <div class="lgwrap">${row(META.attrs, true)}</div>
    <div class="lgwrap" style="margin-top:10px">${row(META.stats, false)}</div></section>`;
}

function buildChrome() {
  const sel = $('#civ');
  sel.innerHTML = Object.keys(META.civs)
    .sort((a, b) => META.civs[a].jp.localeCompare(META.civs[b].jp, 'ja'))
    .map((c) => `<option value="${c}">${META.civs[c].jp}</option>`).join('');
  sel.value = state.civ;
  sel.onchange = () => { state.civ = sel.value; writeURL(true); render(); };

  $('#views').innerHTML = VIEWS
    .map(([v, lbl]) => `<button class="vtab" data-view="${v}">${lbl}</button>`).join('');
  $('#views').onclick = (e) => {
    const b = e.target.closest('.vtab');
    if (!b) return;
    state.view = b.dataset.view; writeURL(true); render();
  };

  const chk = $('#allbld');
  chk.checked = !state.onlyMain;
  chk.onchange = () => { state.onlyMain = !chk.checked; writeURL(); render(); };

  const preparePrint = () => {
    // マトリクスは横に広いので、印刷時だけ 1施設=1ページ に組み替える
    if (state.view === 'matrix') {
      $('#print-area').innerHTML = renderPrintMatrix(
        unitsOfCiv(), META, META.civs[state.civ].jp, { onlyMain: state.onlyMain }) + legendHTML();
      document.body.classList.add('pm');
    } else {
      $('#print-area').innerHTML = '';
      document.body.classList.remove('pm');
    }
  };
  $('#print').onclick = () => { preparePrint(); window.print(); };
  // ?print=1 で印刷用レイアウトを組んだ状態で開く（PDF出力の確認用）
  if (new URLSearchParams(location.search).get('print') === '1') preparePrint();
  $('#disc').innerHTML = META.disclaimer;

  window.onpopstate = () => { readURL(); $('#civ').value = state.civ; render(); };
}

(async function main() {
  document.body.insertAdjacentHTML('afterbegin', SPRITE);
  readURL();
  const [units, meta] = await Promise.all([
    fetch('data/units.json').then((r) => r.json()),
    fetch('data/meta.json').then((r) => r.json()),
  ]);
  DB = units; META = meta;
  if (!META.civs[state.civ]) state.civ = 'od';
  buildChrome();
  writeURL();
  render();
})();
