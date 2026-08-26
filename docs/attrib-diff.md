# ゲーム本体との差分

- upstream: [aoe4world/data](https://github.com/aoe4world/data) （Season 13 / 16.1.9737、2026-05-04 更新）
- 手元のゲーム: `Attrib.sga` 2026-07-05 版
- 生成: `python3 tools/extract_attrib.py --diff --md`

## サイトに反映している差分

HP・攻撃力・防御は生の値をそのまま読めるので、**手元のゲームの値で上書きしている**。

### HP

| ユニット | upstream | 手元のゲーム |
| --- | --- | --- |
| Hardened Limitanei（by） | 100 | **105** |
| Torguud（gol） | 220 | **200** |
| Veteran Torguud（gol） | 260 | **240** |
| Elite Torguud（gol） | 300 | **280** |
| Yatai（sen） | 370 | **320** |

### 攻撃力

| ユニット | upstream | 手元のゲーム |
| --- | --- | --- |
| Bed Crossbow（jin） [Bed Crossbow] | 7 | **8.0** |
| Veteran Bed Crossbow（jin） [Bed Crossbow] | 9 | **10.0** |
| Elite Bed Crossbow（jin） [Bed Crossbow] | 12 | **13.0** |
| Mohe Tribesman（jin） [Bow] | 4 | **5.0** |
| Veteran Mohe Tribesman（jin） [Bow] | 6 | **7.0** |
| Elite Mohe Tribesman（jin） [Bow] | 7 | **8.0** |

### 防御: なし

## 反映していない差分

- コスト: 36 件 / 生産時間: 13 件 / 攻撃間隔: 53 件

これらは upstream 側が**文明ボーナスを織り込んだ値**を持っていることがあり（中国の造船が速い、フランスの騎兵が安い、など）、
こちらが読んでいる生値と食い違う。どちらが「表示すべき値」かは項目ごとに判断が要るので、いまは触っていない。

攻撃間隔については、連射武器（諸葛弩など）や設置が要る攻城兵器の扱いもまだ upstream と揃っていない。
