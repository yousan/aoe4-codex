// ランクマップ一覧。data/maps.json を読んで、プールごとにカードを並べる。
const $ = (s, r = document) => r.querySelector(s);
const el = (t, c, h) => { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; };

const POOLS = [
  { key: 'rm_solo', label: '1v1', size: '1v1', img: true },
  { key: 'rm_team', label: 'チーム戦', size: '2v2', img: false },
];

// 地形タグと、資源の内訳文字列を日本語にする。
// 資源名（果実の茂み・黄金・石材・不可視の森など）はゲーム内の公式表記に合わせている。
const FEAT_JA = {
  'Open': '開けた地形', 'Elevation': '高低差', 'River': '川', 'Hybrid': 'ハイブリッド',
  'Naval': '海', 'Choke Point': 'チョークポイント', 'Choke Points': 'チョークポイント',
  'Stealth Forest': '不可視の森', 'Stealth Forests': '不可視の森',
  'Extra Resources': '資源多め', 'Extra gold': '金多め', 'Extra Gold': '金多め',
  'Extra Wood': '木材多め', 'Less Wood': '木材少なめ',
};
// 「Large: 1 per player / Medium: 2 per player」のような内訳文字列を置き換える
const AMT_JA = [
  [/\bextra large\b/gi, '特大'], [/\bLarge\b/g, '大'], [/\bMedium\b/g, '中'],
  [/\bSmall\b/g, '小'], [/\bTiny\b/g, '極小'], [/\bMicro\b/g, '極小'],
  [/\bper player\b/gi, '/人'], [/\bDefault\b/gi, '基本'], [/\bVaries\b/gi, '変動'],
  [/\bbase\b/gi, '基本'], [/(\d) vs (\d)/g, '$1v$2'],
];
const feat = f => FEAT_JA[f] || f;
const amt = s => AMT_JA.reduce((a, [re, to]) => a.replace(re, to), s || '');

// 群れサイズの日本語。頭数は data 側の herdSizes に入っている
const HERD_JA = { micro: '極小', small: '小', medium: '中', large: '大', 'extra large': '特大' };

const ROWS = [
  ['sacredSites', '聖地', 'raw.sacredSites'],
  ['tradePosts', '集落交易所', 'raw.tradePosts'],
  ['relics', '聖遺物', 'raw.relics'],
  ['sheep', '羊', 'raw.sheep'],
];

let DATA = null;
let pool = 'rm_solo';

function dig(o, path) {
  return path.split('.').reduce((a, k) => (a == null ? a : a[k]), o);
}

function deerText(deer, herdSizes) {
  if (!deer || !deer.length) return null;
  const parts = deer.map(d => {
    const head = herdSizes[d.size];
    return `${HERD_JA[d.size] || d.size}(${head}頭) × ${d.herds}群`;
  });
  const total = deer.reduce((a, d) => a + d.head, 0);
  return { parts, total };
}

function card(m, size, withImg) {
  const b = m.bySize[size];
  const c = el('article', 'mcard');

  const hd = el('div', 'hd');
  hd.append(el('span', 'nm', `${m.ja || m.name}<span class="en">${m.name}</span>`));
  if (m.features.length) {
    const f = el('span', 'feat');
    m.features.forEach(x => {
      const chip = el('span', 'fchip', feat(x));
      if (feat(x) !== x) chip.title = x;   // 元の英語をツールチップに残す
      f.append(chip);
    });
    hd.append(f);
  }
  c.append(hd);

  if (withImg && m.img) {
    const fig = el('figure', 'mimg');
    const im = el('img');
    im.src = m.img;
    im.alt = `${m.ja || m.name} の資源配置サンプル（1v1の生成例2つ）`;
    im.loading = 'lazy';
    fig.append(im, el('figcaption', null, '1v1の生成例 2パターン'));
    c.append(fig);
  } else if (withImg) {
    c.append(el('div', 'noimg', '資源配置図なし'));
  }

  const st = el('div', 'mstats');
  for (const [key, label, rawPath] of ROWS) {
    const v = b[key];
    const raw = dig(m, rawPath);
    const shown = v != null ? v : (amt(raw) || '—');
    const r = el('div', 'mrow');
    r.append(el('span', 'k', label), el('span', 'v', String(shown)));
    if (v != null && raw && !/^\d+$/.test(raw)) r.dataset.tip = amt(raw);
    st.append(r);
  }

  const d = deerText(b.deer, DATA.herdSizes);
  const dr = el('div', 'mrow deer');
  dr.append(el('span', 'k', '鹿'),
    el('span', 'v', d ? `${d.total}頭` : (amt(m.raw.deer) || '—')));
  if (d) dr.append(el('span', 'sub', d.parts.join(' ＋ ')));
  st.append(dr);

  const br = el('div', 'mrow');
  br.append(el('span', 'k', 'イノシシ'), el('span', 'v', b.boar != null ? String(b.boar) : (amt(m.raw.boar) || '—')));
  st.append(br);
  c.append(st);

  const extra = [['果実の茂み', m.raw.berries], ['黄金', m.raw.gold], ['石材', m.raw.stone]]
    .filter(([, v]) => v);
  if (extra.length) {
    const ex = el('div', 'mextra');
    extra.forEach(([k, v]) => ex.append(el('div', null, `<b>${k}</b> ${amt(v)}`)));
    c.append(ex);
  }

  if (m.notes.length) {
    const ul = el('ul', 'mnotes');
    m.notes.forEach(n => ul.append(el('li', null, n)));
    c.append(ul);
  }

  const ft = el('div', 'mft');
  ft.append(el('a', null, 'wiki'));
  ft.querySelector('a').href = m.wiki;
  ft.querySelector('a').target = '_blank';
  ft.querySelector('a').rel = 'noopener';
  if (m.stub) ft.append(el('span', 'warn', '資源データ未確認'));
  c.append(ft);
  return c;
}

function render() {
  const p = POOLS.find(x => x.key === pool);
  const names = DATA.pools[p.key];
  const main = $('#main');
  main.textContent = '';

  const lead = el('div', 'mlead');
  lead.innerHTML = `<p><b>${DATA.rotation} のローテーション / ${names.length}マップ</b>
    　聖遺物は「基本3 + プレイヤー数」で決まるので、${p.label === '1v1' ? '1v1は基本5個' : 'サイズごとに増える'}。
    鹿の群れは 小=${DATA.herdSizes.small}頭 / 中=${DATA.herdSizes.medium}頭 / 大=${DATA.herdSizes.large}頭 /
    特大=${DATA.herdSizes['extra large']}頭。1頭あたり食料350、採集レート0.825/秒。</p>`;
  if (!p.img) lead.innerHTML += `<p class="warn">チーム戦は ${p.size} の数値で表示している。
    資源配置画像は1v1の生成例しか用意していないので、ここでは出していない。</p>`;
  main.append(lead);

  const grid = el('div', 'mgrid');
  names.forEach(n => {
    const m = Object.values(DATA.maps).find(x => x.name === n);
    if (m) grid.append(card(m, p.size, p.img));
  });
  main.append(grid);
  $('#count').textContent = `${names.length} マップ`;
}

function tabs() {
  const t = $('#views');
  POOLS.forEach(p => {
    const b = el('button', 'vtab' + (p.key === pool ? ' on' : ''), p.label);
    b.onclick = () => {
      pool = p.key;
      history.replaceState(null, '', `?pool=${p.key}`);
      tabs();
      render();
    };
    t.append(b);
  });
  if (t.children.length > POOLS.length) [...t.children].slice(0, -POOLS.length).forEach(x => x.remove());
}

const q = new URLSearchParams(location.search).get('pool');
if (POOLS.some(p => p.key === q)) pool = q;

fetch('data/maps.json')
  .then(r => r.json())
  .then(d => {
    DATA = d;
    $('#rot').textContent = `${d.rotation} 時点`;
    $('#views').textContent = '';
    tabs();
    render();
  })
  .catch(e => { $('#main').innerHTML = `<p class="empty">data/maps.json が読めなかった: ${e}</p>`; });

$('#print').onclick = () => window.print();
