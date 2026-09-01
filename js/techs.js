// テクノロジーの効果をユニットの数値に反映する。
// 効果の定義は data/techs.json（upstream の technologies/all.json 由来）。
const FIELD = {
  hitpoints: 'hp', meleeArmor: 'am', rangedArmor: 'ar',
  moveSpeed: 'mv', buildTime: 't',
  meleeAttack: 'd:melee', rangedAttack: 'd:ranged', siegeAttack: 'd:siege',
  attackSpeed: 's', maxRange: 'r1',
};

/** そのユニットに効くか */
export function affects(u, e) {
  if (e.ids && e.ids.includes(u.base)) return true;
  const tags = u.cls || [];
  return (e.cls || []).some((grp) => grp.every((alts) => alts.some((t) => tags.includes(t))));
}

/** 選んだテクノロジーのうち、そのユニットに効くものだけ返す */
export function techsFor(u, techs) {
  return techs.filter((t) => t.fx.some((e) => affects(u, e)));
}

/**
 * そのユニットに「その時代までに」乗せられるテクノロジー一式。
 * - 発動アビリティ・オーラ・一時的な効果（cond）は外す
 * - 上位版があるときは下位版を外す（士官学校 と 士官学校(改良) は重ならない）
 */
export function autoTechs(u, techs, civ) {
  const list = techs.filter((t) => !t.cond && t.civs.includes(civ) && t.age <= u.age
    && t.fx.some((e) => affects(u, e)));
  const ids = new Set(list.map((t) => t.id));
  return list.filter((t) => !ids.has(`${t.id}-improved`));
}

const r2 = (n) => Math.round(n * 1000) / 1000;

/** 数値のラベルに使うアイコンキー */
export const PROP_ICON = {
  hitpoints: 'i-hp', meleeArmor: 'i-armm', rangedArmor: 'i-armr', fireArmor: 'i-armm',
  meleeAttack: 'i-melee', rangedAttack: 'i-ranged', siegeAttack: 'i-siege',
  fireAttack: 'i-fire', attackSpeed: 'i-int', moveSpeed: 'i-speed',
  maxRange: 'i-range', buildTime: 'i-time',
};

/** そのユニットに実際に効く効果だけ返す（適用時と同じ条件で絞る） */
export function effectsFor(u, tech) {
  return tech.fx.filter((e) => affects(u, e)
    && FIELD[e.p]
    && !(e.p === 'attackSpeed' && e.e === 'multiply' && e.v > 1)
    && !(FIELD[e.p].startsWith('d:') && (!u.w || u.w.t !== FIELD[e.p].split(':')[1])));
}

/** 「+1」「×1.15」のような表記 */
export const fxText = (e) => (e.e === 'change'
  ? `${e.v > 0 ? '+' : ''}${e.v}` : `×${r2(e.v)}`);

/**
 * @returns {{u: object, mods: object|null}} mods は フィールド名 → [{n, txt}]
 */
export function applyTechs(unit, techs) {
  if (!techs || !techs.length) return { u: unit, mods: null };
  const u = { ...unit, w: unit.w ? { ...unit.w } : null, cost: { ...unit.cost } };
  const mods = {};
  const note = (field, tech, txt) => {
    (mods[field] = mods[field] || []).push({ t: tech, txt });
  };

  for (const pass of ['change', 'multiply']) {
    for (const t of techs) {
      for (const e of t.fx) {
        if (e.e !== pass || !affects(u, e)) continue;
        // attackSpeed の multiply>1 は「別のボーナスを強化する」類で、
        // 攻撃間隔に直接掛けると逆に遅くなってしまうので外す
        if (e.p === 'attackSpeed' && e.e === 'multiply' && e.v > 1) continue;
        const f = FIELD[e.p];
        if (!f) continue;
        const [kind, need] = f.split(':');
        if (kind === 'd') {
          if (!u.w || u.w.t !== need) continue;
          u.w.d = pass === 'change' ? u.w.d + e.v : u.w.d * e.v;
          note('d', t, pass === 'change' ? `+${e.v}` : `×${e.v}`);
        } else if (kind === 's' || kind === 'r1') {
          if (!u.w || u.w[kind] == null) continue;
          u.w[kind] = pass === 'change' ? u.w[kind] + e.v : u.w[kind] * e.v;
          note(kind, t, pass === 'change' ? `${e.v > 0 ? '+' : ''}${e.v}` : `×${e.v}`);
        } else if (kind === 't') {
          u.cost = { ...u.cost, t: pass === 'change' ? u.cost.t + e.v : u.cost.t * e.v };
          note('t', t, pass === 'change' ? `+${e.v}` : `×${e.v}`);
        } else {
          if (u[kind] == null) continue;
          u[kind] = pass === 'change' ? u[kind] + e.v : u[kind] * e.v;
          note(kind, t, pass === 'change' ? `+${e.v}` : `×${e.v}`);
        }
      }
    }
  }

  if (u.hp != null) u.hp = Math.round(u.hp);
  for (const k of ['am', 'ar']) if (u[k] != null) u[k] = Math.round(u[k]);
  if (u.mv != null) u.mv = r2(u.mv);
  u.cost.t = r2(u.cost.t);
  if (u.w) {
    u.w.d = Math.round(u.w.d);
    u.w.s = r2(u.w.s);
    if (u.w.r1 != null) u.w.r1 = r2(u.w.r1);
    u.w.dps = u.w.s ? Math.round((u.w.d / u.w.s) * 100) / 100 : u.w.dps;
    if (mods.d || mods.s) mods.dps = [...(mods.d || []), ...(mods.s || [])];
  }
  return { u, mods: Object.keys(mods).length ? mods : null };
}
