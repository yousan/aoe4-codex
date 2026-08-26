# aoe4units

Age of Empires IV のユニットデータを、時代・生産施設ごとに並べて見るための静的サイト。
1ユニット＝1カードで、HP / 攻撃 / DPS / 射程 / 防御 / コスト / ダメージボーナス を一覧できる。

## 使い方

`index.html` がユニット一覧、`maps.html` が**ランクマップ一覧**。

### ユニット一覧

`index.html` が本体。ヘッダのプルダウンで**23文明**を切り替え、タブで**3つのビュー**を切り替える。

| ビュー | 内容 |
| --- | --- |
| 生産施設 × 時代 | 横が生産施設（中はユニット系統ごとの列）、縦が時代のマトリクス |
| 表 | 数値比較用。列見出しをクリックで並べ替え |

**生産施設**と**ユニット系統**をチェックボックスで 絞り込める。
施設を外すとその列ごと消え、系統を外すとその縦1列だけ消える。選択は URL に入る
（`?b=barracks,stable&u=gilded-spearman,gilded-knight`）ので、絞り込んだ状態のまま共有できる。

- 状態は URL に入る（`?civ=od&view=matrix`）。リロードしても戻るボタンでも復元される
- 右上の印刷ボタンで A4 横に最適化して印刷（マトリクスは **1施設＝1ページ**に組み替わる）
- ホバーで用語のツールチップ（属性・コスト内訳・ボーナスの対象）
- **⚑ 間違いを報告** から GitHub の Issue を開ける。文明名・見ていたURL・対応パッチ・言語が
  最初から埋まった状態で立ち上がる（`data` ラベル付き）

### ランクマップ一覧

`maps.html`。現行のランクマッププールを 1v1 / チーム戦のタブで切り替えて、
マップごとに **聖地・集落交易所・聖遺物・羊・鹿・イノシシ・果実の茂み・黄金・石材** の数を出す。
1v1 は**資源配置のサンプル画像**（同じマップの生成例2パターン）付き。

- 鹿は「大(7頭) × 4群 = 28頭」のように、群れサイズと群れ数と総頭数を分けて出す
- 数値は**そのマップサイズでの実数**。wiki 側は `20/38/56/74` のように
  1v1/2v2/3v3/4v4 の4値で持っているので、そこから該当サイズを取り出している
- 資源データがまだ無いマップ（新しめのDLCマップ）は「資源データ未確認」と明示する。
  埋めずに空欄で出す

### 構成

```
index.html          ユニット一覧の枠
maps.html           ランクマップ一覧の枠
css/app.css         見た目（カード・マトリクス・マップ・印刷）
js/card.js          ユニットカード1枚の描画。全ビューで共通
js/views.js         マトリクス / 表 と、印刷用レイアウト
js/app.js           プルダウン・タブ・URL 同期
js/maps.js          ランクマップ一覧の描画
data/units.json     全605ユニット（表示用に整形した派生データ・241KB）
data/meta.json      文明名・施設名・アイコンのラベル
data/maps.json      ランクマッププールと各マップの資源データ
assets/maps/        資源配置のサンプル画像（1v1の生成例）
```

ビルド不要。素の ES modules と `fetch()` だけで動く。

### 静的版（旧）

データを HTML に埋め込んで生成した版も残してある。JS 無しで開ける。

| ファイル | 内容 |
| --- | --- |
| `aoe4-od-matrix.html` | ドラゴン騎士団: 生産施設 × 時代 |
| `aoe4-od.html` | ドラゴン騎士団: 時代ごとの一覧 |
| `aoe4-units.html` | 全23文明・605行のテーブル |
| `aoe4-card.html` | カードデザインの検討ページ |

## データについて

- 出典: [aoe4world/data](https://github.com/aoe4world/data) の `units/all.json`
  （ゲームファイルから自動抽出されたもの）。`data/units-all.json` としてリポジトリに含めている
- ユニットアイコンも同じ出典から `assets/units/` にミラーしている（396枚）。
  外部サイトへのホットリンクはしていないので、クローンすればオフラインでも完全に表示できる
- 構造（どの文明・時代・生産施設か）は upstream の **Season 13 / 16.1.9737**（2026-05-04）
- **HP・攻撃力・防御はゲーム本体の `Attrib.sga` から読み直している**ので、
  手元のインストールと同じ値になる（`tools/extract_attrib.py`）。
  差分は [docs/attrib-diff.md](docs/attrib-diff.md)
- コスト・生産時間・攻撃間隔は upstream のまま。upstream 側が文明ボーナスを織り込んだ値を
  持っていることがあり、生値と食い違うため
- 数値はすべて **基礎値**。技術アップグレード・文明ボーナス・オーラの類は含まない
- 再取得は `./tools/fetch.sh`（データとアイコンをまとめて更新する）

### 数値の扱いで気をつけていること

- **突進（チャージ）攻撃は通常攻撃と分けている**。同じユニットに `Sword` と `Lance` の
  ように2種類の武器が入っていることがあり、ダメージが大きい方を主武器にすると DPS が
  実態と乖離する（例: 竜騎士の DPS が 85.71 になる）。`attribName` に `charge` を含む
  武器は別枠にして、槍アイコンの行に威力だけ出している
- **派生武器ではなく基本武器を採用している**。竜軍兵は `Sword 17` / `Mace 18` / `Ax 18` /
  `Bludgeon 18` を持つが、ゲーム内表示は 17。`attribName` が短い方（＝派生でない方）を選ぶ
- **松明（対建物攻撃）は表示しない**
- **自爆ユニットの DPS は出さない**（爆破船は 95 ÷ 0.125秒 で無意味な値になる）

## マップデータについて

- **プールは毎月1日に自動ローテーションする**（2026-07-02 の変更）。
  「今月はこれ」という告知が公式から出ないので、
  [aoe4world の対戦API](https://aoe4world.com/api/v0/games) から直近のランク戦をサンプリングして、
  `leaderboard` が `rm_solo` / `rm_team` のものをマップ名で数えている。これが実測のプール
- 資源の数値と配置画像は [Age of Empires Series Wiki](https://ageofempires.fandom.com/wiki/Age_of_Empires_IV)（CC BY-SA 3.0）の
  `Infobox AoE4 map` から。**通常のページ取得は 403 で弾かれるので、公開の MediaWiki API を使っている**
- 配置画像は `AoE4 <Map> 1p2p Map Spawns.png`（1v1と2v2の生成例が2×2で入った画像）の
  上半分だけを切り出して `assets/maps/` に置いている
- マップ名の日本語表記は、ユニット名と同じく**ゲーム本体のロケールファイル**から抽出（`乾アラビア` / `隠された谷` / `聖遺物の川` など）。
  資源名も公式表記に合わせている（Trade Post = **集落交易所**、Berry Bush = **果実の茂み**、Stealth Forest = **不可視の森**）
- 更新は `python3 tools/build_maps.py`。プール・資源データ・画像・日本語名を全部取り直す。
  **月初のローテーション後に走らせる**
- 手書きの解説文だけは `tools/maps-notes.ja.json` に分けてある（数値は書かない。数値は必ず wiki 由来）

## 多言語表示

画面右上のプルダウンで **14言語**を切り替える。初回はブラウザの言語設定に従い、選択は保存される。
URL にも入る（`?lang=ko`）。

日本語 / English / 한국어 / 简体中文 / 繁體中文 / Deutsch / Español / Français / Italiano /
Polski / Português (BR) / Русский / Türkçe / Tiếng Việt

### 訳していない。ゲームから取り出している

ユニット名・建物名・文明名・属性名は、**ゲーム本体のロケールファイルから抽出した公式表記**を
そのまま出している。手訳も機械翻訳も入れていない。

やっていること:

1. `cardinal/archives/Locale*.sga` を開く（全25言語ぶん同梱されている）
2. 中の zlib ストリームを展開すると UCS（`文字列ID<TAB>文字列` の UTF-16LE）が出てくる
3. **英語の文字列 → その文字列ID → 各言語の文字列** と辿る
   （こちらは既に英語名を持っているので、これだけで全言語が引ける）

```bash
python3 tools/extract_locale.py            # 要: AoE4 のインストール
python3 tools/build_data.py                # data/i18n/<lang>.json を生成
```

抽出結果は `data/locale-raw/<lang>.json`、表示用に UI文言を足したものが `data/i18n/<lang>.json`。
日本語の対応表は読みやすい形でも置いてある → **[docs/glossary.ja.md](docs/glossary.ja.md)**
（ユニット369件・文明23・施設・属性の English ↔ 日本語）。
**ゲーム本体が無くても生成済みのファイルがリポジトリに入っている**ので、開発には要らない。

| 種類 | 出どころ |
| --- | --- |
| ユニット名・建物名・文明名 | ゲームのロケールファイル（369件中359件が一致。残りは英語のまま） |
| 属性・ステータス名 | 同上（`Melee Armor` → `近接戦装甲` など） |
| ゲームに対応する語が無いもの | `DPS` / 生産時間 / 象 の3つだけ、こちらで補っている |
| ボタンなどのUI文言 | このリポジトリ独自。日本語と英語のみで、他言語は英語にフォールバック |

この方式に変える前は日本語をコミュニティwikiから当てていたので、
`Veteran Spearman` を「ベテラン槍兵」と出していた。**正しくは「古参槍兵」**。
そういう取りこぼしが無くなった。

## ビルド

```bash
./tools/fetch.sh                          # 元データとアイコンを取得
python3 tools/extract_locale.py           # 各言語の公式表記（要: ゲーム本体）
python3 tools/extract_attrib.py --diff --md  # 現パッチの数値（要: ゲーム本体）
python3 tools/build_data.py               # data/units.json と data/i18n/*.json を生成

# 静的版（旧）を作り直すとき
python3 tools/build_cards.py
python3 tools/build_civ.py od
python3 tools/build_matrix.py od
```

`tools/aoe4lib.py` が共通部分（データ整形・アイコン・カード描画・CSS）を持っている。

## この先やりたいこと

- GitHub Pages で公開する
- カードなどの見た目を共通コンポーネント化し、ユニットのデータは JSON として分離する
  （現状は各 HTML にデータが埋め込まれていて、ページを増やすたびに重複する）
- 他の文明にも対応する（データ側は全23文明ぶん入っている）

## データの出典と権利

元データの [aoe4world/data](https://github.com/aoe4world/data) は README で
「All of this data is open source, you may use it in your projects, websites, and apps.」
と再利用を認めており、同時に Microsoft の
[Game Content Usage Rules](https://www.xbox.com/en-US/developers/rules) の遵守（＝非商用であること）を
条件としている。このリポジトリはその条件に従って、データとアイコンを同梱している。

> Age Of Empires 4 © Microsoft Corporation.
> aoe4units は Microsoft の "Game Content Usage Rules" に基づき Age of Empires IV のアセットを
> 利用して作成された非公式のファンツールで、Microsoft によって承認・提携されたものではありません。

日本語名の出典は [AoE4 攻略wiki](https://aoe4.upgame.jp/) と AoE Haul wiki。
