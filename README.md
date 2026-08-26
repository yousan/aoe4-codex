# aoe4units

Age of Empires IV のユニットデータを、時代・生産施設ごとに並べて見るための静的サイト。
1ユニット＝1カードで、HP / 攻撃 / DPS / 射程 / 防御 / コスト / ダメージボーナス を一覧できる。

## ページ

| ファイル | 内容 |
| --- | --- |
| `index.html` | 目次 |
| `aoe4-od-matrix.html` | ドラゴン騎士団: 生産施設 × 時代 のマトリクス（施設の中はユニット系統ごとの列） |
| `aoe4-od.html` | ドラゴン騎士団: 時代ごとのユニット一覧 |
| `aoe4-units.html` | 全23文明・605行のテーブル（絞り込み / 列ソート / CSV書き出し） |
| `aoe4-card.html` | カードデザインの検討ページ（アイコン凡例つき） |

各ページは単体で完結した HTML で、データも CSS も埋め込み済み。外部から読むのはユニットの
アイコン画像だけ（`data.aoe4world.com`）。

- ホバーで用語のツールチップが出る（属性・コスト内訳・ボーナスの対象）
- 右上の印刷ボタンで A4 横に最適化して印刷できる（画面用の横長レイアウトとは別に、
  印刷時は 1施設＝1ページ に組み替わる）

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
./tools/fetch.sh              # 元データを data/units-all.json に取得
python3 tools/build_cards.py  # aoe4-card.html
python3 tools/build_civ.py od # aoe4-od.html
python3 tools/build_matrix.py od  # aoe4-od-matrix.html
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
