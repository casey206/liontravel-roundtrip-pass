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
NAVY, CYAN = _rgb("#0A1F44"), _rgb("#00BCD4")   # 騰雲
BR = IMG + "brand/"
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
    if os.environ.get("NOVIDEO"):
        s.shapes.add_picture(poster, Inches(x), Inches(y), Inches(w), Inches(h))
        return
    s.shapes.add_movie(path, Inches(x), Inches(y), Inches(w), Inches(h),
                       poster_frame_image=poster, mime_type="video/mp4")
    PAGE_MAP.setdefault(d.n, []).append((os.path.basename(path), x / W, y / H, w / W, h / H))


def ai_tag(s, x, y, dark=False, text="AI 示意圖"):
    w = 0.3 + _w(text, 0.13, 0.075)
    d._round(s, x, y, w, 0.26, _rgb("#000000") if not dark else _rgb("#FFFFFF"), 0.5)
    d._tx(s, x, y + 0.04, w, 0.2, text, 8.5, color="white" if not dark else "ink", bold=True,
          align=PP_ALIGN.CENTER)


def logo_h(s, path, x, y, h):
    iw, ih = Image.open(path).size
    s.shapes.add_picture(path, Inches(x), Inches(y), Inches(h * iw / ih), Inches(h))
    return x + h * iw / ih


def foot(s, dark=False):
    if dark:
        return
    x = logo_h(s, BR + "accucrazy-dark.png", 0.6, H - 0.27, 0.11) + 0.2
    d._rect(s, x - 0.1, H - 0.28, 0.01, 0.16, _rgb("#CFC8CA"))
    logo_h(s, BR + "lion.png", x, H - 0.29, 0.17)


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


def callouts(s, x, y, w, items, start=1, col="frame", gap=1.15):
    for i, (t, sub) in enumerate(items):
        yy = y + i * gap
        circle_num(s, x, yy, start + i, col, size=0.4)
        d._tx(s, x + 0.55, yy + 0.02, w - 0.55, 0.36, t, 14, bold=True, spacing=1.15)
        d._tx(s, x + 0.55, yy + 0.42, w - 0.55, 0.7, sub, 11, color="mid", spacing=1.4)


def num_card(s, x, y, w, big, lab, sub="", color="frame", h=2.3):
    d._rect(s, x, y, w, h, GREY)
    d._rect(s, x, y, w, 0.08, color)
    d._tx(s, x + 0.25, y + 0.3, w - 0.5, 0.9, big, 44, color=color, bold=True, font=d.f["num"])
    d._tx(s, x + 0.25, y + 1.25, w - 0.5, 0.4, lab, 13, bold=True)
    if sub:
        d._tx(s, x + 0.25, y + 1.65, w - 0.5, 0.75, sub, 11.5, color="mid", spacing=1.4)


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
        d._tx(s, x + 0.12, y + 0.7, w - 0.24, h - 0.8, sub, 13, color=subc or fg,
              align=PP_ALIGN.CENTER, spacing=1.45)


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

# ---------------------------------------------------------------- v3 版型系統
from pptx import Presentation as _P
TPL = "assets/tc_template.pptx"
d.p = _P(TPL)
_sld = d.p.slides._sldIdLst
for _id in list(_sld):
    d.p.part.drop_rel(_id.rId); _sld.remove(_id)
LAY = {l.name: l for l in d.p.slide_layouts}


def _strip(s, keep=()):
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx not in keep:
            ph._element.getparent().remove(ph._element)


def _slide_tpl(bg="paper", layout="1_內容頁_標題_白"):
    s = d.p.slides.add_slide(LAY[layout])
    _strip(s)
    d.n += 1
    if bg != "paper":
        d._rect(s, 0, 0, W, H, bg if isinstance(bg, str) else bg)
    return s
d._slide = _slide_tpl

TOC = [("背景與機會", "機會"), ("合作示意圖與合作重點", "合作"), ("運用情境① 經營台灣人客戶", "情境①"),
       ("運用情境② 經營日本人客戶", "情境②"), ("Banner 視覺提案", "Banner"), ("數據與情報（TCRM・Pandora）", "數據"),
       ("商業模式與分潤", "商模"), ("各方角色與後續行動", "落地")]
SECNUM = {k: i + 1 for i, (_, k) in enumerate(TOC)}
SECTIONS = []
CUR = {"s": None}
INK2 = _rgb("#2B2427")


def sec(name):
    CUR["s"] = name


def info3(title, label=None, banner=None, source=None):
    """騰雲公版內容頁：公版左上箭頭＋「N. 標題」，右上小標籤，下方深藍結論條。"""
    s = d._slide("paper")
    num = SECNUM.get(CUR["s"])
    full = (f"{num}. " if num else "") + title
    lw = (0.36 + _w(label, 0.14, 0.08)) if label else 0
    tw = W - 1.11 - 0.75 - lw
    size = 24
    while size > 17 and _w(full, 0.155 * size / 11.2, 0.085 * size / 11.2) > tw:
        size -= 1
    d._tx(s, 1.11, 0.27, tw, 0.6, full, size, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    if label:
        d._round(s, W - 0.55 - lw, 0.4, lw, 0.32, CYAN, 0.5)
        d._tx(s, W - 0.55 - lw, 0.445, lw, 0.24, label, 10, color="white", bold=True, align=PP_ALIGN.CENTER)
    d._rect(s, 0.54, 1.0, W - 1.08, 0.012, _rgb("#DDE3EA"))
    if source:
        d._tx(s, 0.6, H - 1.3, W - 1.2, 0.24, source, 8.5, color="grey")
    if banner:
        d._round(s, 0.6, H - 1.03, W - 1.2, 0.54, NAVY, 0.25)
        d._rect(s, 0.85, H - 0.82, 0.12, 0.12, CYAN)
        d._tx(s, 1.12, H - 0.9, W - 2.2, 0.36, banner, 15, color="white", bold=True)
    return s
d.info = info3


def divider3(text, sub="", solid=True, img=None, num=""):
    """騰雲公版章節頁（章節頁_中文）。"""
    s = d.p.slides.add_slide(LAY["章節頁_中文"])
    d.n += 1
    n = SECNUM.get(CUR["s"], 0)
    for ph in s.placeholders:
        if ph.placeholder_format.type == 1:
            ph.text = text
            for para in ph.text_frame.paragraphs:
                for r in para.runs: r.font.name = FONT
            d._ea(ph, FONT)
        else:
            ph.text = f"{n:02d}"
    if sub:
        d._tx(s, 0.76, 4.4, 8.5, 0.9, sub, 16, color="white", spacing=1.5)
    return s
d.divider = divider3


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
    px, py, pw, ph = fit(s, img, 0.6, 1.55, 8.55, 4.85)
    if video:
        movie(s, video, poster, px, py, pw, ph)
    ai_tag(s, px + 0.12, py + 0.12, text="AI 示意影片" if video else "AI 示意圖")
    d._round(s, 9.4, 1.55, 3.33, 4.85, GREY, 0.04)
    d._tx(s, 9.62, 1.72, 3.0, 0.3, "畫面重點", 11, color="frame", bold=True)
    callouts(s, 9.62, 2.15, 3.0, left + right, 1, gap=1.05)
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
        d._tx(s, x + 0.1, 1.58, cw - 0.2, 0.35, head, 14, color=fg, bold=True, align=PP_ALIGN.CENTER)
        d._rect(s, x + 0.12, 1.98, cw - 0.24, 2.3, _rgb("#FFFFFF"))
        fit(s, IMG + img, x + 0.16, 2.02, cw - 0.32, 2.22)
        d._tx(s, x + 0.12, 4.38, cw - 0.24, 0.5, cap, 11.5, color=fg, bold=True, align=PP_ALIGN.CENTER, spacing=1.25)
        if i < n - 1:
            arrow(s, x + cw + 0.06, 3.0, 0.38, 0.3, color="frame")
        d._rect(s, x + cw / 2 - 0.02, 4.9, 0.04, 0.25, col)
    cyl = s.shapes.add_shape(MSO_SHAPE.CAN, Inches(1.4), Inches(5.1), Inches(W - 2.8), Inches(1.1))
    cyl.fill.solid(); cyl.fill.fore_color.rgb = LION; cyl.line.fill.background(); cyl.shadow.inherit = False
    d._tx(s, 1.4, 5.48, W - 2.8, 0.6, db_text, 14.5, color="white", bold=True, align=PP_ALIGN.CENTER, spacing=1.3)
    foot(s)
    return s


def shift_down(s, dy=0.28, above=1.1, below=6.6):
    """把標題下方的內容整體下移（橫幅與頁尾不動）。"""
    for sh in s.shapes:
        if Inches(above) < sh.top < Inches(below):
            sh.top = sh.top + Inches(dy)


# ================================================================ 01 封面（騰雲公版）
s = d.p.slides.add_slide(LAY["封面頁首＿版面１"])
d.n += 1
for ph in list(s.placeholders):
    t = ph.placeholder_format.type
    if t == 1:
        ph.text = "雄獅與日本百貨之\n雙向導購合作提案。"
        for para in ph.text_frame.paragraphs:
            for r in para.runs: r.font.size = Pt(40); r.font.bold = True
    elif t == 18:
        ph._element.getparent().remove(ph._element)
    else:
        ph._element.getparent().remove(ph._element)
d._tx(s, 0.8, 6.35, 3, 0.4, "2026.11", 14, color="ink", bold=True)
d._tx(s, 0.8, 4.35, 6.0, 0.5, "雙程票 Round Trip Pass｜出發前，就是熟客。", 16, color="ink", bold=True)
d._tx(s, 0.8, 5.35, 7.0, 0.4, "TURN CLOUD TECHNOLOGY SERVICE INC. × ACCUCRAZY", 13, color="ink", bold=True)
x = logo_h(s, BR + "lion.png", 0.8, 5.9, 0.36) + 0.25
logo_h(s, BR + "hhd-short.png", x, 5.98, 0.2)

# ================================================================ 目次
s = d._slide("paper")
d._tx(s, 1.11, 0.27, 6, 0.6, "目次", 24, bold=True, anchor=MSO_ANCHOR.MIDDLE)
for i, (t, _) in enumerate(TOC):
    col, row = i // 4, i % 4
    x, y = 0.95 + col * 6.1, 1.55 + row * 1.2
    d._tx(s, x, y, 0.8, 0.6, f"{i + 1}.", 26, color=CYAN, bold=True, font=d.f["num"])
    d._tx(s, x + 0.7, y + 0.05, 5.2, 0.6, t, 22, bold=True)
foot(s)

# ================================================================ 02 一頁看懂
sec("機會")
d.divider("背景與機會", "台灣客、退稅新制、資訊斷層、回程空白：四個機會，一句話")
s = d.info("一頁看懂：讓兩邊的客人，互相變成對方的客人", label="Executive Summary",
           banner="雄獅與百貨各開一扇門，中間的系統、數據、推廣與結算，全部交給騰雲")
cols = [("機會", LION, "台灣客是日本百貨最穩的客人",
         "673 萬人次／年，在日消費 1.2 兆日圓\n退稅新制縮水，優惠成新決策點\n回程市場只有去程的 1/4.5"),
        ("解法", TC, "騰雲 T-Space 雙程票",
         "去程：雄獅 App → 日本百貨\n回程：百貨官網・立牌 → LionTrip\n領券到回訪，全部記進 TCRM"),
        ("收益", DEPT, "按成果分潤，三方都有帳",
         "百貨：多一條穩定台灣客源\n雄獅：海外會員＋落地消費入口\n騰雲：CPC＋GMV 分潤")]
cw = (W - 1.5) / 3 - 0.2
for i, (k, col, t, body) in enumerate(cols):
    x = 0.72 + i * (cw + 0.3)
    d._rect(s, x, 1.45, cw, 4.55, GREY)
    d._rect(s, x, 1.45, cw, 0.62, col)
    d._tx(s, x + 0.3, 1.58, cw - 0.6, 0.4, k, 17, color="ink" if col == TC else "white", bold=True)
    d._tx(s, x + 0.3, 2.35, cw - 0.6, 0.9, t, 19, bold=True, spacing=1.3)
    d._tx(s, x + 0.3, 3.45, cw - 0.6, 2.4, body, 14, color="mid", spacing=1.75)
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
    d._tx(s, x + 0.3, 4.15, 3.4, 0.4, t, 15, bold=True)
    d._tx(s, x + 0.3, 4.62, 3.4, 1.1, sub, 12.5, color="mid", spacing=1.45)
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
    d._tx(s, x + 0.3, 3.7, cw - 0.6, 2.2, body, 14, color="mid", spacing=1.7)
foot(s)

# ================================================================ 08 IDEA（動態）
s = d._slide("dark")
movie(s, VID + "planes.mp4", IMG + "idea-bg.jpg", 0, 0, W, H)
d._tx(s, 1.05, 1.85, 5.2, 0.34, "IDEA", 13, color="accent", bold=True)
d._tx(s, 1.02, 2.35, 6.0, 1.7, "雙程票\nRound Trip Pass", 40, color="white", bold=True, spacing=1.2)
d._tx(s, 1.05, 4.45, 5.4, 2.0, "一張票，兩個方向。\n去程：台灣客從雄獅 App 走進日本百貨。\n回程：百貨的日本熟客走進雄獅國際版。\n騰雲 T-Space 記下每一次進出，按成果分潤。",
      13.5, color="gold", spacing=1.75)

# ================================================================ 09 章節
sec("合作")
d.divider("合作示意圖與合作重點", "騰雲 T-Space 導購平台：兩個入口、一個中轉、全程可追蹤")

# ================================================================ 10 合作示意圖
s = d.info("合作示意圖：騰雲 T-Space 是相互導客的共通平台", label="商業模式",
           banner="台灣人顧客 → 日本百貨買免稅商品　｜　日本人顧客 → 雄獅國際會員買旅遊行程")
d._tx(s, 0.62, 1.2, 3.5, 0.35, "雄獅集團", 14, bold=True)
for j, (t, img) in enumerate([("國際版 APP 會員\nLionTrip", "crops/lt-p1.jpg"), ("台灣版 APP 會員\n雄獅旅遊", "crops/tw-p1.jpg")]):
    y = 1.6 + j * 2.5
    d._round(s, 0.62, y, 3.3, 2.3, LION, 0.08)
    d._tx(s, 0.8, y + 0.2, 1.8, 0.8, t, 13, color="white", bold=True, spacing=1.3)
    fit(s, IMG + img, 2.5, y + 0.1, 1.35, 2.1)
d._round(s, 4.75, 2.45, 3.3, 2.3, TC, 0.12)
d._tx(s, 4.85, 2.7, 3.1, 1.1, "騰雲 T-Space\n導購平台", 22, color="ink", bold=True, align=PP_ALIGN.CENTER, spacing=1.2)
d._tx(s, 4.85, 3.85, 3.1, 0.8, "優惠專區・核銷・TCRM\nPandora・推廣・分潤結算", 12, color="ink", align=PP_ALIGN.CENTER, spacing=1.4)
arrow(s, 3.98, 2.3, 0.72, 0.32, color=DEPT, shape=MSO_SHAPE.LEFT_ARROW)
d._tx(s, 4.0, 1.55, 3.0, 0.6, "日本人顧客 → 成為雄獅\n國際會員・購買旅遊行程", 11, color=DEPT, bold=True, spacing=1.25)
arrow(s, 3.98, 4.6, 0.72, 0.32, color=LION)
d._tx(s, 4.0, 5.0, 3.0, 0.6, "台灣人顧客 → 導客至\n日本百貨・購買免稅商品", 11, color=LION, bold=True, spacing=1.25)
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
    cy = 1.62 + (i % 17) * 0.243
    d._rect(s, cx, cy, 1.8, 0.225, _rgb("#FFFFFF"))
    d._tx(s, cx + 0.07, cy + 0.02, 1.72, 0.2, n, 9.5, color=DEPT if "＊" in n else "ink", bold="＊" in n)
d._tx(s, 8.85, 5.93, 4.0, 0.25, "＊ 先行示範點的可能合作對象", 10.5, color=DEPT, bold=True)
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
        d._rect(s, x + 1.25, y + 0.72 + k * 0.56, 0.1, 0.1, col)
        d._tx(s, x + 1.45, y + 0.58 + k * 0.56, w - 1.55, 0.55, p, 12.5, bold=True, spacing=1.2)
for x, col, t, pts, img in [
        (4.95, TC, "騰雲｜LP T-Space", ["雙語優惠活動頁（中文／日文）", "優惠券發放、核銷、分潤結算", "TCRM 顧客標籤＋Pandora 情報"], "crops/tw-p3.jpg"),
        (8.88, DEPT, "日本端百貨業者", ["建立雄獅國際版 APP 專區及催事活動", "導客成功之分潤條件", "優惠專區核銷機制（Mobile POS／APP／立牌）"], "crops/jp-site.jpg")]:
    y, w, h = 1.2, 3.82, 4.95
    d._rect(s, x, y, w, h, GREY)
    d._rect(s, x, y, w, 0.42, col)
    d._tx(s, x + 0.18, y + 0.08, w - 0.3, 0.3, t, 12, color="ink" if col == TC else "white", bold=True)
    fit(s, IMG + img, x + 0.2, y + 0.6, w - 0.4, 2.3)
    for k, p in enumerate(pts):
        d._rect(s, x + 0.25, y + 3.22 + k * 0.58, 0.1, 0.1, col)
        d._tx(s, x + 0.45, y + 3.08 + k * 0.58, w - 0.6, 0.55, p, 12.5, bold=True, spacing=1.2)
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
    d._tx(s, x + 0.22, y + 1.08, cw - 0.4, 0.95, sub, 12, color="ink" if hot else "mid", spacing=1.38)
foot(s)

# ================================================================ 關於騰雲
s = d.info("關於騰雲 × Accucrazy：從 POS、CRM 到 AI Agent，一條龍", label="騰雲 TurnCloud × Accucrazy",
           banner="雙程票要用的核銷、支付、CRM、AI 情報，騰雲集團本來就在做",
           source="Data source: 騰雲 Turn Cloud Introduction（2026/06/16）；TurnCloud × AccuCrazy AI OS Launch Briefing")
logo_h(s, BR + "turncloud.png", 0.6, 1.62, 0.42)
d._tx(s, 0.6, 2.18, 5.8, 0.4, "騰雲科技　6870.TW（上櫃・數位雲端類股）", 14, bold=True)
cw = 1.82
for i, (b, l) in enumerate([("8.04億", "2025 營收（EPS 7.02 元）"), ("+48%", "2026 前 5 月營收年增"), ("250+", "集團員工（研發 65%）")]):
    x = 0.6 + i * (cw + 0.15)
    d._rect(s, x, 2.7, cw, 1.35, GREY)
    d._rect(s, x, 2.7, cw, 0.06, CYAN)
    d._tx(s, x + 0.15, 2.85, cw - 0.3, 0.6, b, 28, color=CYAN, bold=True, font=d.f["num"])
    d._tx(s, x + 0.15, 3.5, cw - 0.3, 0.5, l, 10.5, color="mid", spacing=1.3)
d._tx(s, 0.6, 4.3, 5.9, 1.5, "台灣汐止總部，海外據點：日本（2024）・泰國・馬來西亞・中國\n20 年零售 POS／CRM 導入經驗：TPOS、TCRM、HOYABOX 行動 POS、OLink 支付", 12, spacing=1.6)
d._rect(s, 6.75, 1.6, 0.01, 4.4, _rgb("#E7E2E3"))
logo_h(s, BR + "accucrazy-dark.png", 7.0, 1.72, 0.26)
d._tx(s, 7.0, 2.18, 5.7, 0.4, "Accucrazy 肖準行銷｜The Pocket Company", 14, bold=True)
for i, (t, sub) in enumerate([("AI Agent 團隊", "Pandora 輿情、Banana 視覺、Moana 內容、Adriana 投放、Stacey 指揮"),
                              ("T-Space", "騰雲 AI OS 上的 Agent 工作空間，也是本案導購平台的底座"),
                              ("口碑與社群", "Threads・IG・KOL 操作，本案 Activation 由此執行")]):
    y = 2.72 + i * 1.08
    d._round(s, 7.0, y, 5.73, 0.95, GREY, 0.08)
    d._tx(s, 7.2, y + 0.1, 5.4, 0.35, t, 14, color="frame", bold=True)
    d._tx(s, 7.2, y + 0.48, 5.4, 0.45, sub, 11.5, color="mid")
foot(s)

s = d.info("AI Agent 團隊：Pandora 看市場，Banana 做素材", label="騰雲 × Accucrazy｜AI Agents",
           banner="兩位 AI 員工每週出一份雙邊情報、一批新 Banner，人力只負責決策")
for i, (img, name, role, pts, col) in enumerate([
        ("08_pandora.jpg", "Pandora", "輿情洞察與市場分析", ["監測台灣・日本社群：誰在聊哪家百貨、哪個商品", "每週自動產出聲量、洞察、趨勢三份報告", "本案調查 24,673 篇貼文，就是 Pandora 實測"], CYAN),
        ("10_banana.jpg", "Banana", "視覺設計與圖像生成", ["依 Pandora 熱門話題，當天出 Banner", "中、日文字精準渲染，靜態＋動態一起出", "本案 9 組 Banner 與 DEMO 畫面皆由 Banana 生成"], _rgb("#F5B400"))]):
    x = 0.6 + i * 6.25
    d._round(s, x, 1.55, 5.95, 4.55, GREY, 0.05)
    fit(s, BR + img, x + 0.15, 1.7, 5.65, 2.45)
    d._tx(s, x + 0.3, 4.25, 3.0, 0.45, name, 22, bold=True, font=d.f["num"])
    tag(s, x + 1.85, 4.3, role, col=col, size=10.5, h=0.34, fg="white" if col == CYAN else "ink")
    for k, p in enumerate(pts):
        d._rect(s, x + 0.32, 4.92 + k * 0.38, 0.09, 0.09, col)
        d._tx(s, x + 0.52, 4.82 + k * 0.38, 5.3, 0.35, p, 11.5)
foot(s)

# ================================================================ 13 情境①
sec("情境①")
d.divider("運用情境① 經營台灣人客戶", "雄獅台灣版 App → T-Space → 日本百貨現場核銷")
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
sec("情境②")
d.divider("運用情境② 經營日本人客戶", "百貨官網・館內立牌・催事 → T-Space → LionTrip 國際版")
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
demo("Mockup　阪急阪神官網：桌機首頁輪播＋手機會員區，放雄獅的 Banner", "情境② Mockup", IMG + "mock-dept_site.jpg",
     [("桌機首頁主輪播", "「台湾へ、ふらっと。」阪急阪神 × LionTrip 聯名"),
      ("PR 標示", "右上標「PR｜LionTrip」，百貨官網慣例")],
     [("手機會員區塊", "1:1「台湾フェア、開催中。」會員報版"),
      ("一鍵導流", "點擊帶百貨來源碼，進 LionTrip 下載頁")],
     "百貨的日本熟客，在最信任的官網上看到雄獅")
demo("Mockup　LionTrip 國際版：首頁 Banner 放阪急，點進去就是優惠券", "情境② Mockup", IMG + "mock-liontrip_app.jpg",
     [("首頁 Banner", "Hankyu × LionTrip「Hankyu B1 Sweets & Gifts」"),
      ("海外會員語言", "英文介面，給 LionTrip 國際會員")],
     [("優惠券頁", "5% OFF＋免稅，阪急うめだ本店 B1–B2"),
      ("櫃檯核銷", "Show at Counter，QR 掃碼回寫 TCRM")],
     "LionTrip 會員到大阪，第一站就是阪急")
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

# ================================================================ Banner 視覺提案
sec("Banner")
d.divider("Banner 視覺提案", "同一句「出發前，就是熟客。」，九種說法：靜態＋動態")
s = d.info("Banner 怎麼做：Banana 在 T-Space Studio 裡，四十秒出一組", label="Banner｜Banana Split",
           banner="Pandora 抓到話題 → Banana 出圖 → 騰雲套上雙方正式 logo → 上架")
px, py, pw, ph = fit(s, BR + "demo_studio.jpg", 0.6, 1.55, 8.55, 4.85)
tag(s, px + 0.12, py + 0.12, "T-Space Studio 實際產品畫面", col=NAVY, size=10, h=0.32)
d._round(s, 9.4, 1.55, 3.33, 4.85, GREY, 0.04)
logo_h(s, BR + "tspace-dark.png", 9.62, 1.75, 0.3)
s.shapes.add_picture(BR + "banana.png", Inches(11.75), Inches(1.6), Inches(0.9), Inches(0.9))
callouts(s, 9.62, 2.6, 3.0, [("輸入 Brief", "產品、檔期、切角一句話"),
                             ("Agent 流水線", "Pandora → Moana → Banana 自動接力"),
                             ("輸出多版本", "21:9 輪播、9:16 限動、1:1 會員報")], gap=1.15)
foot(s)
BN = IMG + "banners_v2/"


def banner_grid(title, lab, items, bar):
    s = d.info(title, label=lab, banner=bar)
    cw, chh = 5.9, 2.5
    for i, (img, k, t) in enumerate(items):
        x = 0.6 + (i % 2) * (cw + 0.33)
        y = 1.55 + (i // 2) * (chh + 0.02)
        px, py, pw, ph = fit(s, BN + img, x, y, cw, 1.95)
        tw = tag(s, px, py + ph + 0.1, k, col="frame", size=11, h=0.34)
        d._tx(s, px + tw + 0.14, py + ph + 0.14, cw - tw, 0.3, t, 12.5, color="ink", bold=True)
    foot(s)
    return s

s = d.info("Banner 品牌系統：雄獅紅版型＋正式聯名 logo，畫面再怎麼換都認得出", label="Banner｜Co-branding",
           banner="版型與 logo 由騰雲統一套版，不交給 AI 生成；AI 只負責右側主視覺")
BV = IMG + "banners_v2/"
for i, (img, t, sub) in enumerate([("b2-clay.jpg", "去程｜雄獅台灣版 App", "雄獅紅斜切色塊＋雄獅獅頭浮水印；左上「雄獅旅遊 × 阪急阪神百貨店」聯名膠囊"),
                                   ("b8-jp-clay.jpg", "回程｜LionTrip・百貨官網", "百貨白底＋深紅斜線、明朝體標題；「阪急阪神百貨店 × LionTrip」，CTA 用 LionTrip 粉")]):
    y = 1.55 + i * 2.35
    px, py, pw, ph = fit(s, BV + img, 0.6, y, 4.6, 1.97, border=True)
    d._tx(s, 5.45, y + 0.2, 3.8, 0.4, t, 15, bold=True)
    d._tx(s, 5.45, y + 0.7, 3.75, 1.2, sub, 11.5, color="mid", spacing=1.45)
d._round(s, 9.4, 1.55, 3.33, 4.6, GREY, 0.04)
d._tx(s, 9.62, 1.72, 3.0, 0.3, "套版規則", 12, color="frame", bold=True)
callouts(s, 9.62, 2.15, 3.0, [("左字右圖", "左 40% 品牌色塊放文案，右 60% 放主視覺"),
                             ("聯名在左上", "誰的通路誰在前，用正式 logo"),
                             ("色彩分工", "去程雄獅紅、回程百貨白＋深紅"),
                             ("動態只動右邊", "主視覺動、品牌區全程不動")], gap=0.98)
foot(s)
banner_grid("去程 Banner①：四種說法，同一個優惠", "Banner｜雄獅台灣版 App", [
    ("b2-clay.jpg", "黏土微縮", "最可愛：把百貨做成玩具，主打品牌句"),
    ("b3-taxrefund.jpg", "退稅補給站", "最即時：接住 11/1 退稅新制的討論"),
    ("b4-b1map.jpg", "B1 甜點地圖", "最好逛：把網友攻略變成官方地圖"),
    ("b6-ticket.jpg", "雙程票", "最好懂：行程＋百貨一張票，賣團順便賣券")],
    "四個切角輪播測試，用點擊率決定主打")
s = d.info("去程 Banner②：跟著檔期換臉，限動版也一起做", label="Banner｜雄獅台灣版 App",
           banner="檔期：阪神虎開季（3 月）・櫻花季（3–4 月）・春節／暑假出發前推播")
for i, (img, k, t) in enumerate([("b5-tigers.jpg", "阪神虎主場日", "虎迷限定：阪神梅田本店應援商品"),
                                 ("b7-sakura.jpg", "櫻花季", "春假出發前先領券，季節感最強")]):
    y = 1.55 + i * 2.5
    px, py, pw, ph = fit(s, BN + img, 0.6, y, 8.3, 2.0)
    tw = tag(s, px, py + ph + 0.08, k, col="frame", size=11, h=0.34)
    d._tx(s, px + tw + 0.12, py + ph + 0.11, 6, 0.3, t, 12.5, color="ink", bold=True)
px, py, pw, ph = fit(s, BN + "b9-story.jpg", 9.25, 1.5, 3.5, 4.55)
tag(s, px, py + ph - 0.32, "IG 限動 9:16", col="dark", size=10.5, h=0.34)
foot(s)
s = d.info("回程 Banner：用百貨的語氣，對日本熟客說話", label="Banner｜百貨官網・LionTrip",
           banner="日本側放兩種語氣：LionTrip 的可愛黏土風，百貨會員報的沉穩明朝體")
px, py, pw, ph = fit(s, BN + "b8-jp-clay.jpg", 0.6, 1.6, 7.6, 3.3)
tag(s, px, py + ph + 0.1, "LionTrip 首頁 Banner", col=LION, size=11, h=0.34)
d._tx(s, px, py + ph + 0.5, pw, 0.6, "粘土風台灣ジオラマ：台北101、提灯、タピオカ、小籠包、鉄道", 12, color="mid")
px, py, pw, ph = fit(s, BN + "b10-jp-square.jpg", 8.6, 1.55, 4.15, 4.15)
tag(s, px, py + ph + 0.08, "百貨會員電子報・IG 1:1", col=DEPT, size=11, h=0.34)
foot(s)
s = d.info("動態 Banner：同一張圖，動起來點擊率更高", label="Banner｜Motion",
           banner="動態版用於 App 開屏、IG Reels、LINE 推播；靜態版保留給輪播位")
for i, (vid, img, k) in enumerate([("bn-clay.mp4", "b2-clay.jpg", "黏土微縮｜小人進出百貨"),
                                   ("bn-tax.mp4", "b3-taxrefund.jpg", "退稅補給站｜收據摺成飛機"),
                                   ("bn-tigers.mp4", "b5-tigers.jpg", "阪神虎｜棒球飛過虎紋"),
                                   ("bn-jp.mp4", "b8-jp-clay.jpg", "台湾へ｜小火車繞台灣")]):
    x = 0.6 + (i % 2) * 6.23
    y = 1.55 + (i // 2) * 2.5
    px, py, pw, ph = fit(s, BN + img, x, y, 5.9, 1.95)
    if os.path.exists(VID + "brand2/" + vid):
        movie(s, VID + "brand2/" + vid, BN + img, px, py, pw, ph)
    tw = tag(s, px, py + ph + 0.1, "MOTION", col="dark", size=10.5, h=0.34)
    d._tx(s, px + tw + 0.12, py + ph + 0.13, 5, 0.3, k, 12.5, color="ink", bold=True)
foot(s)

s = d.info("動態 Banner②：檔期版、限動、日本側也全部動起來", label="Banner｜Motion",
           banner="九組 Banner 全部有動態版；完整播放頁見雲端 banners.html")
for i, (vid, img, k) in enumerate([("bn-b1map.mp4", "b4-b1map.jpg", "B1 甜點地圖｜圖釘跳出"),
                                   ("bn-ticket.mp4", "b6-ticket.jpg", "雙程票｜飛機劃過登機證"),
                                   ("bn-sakura.mp4", "b7-sakura.jpg", "櫻花季｜花瓣飄落、電車經過")]):
    y = 1.55 + i * 1.62
    px, py, pw, ph = fit(s, BN + img, 0.6, y, 3.4, 1.42)
    if os.path.exists(VID + "brand2/" + vid):
        movie(s, VID + "brand2/" + vid, BN + img, px, py, pw, ph)
    tw = tag(s, px + pw + 0.2, py + 0.35, "MOTION", col="dark", size=10.5, h=0.34)
    d._tx(s, px + pw + 0.2, py + 0.8, 3.0, 0.4, k, 12.5, color="ink", bold=True)
for j, (vid, img, k, x, w) in enumerate([("bn-story.mp4", "b9-story.jpg", "IG 限動 9:16", 7.35, 2.4),
                                          ("bn-square.mp4", "b10-jp-square.jpg", "百貨會員報 1:1", 9.95, 2.8)]):
    px, py, pw, ph = fit(s, BN + img, x, 1.55, w, 4.3)
    if os.path.exists(VID + "brand2/" + vid):
        movie(s, VID + "brand2/" + vid, BN + img, px, py, pw, ph)
    tag(s, px, py + ph + 0.08, k, col="dark", size=10.5, h=0.34)
foot(s)

# ================================================================ 數據
sec("數據")
d.divider("數據與情報", "TCRM 顧客360 ＋ Pandora 雙邊市場情報")
demo("TCRM 顧客360：每一位客人的旅程，串成一條線", "騰雲｜數據", IMG + "demo-tcrm.jpg",
     [("顧客標籤", "阪急常客、B1甜點、美妝、虎迷、春節出發"),
      ("跨平台旅程", "點擊 → 領券 → 核銷 → 退稅 → 再出發")],
     [("送客來源", "台灣版、國際版分開看，成效說得清"),
      ("個資不落地", "只交換匿名事件 ID，會員資料留在原系統")],
     "一位客人去一次日本，變成每年都回來的熟客")
s = d.info("Pandora：輸入一個關鍵字，聲量、洞察、趨勢三份報告自動完成", label="騰雲｜Pandora",
           banner="這份提案的調查，就是用 Pandora 實測出來的：兩次查詢、24,673 篇台灣社群貼文")
px, py, pw, ph = fit(s, "research/pandora-ui/home.png", 0.6, 1.55, 8.4, 4.75, border=True)
tag(s, px + 0.12, py + 0.12, "Pandora 實際產品畫面", col="dark", size=9, h=0.3)
callouts(s, 9.45, 1.6, 3.3, [("跨平台資料庫", "Threads・IG・PTT・Dcard・FB，累積監測超過 200 萬則貼文"),
                            ("多市場切換", "台灣、日本、香港、韓國…同一套查詢看兩邊市場"),
                            ("AI Agent 寫報告", "聲量、洞察、Threads 趨勢三份報告自動產出")], gap=1.5)
foot(s)
demo("Pandora 聲量報告：阪急阪神在台灣社群的真實數字", "騰雲｜Pandora 實測", IMG + "pandora-volume-c.png",
     [("3,314 篇", "4.5 個月內台灣社群談阪急｜阪神"),
      ("106 萬讚・341 萬聲量", "平均每篇 320 讚、11.5 則留言")],
     [("IG 與 Threads 為主", "IG 1,521 篇、Threads 1,094 篇、PTT 685 篇"),
      ("攻略文最會擴散", "B1 甜點攻略 9.76 萬瀏覽、退稅文 52.1 萬瀏覽")],
     "每週一份：哪家百貨、哪個話題、哪篇攻略正在燒")
demo("Pandora 洞察報告：台灣人怎麼聊日本百貨", "騰雲｜Pandora 實測", IMG + "pandora-insight-c.png",
     [("阪神虎是最大入口", "969 篇，比退稅、優惠討論加起來還多"),
      ("B1 甜點第二", "444 篇，伴手禮是台灣客的固定行程")],
     [("OTA 佔走日本話題", "KKday 4,691、Klook 3,511、雄獅 1,682"),
      ("雄獅缺的是落地購物", "雙程票補的就是這個位置")],
     "熱門話題直接變成下週的專區優惠與 Banner")

# ================================================================ 收費
sec("商模")
d.divider("商業模式與分潤", "騰雲站在中間，按點擊與成交收費")
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
    d._tx(s, 5.1, y + 0.46, 3.2, 0.35, sub, 11.5, color="mid")
d._tx(s, 0.8, 5.55, 11.7, 0.4, "導客成功的定義（待三方確認）：T-Space 追蹤碼 × 優惠券核銷 × 30 天歸因窗", 12, bold=True, color="frame")
foot(s)

d.table("一年跑下來的樣子（試算示意）", ["", "去程｜台灣客 → 日本百貨", "回程｜日本客 → 雄獅"],
        [["年有效點擊", "300,000 次", "50,000 次"], ["CPC", "¥20／次", "¥20／次"],
         ["點擊費小計", "¥600 萬", "¥100 萬"], ["核銷／成交率", "15%", "2%"],
         ["平均客單", "¥40,000", "¥120,000"], ["導購 GMV", "¥18 億", "¥1.2 億"],
         ["GMV 分潤", "3%", "5%"], ["分潤小計", "¥5,400 萬", "¥600 萬"]],
        label="商業模式｜試算", col_w=[1.4, 2.6, 2.6], hot_row=5, size=12.5, row_h=0.43,
        banner="雙向合計：年導購 GMV 約 ¥19.2 億，騰雲服務收入約 ¥6,700 萬（試算示意）",
        source="試算示意：所有假設須以雄獅會員赴日人數、百貨實際客單與三方合約費率替換")
foot(d.p.slides[-1])

# ================================================================ Activation
sec("落地")
d.divider("各方角色與後續行動", "Activation、時程、分工、KPI、Next Step")
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
    d._tx(s, x + 0.25, 3.88, cw - 0.5, 2.0, body, 13.5, spacing=1.55)
foot(s)

d.table("三方分工：各自守好自己的那一段", ["", "雄獅旅遊", "日本百貨", "騰雲"],
        [["入口", "台灣版 Banner・推播／LionTrip 專區", "官網專區・立牌・催事", "T-Space 雙語 LP"],
         ["優惠", "雄獅幣・行程優惠・日本點券", "折扣方案・導客分潤條件", "券務系統・核銷 API"],
         ["支付", "LION Pay 退稅・日本版線上支付", "Mobile POS／APP 核銷", "支付與退稅資料串接"],
         ["數據", "會員 ID（匿名）", "核銷結果（匿名）", "TCRM・Pandora・結算報表"],
         ["推廣", "出團行程排入百貨", "店內露出・會員電子報", "素材製作・雙邊投放"]],
        label="Work Division", col_w=[0.8, 2.5, 2.2, 2.2], size=14, row_h=0.82)
foot(d.p.slides[-1])

d.table("KPI：每一層都看得到數字", ["層級", "指標", "Phase 0 目標（示意）"],
        [["曝光", "Banner・LP 瀏覽（雙邊）", "50 萬次"], ["點擊", "有效點擊／CTR", "6 萬次／12%"],
         ["領券", "優惠券領取數", "1.5 萬張"], ["核銷", "核銷率／導購 GMV", "40%／¥2.4 億"],
         ["回程", "LionTrip 下載／首單", "5,000 次／150 單"], ["熟客", "90 天內回訪率", "20%"]],
        label="KPI", col_w=[1.2, 2.6, 2.4], hot_row=3, size=15, row_h=0.58,
        banner="Phase 0 的數字，就是 Phase 1 分潤費率的依據",
        source="目標值為示意，需依雄獅會員規模、百貨客單與投放預算調整")
foot(d.p.slides[-1])

cl = d.closing("出發前，就是熟客。",
               "Next Step\n① 12 月：三方 kickoff，確認示範點與優惠方案\n"
               "② 簽署導客分潤條件與資料交換原則（只交換匿名事件）\n③ 2027/01：T-Space 雙語專區上線，春節檔期跑第一波")
x = logo_h(cl, BR + "turncloud.png", 4.6, 6.75, 0.34) + 0.45
x = logo_h(cl, BR + "accucrazy-white.png", x, 6.78, 0.27) + 0.45
logo_h(cl, BR + "tspace-light.png", x, 6.75, 0.32)
for sh in cl.shapes:
    if sh.has_text_frame and sh.text_frame.text.startswith("Next Step"):
        for para in sh.text_frame.paragraphs:
            for r in para.runs:
                r.font.color.rgb = d.c["gold"]; r.font.size = Pt(14)

d.save(os.environ.get("OUT", "deck.pptx"))
import json
json.dump(PAGE_MAP, open("assets/video/pages.json", "w"), ensure_ascii=False, indent=1)
print("videos on pages:", sorted(PAGE_MAP))
