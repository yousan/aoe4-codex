// 言語の切り替え。ユニット名・建物名・属性名はゲーム本体から抽出した公式表記
// （data/i18n/<lang>.json）を読むだけで、こちらでは訳さない。
let LANG = 'ja';
let D = { ui: {}, units: {}, buildings: {}, civs: {}, terms: {} };

export async function loadLang(lang) {
  const r = await fetch(`data/i18n/${lang}.json`);
  if (!r.ok) throw new Error(`no locale: ${lang}`);
  D = await r.json();
  LANG = lang;
  document.documentElement.lang = lang;
}

export const lang = () => LANG;

/** UI文言（このサイトの言葉。ゲーム用語ではない） */
export function t(key, vars) {
  let s = (D.ui && D.ui[key]) || key;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.replaceAll(`{${k}}`, v);
  return s;
}

/** ゲーム内表記。無いものは英語のまま返す */
export const unitName = (u) => (D.units && D.units[u.n]) || u.n;
export const term = (key) => (D.terms && D.terms[key]) || key;
export const techName = (tech) => (D.techs && D.techs[tech.id]) || tech.n;
export const disclaimer = () => D.disclaimer || '';
export const uiIsFallback = () => !!D.uiIsFallback;

export function bldName(slug) {
  if (slug === '*other') return t('otherBuilding');
  if (D.buildings && D.buildings[slug]) return D.buildings[slug];
  return slug.split('-').map((w) => w[0].toUpperCase() + w.slice(1)).join(' ');
}

export function civLabel(code, meta) {
  return (D.civs && D.civs[code]) || (meta.civs[code] && meta.civs[code].en) || code;
}
