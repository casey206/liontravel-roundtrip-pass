# 雙程票 Round Trip Pass｜雄獅 × 日本百貨 × 騰雲 提案

雄獅旅遊與阪急阪神等日本百貨的雙向導購合作提案（騰雲 TurnCloud × Accucrazy）。

- 線上版：https://roundtrip-pass-proposal.pages.dev（Banner 全集：`/banners`）
- 成品：`deck.pptx`（含影片完整版）、`deck.pdf`、`deck.ppt`

## 主要檔案
| 路徑 | 內容 |
|---|---|
| `build_deck.py` | 簡報產生器（套用 `assets/tc_template.pptx` 騰雲公版） |
| `banner_tpl/make.py`・`compose.py` | Banner 品牌版型（靜態）與動態合成 |
| `mockups/` | 百貨官網、LionTrip App 的 mockup HTML |
| `index.html`・`banners.html` | 線上翻頁版與 Banner 展示頁 |
| `assets/` | 圖片、logo、主視覺、影片 |
| `research/` | Pandora 原始資料、UGC 截圖、參考素材 |
| `strategy.md` | 策略文件 |

## 重建
```bash
PYTHONPATH=~/.claude/skills/casey-deck/scripts ~/.claude/skills/casey-deck/.venv/bin/python build_deck.py
```
`render/`、`dist/`、`dl/`、`assets/slides*` 為建置產物，未入庫。

> Confidential｜示意數字與優惠內容待三方確認。
