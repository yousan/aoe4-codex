// ビュー（マトリクス / 時代別一覧 / 表）の描画
import { renderCard, ico, lineLabel } from './card.js';
import { t, lang, term, bldName, unitName } from './i18n.js';

const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export const MAIN_COLS = ['barracks', 'archery-range', 'stable', 'town-center'];
const FAM_ORDER = ['a-inf', 'a-cav', 'a-camel', 'a-eleph', 'a-siege', 'a-ship', 'a-relig', 'a-worker'];

const family = (u) => FAM_ORDER.find((f) => u.at.includes(f)) || '';

const ageCell = (meta, a) => (lang() === 'ja'
  ? `<span>第</span>${meta.roman[a]}<span>時代</span>`
  : `<span>${t('age')}</span>${meta.roman[a]}`);

function primary(u, cols) {
  // 町の中心を先に見る（農民・斥候をそこに寄せる）
  const order = cols.includes('town-center') ? ['town-center', ...cols] : cols;
  return order.find((b) => u.pb.includes(b)) || null;
}

function extras(u, meta, cols) {
  if (u.pb.some((b) => meta.unitBuilt.includes(b))) return [t('builtByUnits')];
  const out = u.pb
    .filter((b) => !cols.includes(b) && b !== 'capital-town-center' && meta.landmarks.includes(b))
    .map((b) => bldName(b));
  return [...new Set(out)];
}

/** 縦=時代 / 横=生産施設（施設の中はユニット系統ごとの列） */
export function renderMatrix(units, meta, { blds = null, bases = null } = {}) {
  const all = blds && blds.length ? blds : MAIN_COLS;
  if (bases) units = units.filter((u) => bases.includes(u.base));
  const cols = all.filter((b) => units.some((u) => primary(u, all) === b));
  const shown = units.filter((u) => cols.includes(primary(u, cols)));
  if (!shown.length) return `<p class="empty">${t('noUnits')}</p>`;

  const ages = [...new Set(shown.map((u) => u.age))].sort();
  const sub = {};       // 施設 → [[baseId, ラベル], ...]
  const cell = new Map(); // age|building|base → unit
  for (const b of cols) {
    const us = shown.filter((u) => primary(u, cols) === b);
    const lines = new Map();
    for (const u of us) {
      if (!lines.has(u.base)) lines.set(u.base, []);
      lines.get(u.base).push(u);
      cell.set(`${u.age}|${b}|${u.base}`, u);
    }
    sub[b] = [...lines.entries()]
      .map(([base, list]) => [base, lineLabel(list), Math.min(...list.map((x) => x.age))])
      .sort((a, x) => a[2] - x[2] || a[1].localeCompare(x[1], 'ja'));
  }

  const h1 = cols.map((b) => {
    const n = shown.filter((u) => primary(u, cols) === b).length;
    return `<th class="bld" colspan="${sub[b].length}">${esc(bldName(b))}<span>${n}</span></th>`;
  }).join('');
  const h2 = cols.flatMap((b) => sub[b].map(([, lbl]) => `<th class="ln">${esc(lbl)}</th>`)).join('');

  const rows = ages.map((a) => {
    const tds = cols.flatMap((b, ci) => sub[b].map(([base], si) => {
      const u = cell.get(`${a}|${b}|${base}`);
      const edge = (si === 0 && ci > 0) ? ' bl' : '';
      if (!u) return `<td class="${edge}"><span class="e">·</span></td>`;
      const ex = extras(u, meta, cols);
      return `<td class="${edge}">${renderCard(u, meta)}`
        + (ex.length ? `<div class="alt">＋ ${esc(ex.join('・'))}</div>` : '') + '</td>';
    })).join('');
    return `<tr><th class="age a${a}">${ageCell(meta, a)}</th>${tds}</tr>`;
  }).join('');

  return `<div class="mxwrap"><table class="mx">
    <thead><tr><th class="corner age" rowspan="2">${t('age')}</th>${h1}</tr><tr>${h2}</tr></thead>
    <tbody>${rows}</tbody></table></div>`;
}

const COLS = [
  ['jp', () => t('colUnit'), 'l'], ['age', () => t('colAge'), ''],
  ['hp', () => term('i-hp'), ''], ['d', () => t('colAtk'), ''],
  ['dps', () => 'DPS', ''], ['rng', () => term('i-range'), ''],
  ['s', () => term('i-int'), ''], ['am', () => term('i-armm'), ''],
  ['ar', () => term('i-armr'), ''], ['tot', () => t('colTot'), ''],
  ['pop', () => term('i-pop'), ''], ['t', () => term('i-time'), ''],
  ['mv', () => term('i-speed'), ''],
];
const val = (u, k) => ({
  jp: unitName(u), age: u.age, hp: u.hp,
  d: u.w?.d, dps: u.w?.dps, s: u.w?.s,
  rng: (u.w?.r1 >= 1) ? u.w.r1 : null,
  am: u.am, ar: u.ar, tot: u.cost.tot, pop: u.cost.pop, t: u.cost.t, mv: u.mv,
}[k]);

/** 表。数値の比較用 */
export function renderTable(units, meta, { sort = 'age', asc = true, bases = null } = {}) {
  const src = bases ? units.filter((u) => bases.includes(u.base)) : units;
  if (!src.length) return `<p class="empty">${t('noUnits')}</p>`;
  const rows = [...src].sort((a, b) => {
    const x = val(a, sort); const y = val(b, sort);
    if (typeof x === 'string' || typeof y === 'string') {
      return String(x ?? '').localeCompare(String(y ?? ''), 'ja') * (asc ? 1 : -1);
    }
    return (((x ?? -Infinity) - (y ?? -Infinity)) * (asc ? 1 : -1))
      || a.age - b.age || a.n.localeCompare(b.n);
  });
  const head = COLS.map(([k, lbl, cls]) =>
    `<th class="${cls} ${sort === k ? 'sorted ' + (asc ? 'asc' : '') : ''}" data-sort="${k}">${esc(lbl(meta))}</th>`).join('');
  const body = rows.map((u) => `<tr>
    <td class="l"><img class="tic" src="assets/units/${u.ic}" alt="" loading="lazy">
      <span class="nm">${esc(unitName(u))}</span>${
        unitName(u) !== u.n ? ` <span class="en">${esc(u.n)}</span>` : ''}</td>
    <td><span class="age a${u.age}">${meta.roman[u.age]}</span></td>
    ${COLS.slice(2).map(([k]) => `<td>${val(u, k) ?? '<span class="z">–</span>'}</td>`).join('')}
  </tr>`).join('');
  return `<div class="mxwrap"><table class="tbl"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

/** 印刷用: 1施設 = 1ページ（A4横に収まる幅）に組み替える */
export function renderPrintMatrix(units, meta, civName, { blds = null, bases = null } = {}) {
  const all = blds && blds.length ? blds : MAIN_COLS;
  if (bases) units = units.filter((u) => bases.includes(u.base));
  const cols = all.filter((b) => units.some((u) => primary(u, all) === b));
  const shown = units.filter((u) => cols.includes(primary(u, cols)));
  const ages = [...new Set(shown.map((u) => u.age))].sort();

  return cols.map((b) => {
    const us = shown.filter((u) => primary(u, cols) === b);
    const lines = new Map();
    for (const u of us) {
      if (!lines.has(u.base)) lines.set(u.base, []);
      lines.get(u.base).push(u);
    }
    const order = [...lines.entries()]
      .map(([base, list]) => [base, lineLabel(list), Math.min(...list.map((x) => x.age))])
      .sort((a, x) => a[2] - x[2] || a[1].localeCompare(x[1], 'ja'));
    const head = order.map(([, lbl]) => `<th class="ln">${esc(lbl)}</th>`).join('');
    const rows = ages.map((a) => {
      const tds = order.map(([base]) => {
        const u = us.find((x) => x.age === a && x.base === base);
        if (!u) return '<td><span class="e">·</span></td>';
        const ex = extras(u, meta, cols);
        return `<td>${renderCard(u, meta)}`
          + (ex.length ? `<div class="alt">＋ ${esc(ex.join('・'))}</div>` : '') + '</td>';
      }).join('');
      return `<tr><th class="age a${a}">${ageCell(meta, a)}</th>${tds}</tr>`;
    }).join('');
    return `<section class="psec"><h2 class="pt">${esc(civName)} — ${esc(bldName(b))}</h2>
      <table class="mx"><thead><tr><th class="corner age">${t('age')}</th>${head}</tr></thead>
      <tbody>${rows}</tbody></table></section>`;
  }).join('');
}

/** 施設ごとの「ユニット系統」の一覧（フィルタの選択肢に使う） */
export function availableLines(units, meta, blds) {
  const cols = (blds && blds.length) ? blds : MAIN_COLS;
  const shown = units.filter((u) => cols.includes(primary(u, cols)));
  const seen = new Map();
  for (const u of shown) {
    if (!seen.has(u.base)) seen.set(u.base, { list: [], b: primary(u, cols) });
    seen.get(u.base).list.push(u);
  }
  return [...seen.entries()]
    .map(([base, { list, b }]) => ({ base, b, age: Math.min(...list.map((x) => x.age)),
      label: lineLabel(list) }))
    .sort((x, y) => cols.indexOf(x.b) - cols.indexOf(y.b) || x.age - y.age
      || x.label.localeCompare(y.label, lang()));
}

/** その文明で実際に使われている生産施設（列の候補） */
export function availableBuildings(units, meta) {
  const all = meta.buildingOrder;
  const set = new Set();
  for (const u of units) {
    const p = primary(u, all);
    if (p) set.add(p);
  }
  return all.filter((b) => set.has(b));
}
