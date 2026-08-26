// 言語の切り替え。ゲーム内の用語は data/meta.json 側に持たせ、ここでは選ぶだけ。
let LANG = 'ja';
let UI = {};

export function setLang(lang, ui) { LANG = lang; if (ui) UI = ui; }
export const lang = () => LANG;

/** UI文言（アプリ側の言葉。ゲーム内用語ではない） */
export function t(key, vars) {
  let s = (UI[LANG] && UI[LANG][key]) || (UI.en && UI.en[key]) || key;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.replaceAll(`{${k}}`, v);
  return s;
}

/** {ja, en} 形式のラベルから現在の言語を取り出す */
export const L = (o) => (!o ? '' : (o[LANG] || o.en || o.ja || ''));
