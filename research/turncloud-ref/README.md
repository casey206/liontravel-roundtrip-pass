# TurnCloud × The Pocket Company — Launch Presentation

這個 repo 是 **The Pocket Company（Accucrazy）加入騰雲 TurnCloud** 發表會的線上簡報與相關案例資料的 **唯一正式來源（canonical source）**。

> 規矩一句話：**GitHub 上的這份 repo 就是正確版本。** 任何地方（網域、VM、其他 repo）如果跟這裡不一致，以這裡為準，並把那邊同步回來。

---

## 1. 線上位置（兩個部署，內容必須一致）

| 位置 | URL | 由誰提供 |
|---|---|---|
| 自訂網域 | https://turncloud.thepocket.company/ | GCP VM（nginx，`/var/www/deck/`） |
| GitHub Pages | https://accucrazy.github.io/turncloud-presentation/ | 本 repo（`main` 分支） |

**兩邊內容必須一致**，且都等於本 repo `main` 的最新狀態。更新流程見第 4 節。

---

## 2. 正確版本與最新進度（很重要）

- **主視覺發表會 deck = repo 根目錄的 `index.html`**（標題：`Enterprise AIOS — 我們想要一起長大的生態系`，署名 Ian Wu · CEO Accucrazy）。
- **目前 24 頁**，敘事弧：Cover → Trailer 預告 → 三層架構（Runtime→AI OS→Agents）→ One OS·Two Spaces → 5 位 AI 員工總覽 → Harness 主圖 → 五位 Agent 逐一登場（人物頁＋live demo）→ 開放生態系（Raccoon/Rytho/Luna/CUHK）→ Finale → One More Thing（送 100 點 Banana Split）。**逐頁清單見 [`SLIDE_FRAMEWORK.md` §1.5](./SLIDE_FRAMEWORK.md#15-memory-最新版投影片進度current-deck-inventory)。**
- 「正確基準」歷史起點是 commit **`8aba57a`**（`Add 'one more thing' redeem slide with QR…`，含 trailer 片頭、redeem/QR 頁、生態系內容），之後又經多次更新；**最新 commit `35950a9`（2026-06-23）**換上新的 Culture Listening / Motion Lab / Reels Studio demo `.mov`。英文版 `tpc-launch-en/` 同為 24 頁，內容同步。
- 過去曾有一份 **不同 repo（`turncloudlaunch` / `tpc-launch-deck/v2`）的舊分支** 被誤部署到網域上（缺 trailer + redeem）。**那份不是正確版本**，已被本 repo 的版本取代。
- 🔴 **建置來源已與正式 deck 脫鉤**：經 2026-06-23 核對，repo 內**沒有任何一份 `slides.yaml` 能重建出目前這份 24 頁 `index.html`**（`tpc-launch/slides.yaml`=26 頁、棄用的 `tpc-launch-deck/v2/`=27 頁，皆缺 trailer/redeem）。**正式 deck 目前是手動維護的單檔 HTML** ── 細節與修復計畫見 `SLIDE_FRAMEWORK.md` §0.5 與 §1.5。

---

## 3. 目錄結構

| 路徑 | 內容 |
|---|---|
| `index.html` | ⭐ 主發表會 deck（正確版本，24 頁 — 目前為**手動維護**，小改可直接編輯，大改見第 4 節） |
| `BRIEFING.md` | ⭐ 規矩 / 戰情手冊 ── 內容定位、敘事結構、講稿、商業模式、競品、CTA。建 deck 前先讀這份。 |
| `SLIDE_FRAMEWORK.md` | ⭐ Slide framework onboarding（Harness）── 給接手的 AI Agent / 工程師：版本規矩、template 參考、slides.yaml 語法、Gemini 生圖、部署 recipes。**動框架前先讀這份。** |
| `tpc-launch/` | deck 的建置專案：`slides.yaml`、`templates/`、`build.py`、`generate_*.py`。`tpc-launch/index.html` 已對齊根目錄正確版（資產以 `../img/` 指回根目錄）。 |
| `tpc-launch-en/` | 英文版發表會 deck（English version，內容同步自正確版）。 |
| `tengyun-report/` | 騰雲發表會 × Computex 口碑成效戰報（破百萬次觀看、含 Pandora 聲量轉位頁）。 |
| `img/` | 主 deck 用到的所有圖片與影片資產。 |
| `aios.html` · `slides/` · `sharing/` · `babycam-dtc/` · `assets/` | 其他相關簡報 / 分享頁 / 素材。 |

---

## 4. 怎麼改、怎麼建（建置規矩）

完整的框架說明（template 參考、`slides.yaml` 語法、Gemini 生圖、所有 recipes、**24 頁逐頁清單**）都在 **[`SLIDE_FRAMEWORK.md`](./SLIDE_FRAMEWORK.md)** — 這裡只講最重要的兩條：

1. **改正式 deck（含小改/大改）**：根目錄 `index.html` 與 `tpc-launch-en/index.html` 目前都是**手動維護的單檔 HTML**，請**直接編輯這兩份**，再 push + 同步 VM。
2. **🔴 不要用 `python build.py` 蓋正式 deck**：repo 內沒有任何 `slides.yaml` 對得起目前的 24 頁 canonical deck（`tpc-launch/slides.yaml`=26 頁、棄用的 `tpc-launch-deck/v2/`=27 頁，皆缺 trailer/redeem）。`build.py` 只用於 `tpc-launch/` 內的框架實驗，**產物絕不可覆蓋根目錄 `index.html`**。把建置來源校正回 canonical（或改用 CodyML）是 `CODYML_PLAN.md` Phase 0 的前置工作。

---

## 5. 部署（讓網域 + GitHub Pages 一致）

改完、commit 並 push 到 `main` 後：

1. **GitHub Pages** 會自動由 `main` 重新發佈（約 1–2 分鐘）。
2. **GCP VM（網域）** 需手動同步：把 `index.html` 與用到的 `img/` 資產上傳到 `reel-studio:/var/www/deck/`（root deck），`tengyun-report/`、`tpc-launch-en/` 同理放到對應子目錄。

部署後務必驗證：slide 數正確、`img/` 圖片 0 broken、影片可載入（HTTP 200）。

---

## 6. 一句話總結

> **Runtime 讓 AI 運行空間，AI OS 讓企業管理 AI，AI Agents 真正開始為企業工作。**
> 詳細敘事與所有數字、講稿，see **[`BRIEFING.md`](./BRIEFING.md)**；簡報系統、template、24 頁逐頁清單，see **[`SLIDE_FRAMEWORK.md`](./SLIDE_FRAMEWORK.md)**。

---

*Last updated · 2026-06-23 · canonical deck = 根目錄 `index.html`（24 頁，HEAD `35950a9`，手動維護）· build 來源已脫鉤，詳見 `SLIDE_FRAMEWORK.md` §0.5 / §1.5。*
