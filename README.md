# aoe4units

Age of Empires IV のユニットデータを、時代・生産施設ごとに並べて見るための静的サイト。
1ユニット＝1カードで、HP / 攻撃 / DPS / 射程 / 防御 / コスト / ダメージボーナス を一覧できる。

## 使い方

`index.html` が本体。ヘッダのプルダウンで**23文明**を切り替え、タブで**3つのビュー**を切り替える。

| ビュー | 内容 |
| --- | --- |
| 生産施設 × 時代 | 横が生産施設（中はユニット系統ごとの列）、縦が時代のマトリクス |
| 時代別一覧 | 時代ごとに、兵種で区切ってカードを並べる |
| 表 | 数値比較用。列見出しをクリックで並べ替え |

- 状態は URL に入る（`?civ=od&view=matrix`）。リロードしても戻るボタンでも復元される
- 右上の印刷ボタンで A4 横に最適化して印刷（マトリクスは **1施設＝1ページ**に組み替わる）
- ホバーで用語のツールチップ（属性・コスト内訳・ボーナスの対象）

### 構成

```
index.html          画面の枠だけ
css/app.css         見た目（カード・マトリクス・印刷）
js/card.js          ユニットカード1枚の描画。全ビューで共通
js/views.js         マトリクス / 一覧 / 表 と、印刷用レイアウト
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
