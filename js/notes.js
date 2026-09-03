// 考察ページ。data/notes.json を読んで記事を組み立てる。
// ここだけは「ゲームから抽出した事実」ではなく前提を置いた考察なので、
// 記事ごとに 前提 / 出典 / 日付 / 確度 を必ず出す。
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
// 本文で使える装飾は **強調** だけ。先にエスケープしてから置き換えるので HTML は書けない
const md = (s) => esc(s).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>');

const KIND = {
  fact: { label: '事実（出典あり）', cls: 'k-fact' },
  analysis: { label: '考察（前提あり）', cls: 'k-ana' },
  correction: { label: '訂正', cls: 'k-fix' },
};

let DB = null;
const state = { id: null };

function readURL() {
  state.id = new URLSearchParams(location.search).get('n');
}

function writeURL(push = false) {
  const url = state.id ? `${location.pathname}?n=${state.id}` : location.pathname;
  if (push) history.pushState(null, '', url); else history.replaceState(null, '', url);
}

const kindOf = (n) => KIND[n.kind] || KIND.analysis;

/* ---------------- 本文のブロック ---------------- */
function block(b) {
  if (b.h) return `<h3 class="nh">${esc(b.h)}</h3>`;
  if (b.p) return `<p class="np">${md(b.p)}</p>`;
  if (b.note) return `<p class="nnote">${md(b.note)}</p>`;
  if (b.ul) return `<ul class="nul">${b.ul.map((x) => `<li>${md(x)}</li>`).join('')}</ul>`;
  if (b.table) {
    const h = b.table.head.map((x) => `<th>${esc(x)}</th>`).join('');
    const r = b.table.rows.map((row) =>
      `<tr>${row.map((c, i) => `<td class="${i ? 'num' : 'l'}">${md(c)}</td>`).join('')}</tr>`).join('');
    return `<div class="ntwrap"><table class="ntbl"><thead><tr>${h}</tr></thead><tbody>${r}</tbody></table></div>`;
  }
  return '';
}

function article(n) {
  const k = kindOf(n);
  const asm = (n.assumptions || []).map((x) => `<li>${md(x)}</li>`).join('');
  const src = (n.sources || []).map((s) => s.u
    ? `<li><a href="${esc(s.u)}" target="_blank" rel="noopener">${esc(s.t)}</a></li>`
    : `<li>${esc(s.t)}</li>`).join('');
  return `<article class="ncard" id="n-${esc(n.id)}">
    <div class="nhd">
      <span class="kind ${k.cls}">${esc(k.label)}</span>
      <span class="ndate">${esc(n.date)}</span>
      ${(n.tags || []).map((t) => `<span class="ntag">${esc(t)}</span>`).join('')}
    </div>
    <h2 class="ntitle">${esc(n.title)}</h2>
    <p class="nlead">${md(n.lead || '')}</p>
    ${asm ? `<div class="nmeta"><b>前提</b><ul>${asm}</ul></div>` : ''}
    ${n.body.map(block).join('')}
    ${src ? `<div class="nmeta src"><b>出典</b><ul>${src}</ul></div>` : ''}
  </article>`;
}

function index() {
  const items = DB.notes.map((n) => {
    const k = kindOf(n);
    return `<a class="nitem" href="?n=${esc(n.id)}" data-id="${esc(n.id)}">
      <span class="kind ${k.cls}">${esc(k.label)}</span>
      <span class="nit">${esc(n.title)}</span>
      <span class="nil">${esc(n.lead || '')}</span>
      <span class="ndate">${esc(n.date)}</span></a>`;
  }).join('');
  return `<h2 class="pickh">考察（${DB.notes.length}件）</h2>
    <p class="note nintro">このページの中身は、ほかのページと性格が違う。ユニットや文明特性は
ゲーム本体から機械的に抜いた事実だが、ここは<b>前提を置いた上での計算と考察</b>で、
実測ではない。記事ごとに前提と出典を頭に書いてあるので、そこを見てから数字を使ってほしい。</p>
    <div class="nlist">${items}</div>`;
}

function render() {
  const n = state.id && DB.notes.find((x) => x.id === state.id);
  $('#main').innerHTML = n
    ? `<p class="nback"><a href="?">← 考察の一覧へ</a></p>${article(n)}`
    : index();
  document.title = n ? `${n.title} — AoE4 考察` : 'AoE4 考察';
  $('#pagetitle').textContent = n ? n.title : '考察';
  window.scrollTo({ top: 0 });
}

function wire() {
  $('#main').addEventListener('click', (e) => {
    const a = e.target.closest('a.nitem, a.nback, .nback a');
    if (!a) return;
    e.preventDefault();
    state.id = a.dataset.id || null;
    writeURL(true); render();
  });
  addEventListener('popstate', () => { readURL(); render(); });
}

(async function main() {
  DB = await (await fetch('data/notes.json')).json();
  readURL();
  if (state.id && !DB.notes.some((n) => n.id === state.id)) state.id = null;
  wire();
  render();
  writeURL();
}());
