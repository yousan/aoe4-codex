# aoe4units

Age of Empires IV のユニットデータを、時代・生産施設ごとに並べて見るための静的サイト。
1ユニット＝1カードで、HP / 攻撃 / DPS / 射程 / 防御 / コスト / ダメージボーナス を一覧できる。

## 使い方

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

### 構成

```
index.html          画面の枠だけ
css/app.css         見た目（カード・マトリクス・印刷）
js/card.js          ユニットカード1枚の描画。全ビューで共通
js/views.js         マトリクス / 表 と、印刷用レイアウト
js/app.js           プルダウン・タブ・URL 同期
data/units.json     全605ユニット（表示用に整形した派生データ・241KB）
data/meta.json      文明名・施設名・アイコンのラベル
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
- 対応パッチ: **Season 13 / patch 16.1.9737**（元データの最終更新 2026-05-04）。
  それ以降のバランス調整は反映されていない
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

## 多言語表示

画面右上で **日本語 / English** を切り替える。初回はブラウザの言語設定に従い、選択は保存される。
URL にも入る（`?lang=en`）。

**方針: ゲーム内の表記に合わせる。独自訳はしない。** 語ごとの出どころは以下のとおり。

| 種類 | English | 日本語 |
| --- | --- | --- |
| ユニット名 | ゲームファイル由来（aoe4world/data が `LocaleEnglish.sga` を展開して生成） | コミュニティwiki（下記）。未確認のものは点線で **仮訳** と表示 |
| 建物・歴史的建造物名 | 同上（`buildings/all.json`） | 同上 |
| 属性・ステータス名 | ゲーム内のクラス表記（Heavy / Light / Melee / Ranged など） | ゲーム内表記（重装・軽装・近接・遠隔 など） |
| ボタンなどのUI文言 | このリポジトリ独自（ゲーム用語ではないため） | 同左 |

### 日本語を一次資料にするには

いまの日本語名は、ゲーム内表記を写した**コミュニティwiki経由**であって一次資料ではない。
公式表記を機械的に取り込むには、upstream と同じ手順を日本語ロケールで回す必要がある。

1. 自分の AoE4 インストールから `LocaleJapanese.sga` と `Attrib.sga` を取り出す
2. [AOEMods.Essence](https://github.com/aoemods/AOEMods.Essence) で展開する
3. aoe4world/data の抽出スクリプトを日本語ロケールで実行する

`units/all.json` には locstring ID が残っていないため、**名前だけを後から差し替えることはできない**。
（この作業をしていない現状は、上表のとおり出典を明示して区別している）

### 他の言語を足すには

`tools/build_data.py` の `UI` に言語を1つ足せば UI は増える。ただしユニット名・建物名は
上と同じ理由で、その言語のロケールから取り込む必要がある。**機械翻訳は入れない。**

### 日本語名

ゲーム内表記に合わせている。出典は
[AoE4 攻略wiki](https://aoe4.upgame.jp/) と AoE Haul wiki。
接頭辞は 黎明 / 初期 / 熟練 / ベテラン / 精鋭 / 竜(Gilded) のルールで自動展開。
公式表記を確認できなかったものは点線を引いて **仮訳** と明示している。

## ビルド

```bash
./tools/fetch.sh               # 元データとアイコンを取得
python3 tools/build_data.py    # data/units.json と data/meta.json を生成（アプリはこれを読む）

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
