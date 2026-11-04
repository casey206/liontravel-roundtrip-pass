"""騰雲 × 雄獅 × 日本百貨｜雙程票 Round Trip Pass v2 — PPTX builder (deck_v2)"""
import os, unicodedata
from deck_v2 import Deck, W, H, FRAME, _rgb
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

IMG, VID = "assets/img/", "assets/video/"
FONT = os.environ.get("DECK_FONT", "Noto Sans TC")
d = Deck(frame="#F03742", accent="#FF8400", dark="#1E1A1D", gold="#FFD3A3",
         f_head=FONT, f_body=FONT, f_num="Arial Narrow")
d.footer = "© TurnCloud 騰雲 × 雄獅旅遊｜Confidential"
SOFT = _rgb("#FFF1F2")
LION, TC, DEPT = _rgb("#1DB7D3"), _rgb("#FFC000"), _rgb("#C8102E")   # 三方色碼，沿用騰雲合作示意圖
GREY = _rgb("#F6F4F4")
PAGE_MAP = {}   # 頁碼 → 影片，給 HTML 版疊動態用


# ---------------------------------------------------------------- helpers
def _w(text, per_cjk=0.155, per_lat=0.085):
    return sum(per_cjk if unicodedata.east_asian_width(ch) in "WF" else per_lat for ch in text)


def label(s, text, dark_bg=False, x=0.42, y=0.34):
    w = 0.36 + _w(text, 0.16, 0.09)
    d._round(s, x, y, w, 0.32, "frame" if not dark_bg else "accent", 0.5)
    d._tx(s, x, y + 0.045, w, 0.24, text, 11, color="white", bold=True, align=PP_ALIGN.CENTER)
    return y + 0.32
d._label = label


def fit(s, path, x, y, w, h, border=False):
    """等比縮放放進框內，不裁切。"""
    iw, ih = Image.open(path).size
    r = min(w / iw, h / ih)
    pw, ph = iw * r, ih * r
    px, py = x + (w - pw) / 2, y + (h - ph) / 2
    if border:
        d._rect(s, px - 0.03, py - 0.03, pw + 0.06, ph + 0.06, _rgb("#E2E2E2"))
    s.shapes.add_picture(path, Inches(px), Inches(py), Inches(pw), Inches(ph))
    return px, py, pw, ph


def movie(s, path, poster, x, y, w, h):
    s.shapes.add_movie(path, Inches(x), Inches(y), Inches(w), Inches(h),
                       poster_frame_image=poster, mime_type="video/mp4")
    PAGE_MAP[d.n] = (os.path.basename(path), x / W, y / H, w / W, h / H)


def ai_tag(s, x, y, dark=False, text="AI 示意圖"):
    w = 0.3 + _w(text, 0.13, 0.075)
    d._round(s, x, y, w, 0.26, _rgb("#000000") if not dark else _rgb("#FFFFFF"), 0.5)
    d._tx(s, x, y + 0.04, w, 0.2, text, 8.5, color="white" if not dark else "ink", bold=True,
          align=PP_ALIGN.CENTER)


def foot(s, dark=False):
    on_banner = any(abs(sh.top - Inches(H - 0.78)) < 2000 and sh.width >= Inches(W - 0.01)
                    for sh in s.shapes)
    if on_banner:
        d._tx(s, W - 1.0, H - 0.36, 0.6, 0.22, str(d.n), 8, color="white", align=PP_ALIGN.RIGHT)
    else:
        d._foot(s, dark)


def tag(s, x, y, text, col="frame", size=11.5, h=0.42, fg="white"):
    tw = 0.4 + _w(text, 0.17, 0.095)
    d._rect(s, x, y, tw, h, col)
    d._tx(s, x + 0.2, y + (h - 0.28) / 2 + 0.02, tw - 0.3, 0.28, text, size, color=fg, bold=True)
    return tw


def arrow(s, x, y, w, h, color="frame", shape=MSO_SHAPE.RIGHT_ARROW):
    a = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = d.c[color] if isinstance(color, str) else color
    a.line.fill.background(); a.shadow.inherit = False
    return a


def circle_num(s, x, y, n, col="frame", size=0.42):
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(size), Inches(size))
    o.fill.solid(); o.fill.fore_color.rgb = d.c[col] if isinstance(col, str) else col
    o.line.fill.background(); o.shadow.inherit = False
    d._tx(s, x, y + size * 0.16, size, size * 0.7, str(n), 12, color="white", bold=True,
          align=PP_ALIGN.CENTER, font=d.f["num"])


def callouts(s, x, y, w, items, start=1, col="frame", gap=1.35):
    for i, (t, sub) in enumerate(items):
        yy = y + i * gap
        circle_num(s, x, yy, start + i, col)
        d._tx(s, x, yy + 0.52, w, 0.4, t, 12.5, bold=True, spacing=1.2)
        d._tx(s, x, yy + 0.86, w, 0.6, sub, 9.5, color="mid", spacing=1.35)


def num_card(s, x, y, w, big, lab, sub="", color="frame", h=2.3):
    d._rect(s, x, y, w, h, GREY)
    d._rect(s, x, y, w, 0.08, color)
    d._tx(s, x + 0.25, y + 0.3, w - 0.5, 0.9, big, 44, color=color, bold=True, font=d.f["num"])
    d._tx(s, x + 0.25, y + 1.25, w - 0.5, 0.4, lab, 13, bold=True)
    if sub:
        d._tx(s, x + 0.25, y + 1.65, w - 0.5, 0.6, sub, 10, color="mid", spacing=1.35)


def bars(s, items, x, y, w, row_h=0.5, hot=None, unit="篇", name_w=1.9, size=12):
    maxv = max(v for _, v in items)
    for i, (name, v) in enumerate(items):
        yy = y + i * row_h
        d._tx(s, x, yy + 0.06, name_w, 0.3, name, size, bold=True, align=PP_ALIGN.RIGHT)
        bw = (w - name_w - 1.4) * v / maxv
        d._rect(s, x + name_w + 0.15, yy + 0.05, max(0.05, bw), row_h - 0.16,
                "frame" if (hot is None or i in hot) else _rgb("#D9D2D3"))
        d._tx(s, x + name_w + 0.25 + bw, yy + 0.06, 1.3, 0.3, f"{v:,} {unit}", 11, color="mid",
              bold=True, font=d.f["num"])


def box(s, x, y, w, h, fill, title, sub="", fg="white", subc=None, tsize=14, radius=0.12):
    d._round(s, x, y, w, h, fill, radius)
    d._tx(s, x + 0.12, y + 0.16, w - 0.24, 0.9, title, tsize, color=fg, bold=True,
          align=PP_ALIGN.CENTER, spacing=1.2)
    if sub:
        d._tx(s, x + 0.12, y + 0.7, w - 0.24, h - 0.8, sub, 11, color=subc or fg,
              align=PP_ALIGN.CENTER, spacing=1.4)


_orig_table = d.table
def big_table(*a, size=14, row_h=0.6, **k):
    s = _orig_table(*a, **k)
    gt = [sh for sh in s.shapes if sh.has_table][-1].table
    for r_i, row in enumerate(gt.rows):
        row.height = Inches(row_h if r_i else 0.55)
        for c in row.cells:
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_left = c.margin_right = Inches(0.14)
            for para in c.text_frame.paragraphs:
                for r in para.runs:
                    r.font.size = Pt(size)
    return s
d.table = big_table


def social_idea(code, channel, title, desc, img=None):
    s = d._slide("dark")
    ih = 5.3
    d._pic(s, img, 0, 0, W, ih, dim=0.08)
    tw = tag(s, 0.62, ih - 0.7, "Social Idea " + code)
    tag(s, 0.62 + tw, ih - 0.7, channel, col="dark")
    d._rect(s, 0, ih, W, H - ih, "dark")
    d._tx(s, 0.7, ih + 0.25, W - 1.4, 0.5, title, 22, color="white", bold=True)
    d._tx(s, 0.7, ih + 0.85, W - 1.4, 1.0, desc, 12.5, color="gold", spacing=1.5)
    foot(s, True)
    return s


def demo(title, lab, img, left, right, banner, video=None, poster=None):
    """DEMO 頁：中間整張示意圖（等比、不裁切），兩側編號註解。"""
    s = d.info(title, label=lab, banner=banner)
    px, py, pw, ph = fit(s, img, 2.3, 1.5, 8.75, 4.75)
    if video:
        movie(s, video, poster, px, py, pw, ph)
    ai_tag(s, px + 0.12, py + 0.12, text="AI 示意影片" if video else "AI 示意圖")
    callouts(s, 0.45, 1.6, 1.75, left, 1)
    callouts(s, 11.2, 1.6, 1.8, right, len(left) + 1)
    foot(s)
    return s


def scenario(title, lab, steps, banner, db_text):
    s = d.info(title, label=lab, banner=banner)
    n = len(steps)
    cw = (W - 1.5 - (n - 1) * 0.5) / n
    for i, (head, col, img, cap) in enumerate(steps):
        x = 0.72 + i * (cw + 0.5)
        fg = "ink" if col == TC else "white"
        d._round(s, x, 1.5, cw, 3.4, col, 0.06)
        d._tx(s, x + 0.1, 1.58, cw - 0.2, 0.35, head, 13, color=fg, bold=True, align=PP_ALIGN.CENTER)
        d._rect(s, x + 0.12, 1.98, cw - 0.24, 2.3, _rgb("#FFFFFF"))
        fit(s, IMG + img, x + 0.16, 2.02, cw - 0.32, 2.22)
        d._tx(s, x + 0.12, 4.38, cw - 0.24, 0.5, cap, 10, color=fg, align=PP_ALIGN.CENTER, spacing=1.3)
        if i < n - 1:
            arrow(s, x + cw + 0.06, 3.0, 0.38, 0.3, color="frame")
        d._rect(s, x + cw / 2 - 0.02, 4.9, 0.04, 0.25, col)
    cyl = s.shapes.add_shape(MSO_SHAPE.CAN, Inches(1.4), Inches(5.1), Inches(W - 2.8), Inches(1.1))
    cyl.fill.solid(); cyl.fill.fore_color.rgb = LION; cyl.line.fill.background(); cyl.shadow.inherit = False
    d._tx(s, 1.4, 5.48, W - 2.8, 0.6, db_text, 13, color="white", bold=True, align=PP_ALIGN.CENTER, spacing=1.3)
    foot(s)
    return s


def shift_down(s, dy=0.28, above=1.1, below=6.6):
    """把標題下方的內容整體下移（橫幅與頁尾不動）。"""
    for sh in s.shapes:
        if Inches(above) < sh.top < Inches(below):
            sh.top = sh.top + Inches(dy)


# ================================================================ 01 封面
s = d._slide("dark")
d._pic(s, IMG + "cover.jpg", 0, 0, W, H)
g = d._rect(s, 0, 0, 8.6, H, _rgb("#000000"))
d._lin_grad(g, [("1E1A1D", 88000, 0), ("1E1A1D", 70000, 45000), ("1E1A1D", 0, 100000)], angle=0)
d._rect(s, 0, 0, 0.2, H, "frame")
d._tx(s, 1.05, 1.15, 7.0, 0.4, "TURNCLOUD × LION TRAVEL × 日本百貨", 15, color="accent", bold=True)
d._tx(s, 1.0, 1.7, 7.0, 1.6, "雙程票", 96, color="white", bold=True)
d._tx(s, 1.05, 3.45, 7.0, 0.7, "台日百貨雙向導購計畫", 32, color="white", bold=True)
d._rect(s, 1.05, 4.5, 0.72, 0.06, "frame")
d._tx(s, 1.05, 4.7, 7.0, 0.4, "Partnership Proposal｜騰雲 T-Space 導購平台", 15, color="gold", bold=True)
d._tx(s, 1.05, 5.25, 7.0, 0.3, "2026.11", 12, color="white", font=d.f["num"])
d._tx(s, 1.05, 5.65, 7.0, 0.8, "提案對象：阪急阪神百貨 經營層 ／ 雄獅旅遊 經營層\n提案單位：騰雲 TurnCloud", 11,
      color="white", spacing=1.5)
ai_tag(s, W - 1.3, H - 0.5, dark=True)

# ================================================================ 02 一頁看懂
s = d.info("一頁看懂：讓兩邊的客人，互相變成對方的客人", label="Executive Summary",
           banner="雄獅與百貨各開一扇門，中間的系統、數據、推廣與結算，全部交給騰雲")
cols = [("機會", LION, "台灣客是日本百貨最穩的客人",
         "673 萬人次・在日消費 1.2 兆日圓\n11/1 退稅新制縮水，優惠成了新決策點\n日本人訪台只有台灣人訪日的 1/4.5"),
        ("解法", TC, "騰雲 T-Space 雙程票",
         "去程：雄獅 App → 日本百貨 95折＋免稅\n回程：百貨官網・立牌・催事 → LionTrip\n領券、核銷、回訪全部記進 TCRM"),
        ("收益", DEPT, "按成果分潤，三方都有帳",
         "百貨：多一條穩定的台灣客源\n雄獅：海外會員＋落地消費入口\n騰雲：CPC＋GMV 分潤（試算 ¥6,700 萬／年）")]
cw = (W - 1.5) / 3 - 0.2
for i, (k, col, t, body) in enumerate(cols):
    x = 0.72 + i * (cw + 0.3)
    d._rect(s, x, 1.45, cw, 4.55, GREY)
    d._rect(s, x, 1.45, cw, 0.62, col)
    d._tx(s, x + 0.3, 1.58, cw - 0.6, 0.4, k, 17, color="ink" if col == TC else "white", bold=True)
    d._tx(s, x + 0.3, 2.35, cw - 0.6, 0.9, t, 19, bold=True, spacing=1.3)
    d._tx(s, x + 0.3, 3.45, cw - 0.6, 2.4, body, 12.5, color="mid", spacing=1.75)
foot(s)

# ================================================================ 03 機會①
s = d.info("機會①　台灣客，是日本百貨最穩的客人", label="核心與機會",
           banner="中國客退潮的年代，台灣客是最該經營的那一塊",
           source="Data source: 台灣觀光統計 2025（やまとごころ）；觀光廳 訪日外國人消費動向調查 2025（xmy.tw 整理）；"
                  "H2O リテイリング 2026/6 売上速報；訪日ラボ 2026/05/20；JNTO 2025（旅報 ttnmedia）")
cw = (W - 1.5) / 4 - 0.15
for i, (b, l, sub, col) in enumerate([
        ("673萬", "2025 訪日台灣旅客", "在日消費 1.2 兆日圓，全球第二", "frame"),
        ("32.9%", "花在購物的比例", "台灣客的錢，有三分之一進了商店", "frame"),
        ("117.1%", "阪急本店 2026/6 營收", "免稅營收約 +3 成，6 個月連續創新高", "frame"),
        ("−4成", "H2O 中國客數（通年）", "入境營收 −2 成；台灣・香港・韓國持續成長", "dark")]):
    num_card(s, 0.72 + i * (cw + 0.2), 1.45, cw, b, l, sub, color=col, h=2.5)
d._tx(s, 0.75, 4.3, W - 1.5, 1.2, "42% 的台灣旅客已經去過日本 6 次以上。\n他們不缺去日本的理由，缺的是「這次去哪裡買、怎麼買最划算」。",
      15, bold=True, spacing=1.6)
foot(s)

# ================================================================ 04 機會②
s = d.info("機會②　退 10% 的好日子過去了，優惠成了新的決策點", label="核心與機會",
           banner="11/1 起先付後退：台灣人還是會買，只是更會算",
           source="UGC: threads.com/@linshibi/post/Dc8fX1kGqn0（52.1 萬瀏覽）；threads.com/@taiwan_japanticket/post/De_AVqZk9Lr　爬取日 2026/11/02")
fit(s, IMG + "ugc/u1-linshibi.png", 0.7, 1.5, 4.0, 4.6, border=True)
fit(s, IMG + "ugc/u4-newrule.png", 4.95, 1.5, 3.3, 4.6, border=True)
d._tx(s, 8.65, 1.45, 4.0, 4.5,
      "570 日圓的稅金，\n退回來只剩 238 日圓。\n\n52.1 萬人看過這篇。\n\n退稅縮水的那一塊，\n正好是「台灣客專屬禮遇」\n補得上的位置。", 15, bold=True, spacing=1.55)
foot(s)

# ================================================================ 05 機會③
s = d.info("機會③　台灣人逛日本百貨，靠的是網友攻略，不是百貨自己", label="核心與機會",
           banner="攻略在網友手上、優惠在櫃檯手上：中間缺一個專區",
           source="Pandora 社群聲量實測：日本百貨查詢 N=14,272（實際覆蓋 2026/06/15–11/01），阪急｜阪神子集 3,314 篇；"
                  "UGC: threads.com/@osaka_rental_car/post/DcfLv9AkfYs（9.76 萬瀏覽）")
fit(s, IMG + "ugc/u2-b1.png", 0.7, 1.5, 4.6, 4.6, border=True)
d._tx(s, 5.75, 1.5, 6.8, 0.4, "台灣社群聊阪急阪神，聊的是什麼（Pandora）", 13, color="frame", bold=True)
bars(s, [("阪神虎・甲子園", 969), ("B1 美食・伴手禮", 444), ("精品・美妝", 122),
         ("優惠・折扣", 101), ("退稅・免稅", 72)], 5.6, 2.05, 7.1, row_h=0.6, hot=[0, 1], name_w=1.8)
d._tx(s, 5.75, 5.15, 6.8, 0.9, "3,314 篇討論裡，百貨官方的聲音幾乎聽不到；\n「去哪買、有什麼優惠」全靠網友整理。", 12.5, bold=True, spacing=1.5)
foot(s)

# ================================================================ 06 機會④
s = d.info("機會④　回程是空白的：日本人來台灣，只有台灣人去日本的 1/4.5", label="核心與機會",
           banner="百貨的日本熟客，是雄獅國際版還沒打開的市場",
           source="Data source: travelvoice 2026/04/16（台灣觀光署 2025）；Pandora 2026/06/15–11/01；訪日ラボ 2026/10/01")
d._tx(s, 0.9, 1.35, 4.0, 0.4, "台灣 → 日本", 15, color="mid", bold=True)
d._tx(s, 0.85, 1.75, 5.0, 1.6, "673萬", 96, color="frame", bold=True, font=d.f["num"])
d._tx(s, 6.9, 1.35, 4.0, 0.4, "日本 → 台灣", 15, color="mid", bold=True)
d._tx(s, 6.85, 1.75, 5.0, 1.6, "148萬", 96, color="dark", bold=True, font=d.f["num"])
d._round(s, 4.95, 2.3, 1.7, 0.7, d.c["accent"], 0.5)
d._tx(s, 4.95, 2.42, 1.7, 0.45, "4.5 倍", 20, color="white", bold=True, align=PP_ALIGN.CENTER)
for i, (t, sub) in enumerate([("訪台日本人年增 12.4%", "成長比整體訪台市場更快，回程正在變大"),
                              ("阪神虎是台灣人的主場", "Pandora 969 篇討論；阪神虎和阪急阪神百貨同屬一個集團"),
                              ("地方百貨在苦戰", "大城市免稅成長、地方失速：雄獅的團體行程能把客人帶到地方")]):
    x = 0.72 + i * 4.0
    d._rect(s, x, 3.95, 3.8, 1.85, SOFT)
    d._rect(s, x, 3.95, 0.08, 1.85, "frame")
    d._tx(s, x + 0.3, 4.15, 3.4, 0.4, t, 14, bold=True)
    d._tx(s, x + 0.3, 4.65, 3.4, 1.0, sub, 11, color="mid", spacing=1.45)
foot(s)

# ================================================================ 07 三個切角
s = d.info("三個切角，收斂成一句話", label="切角 → Proposition",
           banner="Proposition｜出發前，就是熟客。")
cuts = [("切角 1｜退稅縮水", "出發前就領好禮遇", "雄獅 App 日本百貨優惠專區\n95折＋免稅，補回退稅縮水的那一塊"),
        ("切角 2｜資訊斷層", "把網友攻略，\n變成官方專區", "T-Space 活動頁整合 70 多家百貨\n優惠、櫃位、B1 地圖一次看完"),
        ("切角 3｜回程空白", "百貨熟客，\n變成雄獅會員", "百貨官網・館內立牌・催事導向 LionTrip\n日本點券與線上支付，訂台灣行程")]
cw = (W - 1.5) / 3 - 0.2
for i, (k, t, body) in enumerate(cuts):
    x = 0.72 + i * (cw + 0.3)
    d._rect(s, x, 1.45, cw, 4.6, GREY)
    tag(s, x, 1.45, k, col="dark", size=11, h=0.4)
    d._tx(s, x + 0.3, 2.2, cw - 0.6, 1.2, t, 21, color="frame", bold=True, spacing=1.3)
    d._tx(s, x + 0.3, 3.7, cw - 0.6, 2.2, body, 12.5, color="mid", spacing=1.7)
foot(s)

# ================================================================ 08 IDEA（動態）
s = d._slide("dark")
movie(s, VID + "planes.mp4", IMG + "idea-bg.jpg", 0, 0, W, H)
d._tx(s, 1.05, 1.85, 5.2, 0.34, "IDEA", 13, color="accent", bold=True)
d._tx(s, 1.02, 2.35, 6.0, 1.7, "雙程票\nRound Trip Pass", 40, color="white", bold=True, spacing=1.2)
d._tx(s, 1.05, 4.45, 5.4, 2.0, "一張票，兩個方向。\n去程：台灣客從雄獅 App 走進日本百貨。\n回程：百貨的日本熟客走進雄獅國際版。\n騰雲 T-Space 記下每一次進出，按成果分潤。",
      13.5, color="gold", spacing=1.75)

# ================================================================ 09 章節
d.divider("How it works.", "騰雲 T-Space 導購平台：兩個入口、一個中轉、全程可追蹤")

# ================================================================ 10 合作示意圖
s = d.info("合作示意圖：騰雲 T-Space 是相互導客的共通平台", label="商業模式",
           banner="台灣人顧客 → 日本百貨買免稅商品　｜　日本人顧客 → 雄獅國際會員買旅遊行程")
x0 = 9.2
for t, col in [("雄獅", LION), ("騰雲", TC), ("日本百貨業者", DEPT)]:
    x0 += tag(s, x0, 0.4, t, col=col, size=10, h=0.34, fg="ink" if col == TC else "white") + 0.08
d._tx(s, 0.62, 1.2, 3.5, 0.35, "雄獅集團", 14, bold=True)
for j, (t, img) in enumerate([("國際版 APP 會員\nLionTrip", "crops/lt-p1.jpg"), ("台灣版 APP 會員\n雄獅旅遊", "crops/tw-p1.jpg")]):
    y = 1.6 + j * 2.5
    d._round(s, 0.62, y, 3.3, 2.3, LION, 0.08)
    d._tx(s, 0.8, y + 0.2, 1.8, 0.8, t, 13, color="white", bold=True, spacing=1.3)
    fit(s, IMG + img, 2.5, y + 0.1, 1.35, 2.1)
d._round(s, 4.75, 2.45, 3.3, 2.3, TC, 0.12)
d._tx(s, 4.85, 2.7, 3.1, 1.1, "騰雲 T-Space\n導購平台", 22, color="ink", bold=True, align=PP_ALIGN.CENTER, spacing=1.2)
d._tx(s, 4.85, 3.85, 3.1, 0.8, "優惠專區・核銷・TCRM\nPandora・推廣・分潤結算", 10.5, color="ink", align=PP_ALIGN.CENTER, spacing=1.4)
arrow(s, 3.98, 2.3, 0.72, 0.32, color=DEPT, shape=MSO_SHAPE.LEFT_ARROW)
d._tx(s, 4.0, 1.55, 3.0, 0.6, "日本人顧客 → 成為雄獅\n國際會員・購買旅遊行程", 9.5, color=DEPT, bold=True, spacing=1.25)
arrow(s, 3.98, 4.6, 0.72, 0.32, color=LION)
d._tx(s, 4.0, 5.0, 3.0, 0.6, "台灣人顧客 → 導客至\n日本百貨・購買免稅商品", 9.5, color=LION, bold=True, spacing=1.25)
arrow(s, 8.1, 2.8, 0.65, 0.32, color=LION)
arrow(s, 8.1, 4.1, 0.65, 0.32, color=DEPT, shape=MSO_SHAPE.LEFT_ARROW)
d._rect(s, 8.85, 1.2, 3.95, 4.7, DEPT)
d._tx(s, 9.0, 1.27, 3.7, 0.3, "日本端百貨業者名單（共 70 多家）", 11, color="white", bold=True)
names = ["阪急阪神集團＊", "仙台三越", "藤崎＊", "薄井百貨", "京急百貨", "Saikaya", "丸廣百貨", "八木橋", "水戶京成百貨",
         "Suzuran", "岡島", "長野東急百貨", "井上", "遠鐵百貨", "名鐵百貨", "大和百貨", "山陽百貨",
         "津松菱", "金澤丸越百貨", "京阪百貨", "丸由", "天滿屋", "福屋", "伊予鐵高島屋", "高知大丸", "博多大丸",
         "井筒屋", "濱屋百貨", "鶴屋百貨＊", "TOKIWA", "山形屋", "Ryubo Industry", "櫻野百貨", "川德 等…"]
for i, n in enumerate(names):
    cx = 9.0 + (i // 17) * 1.87
    cy = 1.65 + (i % 17) * 0.24
    d._rect(s, cx, cy, 1.8, 0.22, _rgb("#FFFFFF"))
    d._tx(s, cx + 0.06, cy + 0.025, 1.72, 0.2, n, 8, color=DEPT if "＊" in n else "ink", bold="＊" in n)
d._tx(s, 8.85, 5.93, 4.0, 0.25, "＊ 先行示範點的可能合作對象", 9, color=DEPT, bold=True)
foot(s)

shift_down(s)

# ================================================================ 11 合作重點
s = d.info("合作重點：三方各自要做的事", label="商業模式")
for i, (col, t, pts, img) in enumerate([
        (LION, "雄獅｜國際版 APP 會員", ["日本版本點券服務", "日本版線上支付系統", "連結海外行程加值服務（食衣住行育樂）"], "crops/lt-p2.jpg"),
        (LION, "雄獅｜台灣版 APP 會員", ["T-Space 優惠連結專區", "導入 LION Pay 順利快速退稅", "台灣人旅日服務（食衣住行育樂）"], "crops/tw-p2.jpg")]):
    x, y, w, h = 0.62, 1.2 + i * 2.55, 4.1, 2.4
    d._rect(s, x, y, w, h, GREY)
    d._rect(s, x, y, w, 0.42, col)
    d._tx(s, x + 0.18, y + 0.08, w - 0.3, 0.3, t, 12, color="white", bold=True)
    fit(s, IMG + img, x + 0.1, y + 0.5, 1.0, 1.82)
    for k, p in enumerate(pts):
        d._rect(s, x + 1.25, y + 0.72 + k * 0.52, 0.1, 0.1, col)
        d._tx(s, x + 1.45, y + 0.6 + k * 0.52, w - 1.55, 0.5, p, 11, spacing=1.25)
for x, col, t, pts, img in [
        (4.95, TC, "騰雲｜LP T-Space", ["雙語優惠活動頁（中文／日文）", "優惠券發放、核銷、分潤結算", "TCRM 顧客標籤＋Pandora 情報"], "crops/tw-p3.jpg"),
        (8.88, DEPT, "日本端百貨業者", ["建立雄獅國際版 APP 專區及催事活動", "導客成功之分潤條件", "優惠專區核銷機制（Mobile POS／APP／立牌）"], "crops/jp-site.jpg")]:
    y, w, h = 1.2, 3.82, 4.95
    d._rect(s, x, y, w, h, GREY)
    d._rect(s, x, y, w, 0.42, col)
    d._tx(s, x + 0.18, y + 0.08, w - 0.3, 0.3, t, 12, color="ink" if col == TC else "white", bold=True)
    fit(s, IMG + img, x + 0.2, y + 0.6, w - 0.4, 2.3)
    for k, p in enumerate(pts):
        d._rect(s, x + 0.25, y + 3.25 + k * 0.55, 0.1, 0.1, col)
        d._tx(s, x + 0.45, y + 3.12 + k * 0.55, w - 0.6, 0.5, p, 11.5, spacing=1.25)
foot(s)

shift_down(s, 0.25)

# ================================================================ 12 騰雲角色
s = d.info("騰雲扮演的角色：中間那一段，全部交給我們", label="騰雲 TurnCloud",
           banner="雄獅與百貨只要各開一扇門，系統、數據、推廣、結算由騰雲一站負責")
mods = [("T-Space 導購平台", "雙語優惠活動頁、70 多家百貨優惠上架、專區版位管理"),
        ("內容與素材製作", "Banner、開屏、推播、立牌、催事物料，中日雙語一次做"),
        ("券務與核銷", "發券、防重複、Mobile POS／APP／立牌三種核銷"),
        ("LION Pay 退稅串接", "核銷資料直通退稅流程，台灣客少排一次隊"),
        ("TCRM 顧客360", "點擊、領券、核銷、回訪全部貼標，跨國會員不落地"),
        ("Pandora 雙邊情報", "台灣社群看日本百貨、日本社群看台灣旅遊，每週報告"),
        ("廣告推廣", "Meta／LINE／Google 雙邊投放，用核銷數據優化出價"),
        ("分潤結算與對帳", "CPC＋GMV 自動計算，三方月結報表與加盟店後台")]
cw, chh = (W - 1.5) / 4 - 0.15, 2.0
for i, (t, sub) in enumerate(mods):
    x = 0.72 + (i % 4) * (cw + 0.2)
    y = 1.5 + (i // 4) * (chh + 0.15)
    hot = i in (0, 4)
    d._rect(s, x, y, cw, chh, TC if hot else GREY)
    d._tx(s, x + 0.22, y + 0.18, 0.6, 0.4, f"{i + 1:02d}", 18, color="ink" if hot else "frame", bold=True, font=d.f["num"])
    d._tx(s, x + 0.22, y + 0.65, cw - 0.4, 0.4, t, 15, bold=True)
    d._tx(s, x + 0.22, y + 1.12, cw - 0.4, 0.9, sub, 10.5, color="ink" if hot else "mid", spacing=1.4)
foot(s)

# ================================================================ 13 情境①
scenario("運用情境①　經營台灣客：雄獅台灣版 App → 日本百貨", "情境① 去程",
         [("雄獅台灣版 App", LION, "crops/tw-p1.jpg", "首頁 Banner「日本百貨優惠專區」"),
          ("騰雲 T-Space 活動頁", TC, "crops/tw-p2.jpg", "70 多家百貨優惠，依地區篩選"),
          ("優惠券＋LION Pay", TC, "crops/tw-p3.jpg", "95折＋免稅 QR，一鍵快速退稅"),
          ("日本百貨 現場核銷", DEPT, "demo-pos.jpg", "Mobile POS／APP／立牌掃碼")],
         "核銷結果回寫，按成果分潤", "TCRM 顧客360 數據中心｜收集領取優惠／實際使用等顧客標籤")

demo("DEMO 1　廣告版位：推播、開屏、行程頁，三個時間點接住台灣客", "情境① DEMO", IMG + "demo-banners.jpg",
     [("出發前推播", "依訂單出發日與目的地，D-7 推「先領阪急阪神 95折」"),
      ("App 開屏", "全版 3 秒，主打「出發前，就是熟客。」")],
     [("行程頁內嵌", "大阪團、福岡團頁面直接帶券"),
      ("版位都在雄獅", "不用新增 App 功能，只接上 T-Space 連結")],
     "雄獅不用改 App，只要把現有版位接上 T-Space")
demo("DEMO 2　App 首頁 → 優惠專區 → 優惠券：三步領完", "情境① DEMO", IMG + "demo-tw-app.jpg",
     [("首頁輪播 Banner", "沿用雄獅現行紅色頂欄與圖示列"),
      ("T-Space 優惠專區", "阪急阪神、藤崎、鶴屋…依地區篩選")],
     [("優惠券＋QR", "95折＋免稅，櫃檯掃碼即核銷"),
      ("LION Pay 快速退稅", "核銷資料直通退稅流程")],
     "畫面照雄獅台灣版 App 現行介面設計，優惠內容為示意")
demo("DEMO 3　現場核銷：掃一下，三方同時看到這筆成交", "情境① DEMO", IMG + "demo-pos.jpg",
     [("Mobile POS 掃碼", "百貨用現有手持機或騰雲提供的機台"),
      ("立牌掃碼", "沒有 POS 的櫃位，顧客掃立牌自助核銷")],
     [("即時回寫", "核銷金額、櫃位、時間即時進 TCRM"),
      ("分潤依據", "這一筆就是 GMV 分潤的計算基礎")],
     "核銷那一秒，就是三方對帳的起點", video=VID + "pos.mp4", poster=VID + "pos-poster.jpg")
demo("DEMO 4　百貨每天看得到：T-Space 加盟店後台", "情境① DEMO", IMG + "demo-tspace-admin.jpg",
     [("本日消込・送客數", "每天看到雄獅導了多少台灣客"),
      ("店舗別成效", "梅田本店、阪神梅田、博多、MEN'S 分開看")],
     [("人氣クーポン", "哪張券最有效，下週就加碼"),
      ("今月の手数料", "分潤費用透明，月結對帳")],
     "日文後台給百貨、中文報表給雄獅，同一份數據")

# ================================================================ 情境②
scenario("運用情境②　經營日本客：日本百貨 → 雄獅國際版 LionTrip", "情境② 回程",
         [("百貨官網專區", DEPT, "crops/jp-site.jpg", "「台湾へ、ふらっと。」會員專區"),
          ("館內立牌・催事", DEPT, "demo-standee.jpg", "服務台立牌、台湾フェア掃碼"),
          ("騰雲 T-Space 日文頁", TC, "crops/lt-p1.jpg", "下載 LionTrip 領 ¥3,000"),
          ("LionTrip 國際版", LION, "crops/lt-p3.jpg", "日本點券＋線上支付訂行程")],
         "成交回寫，百貨也拿得到分潤", "TCRM 顧客360 數據中心｜百貨熟客 → 雄獅國際會員，來源可追蹤")

demo("DEMO 5　百貨官網：在日本熟客最信任的地方，放一扇雄獅的門", "情境② DEMO", IMG + "demo-jp-site.jpg",
     [("首頁主視覺", "百貨會員限定「台湾へ、ふらっと。」"),
      ("LionTrip ¥3,000 OFF", "下載即領，來源碼綁定百貨")],
     [("行程卡片", "台北美食散步、九份十分、台灣鐵道"),
      ("催事導流", "「台湾フェア開催中」連到館內活動")],
     "風格照日本百貨官網：白底、深紅、方角、大量留白")
demo("DEMO 6　館內立牌：服務台就是 LionTrip 的下載點", "情境② DEMO", IMG + "demo-standee.jpg",
     [("服務台・收銀台立牌", "百貨會員限定 ¥3,000 OFF"),
      ("掃碼即下載", "QR 帶百貨來源碼，每次下載都算數")],
     [("服務人員一句話", "「台湾旅行、お得になりますよ」"),
      ("零系統門檻", "百貨不改系統，放立牌就能開始")],
     "百貨把熟客的信任借給雄獅，雄獅把分潤分給百貨", video=VID + "standee.mp4", poster=VID + "standee-poster.jpg")
demo("DEMO 7　LionTrip 國際版：日本點券＋線上支付，訂台灣行程", "情境② DEMO", IMG + "demo-liontrip.jpg",
     [("探索首頁", "沿用 LionTrip 現行粉色漸層與黏土風圖示"),
      ("日本版點券", "百貨點數 3,000 pt、台灣行程折價券")],
     [("日本版線上支付", "信用卡／QR 決濟，日本客用得順手"),
      ("海外行程加值", "日文導覽一日遊、鐵道旅、食衣住行育樂")],
     "畫面照 LionTrip 現行介面設計，點數與價格為示意")
demo("DEMO 8　催事活動：台湾フェア × LionTrip，把台灣帶進百貨", "情境② DEMO", IMG + "taiwan-fair.jpg",
     [("百貨催事場", "台灣物產展加開 LionTrip 攤位"),
      ("現場掃碼", "試吃、逛攤、掃碼下載一次完成")],
     [("現場訂行程", "九份、台南、花東，日文客服當場解答"),
      ("活動成效回報", "掃碼數、下載數、訂單數全記錄")],
     "催事檔期與規模依百貨年度企劃")

# ================================================================ 數據
demo("TCRM 顧客360：每一位客人的旅程，串成一條線", "騰雲｜數據", IMG + "demo-tcrm.jpg",
     [("顧客標籤", "阪急常客、B1甜點、美妝、虎迷、春節出發"),
      ("跨平台旅程", "點擊 → 領券 → 核銷 → 退稅 → 再出發")],
     [("送客來源", "台灣版、國際版分開看，成效說得清"),
      ("個資不落地", "只交換匿名事件 ID，會員資料留在原系統")],
     "一位客人去一次日本，變成每年都回來的熟客")
demo("Pandora 雙邊市場情報：兩邊的客人在聊什麼，每週一份", "騰雲｜數據", IMG + "pandora-dash.jpg",
     [("台灣社群", "哪家百貨、哪個櫃位、哪個商品正在燒"),
      ("日本社群", "日本人想去台灣哪裡、在意什麼")],
     [("決定下週優惠", "熱門話題直接變成專區優惠與 Banner"),
      ("決定推哪條行程", "百貨官網推什麼雄獅行程，用數據選")],
     "這份提案的調查，就是 Pandora 實測出來的")

# ================================================================ 收費
s = d.info("收費模式：騰雲像 trivago，站在中間按成果收費", label="商業模式｜分潤",
           banner="沒有成交就不收分潤：三方只為看得見的結果付錢")
box(s, 0.8, 1.55, 2.9, 3.7, LION, "雄獅旅遊", "導台灣客去百貨\n＝百貨付費\n\n收日本客進 LionTrip\n＝雄獅付費")
box(s, 9.65, 1.55, 2.9, 3.7, DEPT, "日本百貨", "台灣客到店核銷\n＝百貨付費\n\n導日本客去雄獅\n＝百貨收分潤")
arrow(s, 3.85, 3.2, 0.7, 0.4, shape=MSO_SHAPE.LEFT_RIGHT_ARROW, color="mid")
arrow(s, 8.8, 3.2, 0.7, 0.4, shape=MSO_SHAPE.LEFT_RIGHT_ARROW, color="mid")
d._round(s, 4.7, 1.4, 3.95, 4.0, TC, 0.06)
d._tx(s, 4.85, 1.57, 3.65, 0.4, "騰雲 T-Space 收的三種費用", 14, color="ink", bold=True, align=PP_ALIGN.CENTER)
for i, (t, sub) in enumerate([("CPC 點擊費", "每次有效點擊計費（示意 ¥20）"),
                              ("CPA 核銷費（選配）", "領券並到店核銷才計費"),
                              ("GMV 分潤", "導客成功訂單金額 × 費率（示意 3–5%）")]):
    y = 2.15 + i * 1.02
    d._round(s, 4.95, y, 3.45, 0.86, _rgb("#FFFFFF"), 0.12)
    d._tx(s, 5.1, y + 0.1, 3.2, 0.35, t, 14, bold=True)
    d._tx(s, 5.1, y + 0.48, 3.2, 0.3, sub, 10, color="mid")
d._tx(s, 0.8, 5.55, 11.7, 0.4, "導客成功的定義（待三方確認）：T-Space 追蹤碼 × 優惠券核銷 × 30 天歸因窗", 12, bold=True, color="frame")
foot(s)

d.table("一年跑下來的樣子（試算示意）", ["", "去程｜台灣客 → 日本百貨", "回程｜日本客 → 雄獅"],
        [["年有效點擊", "300,000 次", "50,000 次"], ["CPC", "¥20／次", "¥20／次"],
         ["點擊費小計", "¥600 萬", "¥100 萬"], ["核銷／成交率", "15%", "2%"],
         ["平均客單", "¥40,000", "¥120,000"], ["導購 GMV", "¥18 億", "¥1.2 億"],
         ["GMV 分潤", "3%", "5%"], ["分潤小計", "¥5,400 萬", "¥600 萬"]],
        label="商業模式｜試算", col_w=[1.4, 2.6, 2.6], hot_row=5, size=13, row_h=0.47,
        banner="雙向合計：年導購 GMV 約 ¥19.2 億，騰雲服務收入約 ¥6,700 萬（試算示意）",
        source="試算示意：所有假設須以雄獅會員赴日人數、百貨實際客單與三方合約費率替換")
foot(d.p.slides[-1])

# ================================================================ Activation
social_idea("A-1", "雄獅 App × 阪神梅田本店 × 甲子園", "阪神虎主場日：雄獅甲子園應援團",
            "雄獅開甲子園觀賽團，行程含阪神梅田本店虎迷商品專屬優惠；台灣虎迷穿應援服逛百貨，社群自然擴散\n"
            "球團合作需另洽，此為提案方向（AI 示意圖）", img=IMG + "stadium.jpg")
social_idea("A-2", "T-Space 專區 ＋ Threads", "退稅補給站：新制縮水的，雄獅幫你補回來",
            "11/1 新制上路，網友算出退稅剩 3.7%。優惠專區首波主打「台灣旅客專屬 95折＋免稅」＋退稅新制懶人包\n"
            "官方帳號到退稅討論串下回覆懶人包（Threads 海巡）（AI 示意圖）", img=IMG + "taxrefund.jpg")

# ================================================================ 時程
s = d.info("先從示範點跑起來，再擴到 70 多家", label="時程",
           banner="Phase 0 用三家示範點驗證數字，數字對了再複製")
d.timeline(s, 1.5, ["2026/12", "2027/02", "2027/04", "2027/06", "2027/09", "2027/12"],
           [("Phase 0｜示範點：阪急阪神・藤崎・鶴屋", 0.0, 0.32),
            ("Phase 1｜擴大：關西・九州主要百貨＋阪神虎開季", 0.22, 0.6),
            ("Phase 2｜全面：70 多家依序接入", 0.52, 1.0)])
cw = (W - 1.5) / 3 - 0.2
for i, (t, body) in enumerate([
        ("Phase 0　2026/12–2027/02", "T-Space 雙語專區上線\n雄獅台灣版 Banner＋LION Pay\n示範點核銷機制（POS／立牌）\n春節檔期跑第一波數字"),
        ("Phase 1　2027/02–2027/07", "LionTrip 日本點券＋線上支付\n百貨官網專區＋館內立牌\n阪神虎開季 × 甲子園應援團\n櫻花季、暑假兩波投放"),
        ("Phase 2　2027/06–2027/12", "70 多家百貨分批接入\n雄獅團體行程排入地方百貨\n台湾フェア × LionTrip 催事\nTCRM 熟客再行銷")]):
    x = 0.72 + i * (cw + 0.3)
    d._rect(s, x, 3.2, cw, 2.75, GREY)
    d._rect(s, x, 3.2, cw, 0.07, "frame")
    d._tx(s, x + 0.25, 3.4, cw - 0.5, 0.4, t, 13.5, color="frame", bold=True)
    d._tx(s, x + 0.25, 3.9, cw - 0.5, 2.0, body, 12, spacing=1.6)
foot(s)

d.table("三方分工：各自守好自己的那一段", ["", "雄獅旅遊", "日本百貨", "騰雲"],
        [["入口", "台灣版 Banner・推播／LionTrip 專區", "官網專區・立牌・催事", "T-Space 雙語 LP"],
         ["優惠", "雄獅幣・行程優惠・日本點券", "折扣方案・導客分潤條件", "券務系統・核銷 API"],
         ["支付", "LION Pay 退稅・日本版線上支付", "Mobile POS／APP 核銷", "支付與退稅資料串接"],
         ["數據", "會員 ID（匿名）", "核銷結果（匿名）", "TCRM・Pandora・結算報表"],
         ["推廣", "出團行程排入百貨", "店內露出・會員電子報", "素材製作・雙邊投放"]],
        label="Work Division", col_w=[0.8, 2.5, 2.2, 2.2], size=12.5, row_h=0.72)
foot(d.p.slides[-1])

d.table("KPI：每一層都看得到數字", ["層級", "指標", "Phase 0 目標（示意）"],
        [["曝光", "Banner・LP 瀏覽（雙邊）", "50 萬次"], ["點擊", "有效點擊／CTR", "6 萬次／12%"],
         ["領券", "優惠券領取數", "1.5 萬張"], ["核銷", "核銷率／導購 GMV", "40%／¥2.4 億"],
         ["回程", "LionTrip 下載／首單", "5,000 次／150 單"], ["熟客", "90 天內回訪率", "20%"]],
        label="KPI", col_w=[1.2, 2.6, 2.4], hot_row=3, size=13.5, row_h=0.58,
        banner="Phase 0 的數字，就是 Phase 1 分潤費率的依據",
        source="目標值為示意，需依雄獅會員規模、百貨客單與投放預算調整")
foot(d.p.slides[-1])

cl = d.closing("出發前，就是熟客。",
               "Next Step\n① 12 月：三方 kickoff，確認示範點與優惠方案\n"
               "② 簽署導客分潤條件與資料交換原則（只交換匿名事件）\n③ 2027/01：T-Space 雙語專區上線，春節檔期跑第一波")
for sh in cl.shapes:
    if sh.has_text_frame and sh.text_frame.text.startswith("Next Step"):
        for para in sh.text_frame.paragraphs:
            for r in para.runs:
                r.font.color.rgb = d.c["gold"]; r.font.size = Pt(14)

d.save("deck.pptx")
import json
json.dump(PAGE_MAP, open("assets/video/pages.json", "w"), ensure_ascii=False, indent=1)
print("videos on pages:", sorted(PAGE_MAP))
