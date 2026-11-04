"""雄獅 × 阪急阪神百貨 × 騰雲｜雙程票 Round Trip Pass — PPTX builder (deck_v2)"""
import os, unicodedata
from deck_v2 import Deck, W, H, FRAME, _rgb
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image

IMG = "assets/img/"
d = Deck(frame="#F03742", accent="#FF8400", dark="#1E1A1D", gold="#FFD3A3",
         f_head=os.environ.get("DECK_FONT","Noto Sans TC"), f_body=os.environ.get("DECK_FONT","Noto Sans TC"), f_num="Arial Narrow")
d.footer = "© 雄獅旅遊 × 騰雲｜Confidential"
SOFT = _rgb("#FFF1F2")


def _w(text, per_cjk=0.155, per_lat=0.085):
    return sum(per_cjk if unicodedata.east_asian_width(ch) in "WF" else per_lat for ch in text)


def label(s, text, dark_bg=False, x=0.42, y=0.34):
    w = 0.36 + _w(text, 0.16, 0.09)
    d._round(s, x, y, w, 0.32, "frame" if not dark_bg else "accent", 0.5)
    d._tx(s, x, y + 0.045, w, 0.24, text, 11, color="white", bold=True, align=PP_ALIGN.CENTER)
    return y + 0.32
d._label = label


def fit(s, path, x, y, w, h, border=True):
    """等比縮放放進框內（截圖用，不裁切）。"""
    iw, ih = Image.open(path).size
    r = min(w / iw, h / ih)
    pw, ph = iw * r, ih * r
    px, py = x + (w - pw) / 2, y + (h - ph) / 2
    if border:
        d._rect(s, px - 0.04, py - 0.04, pw + 0.08, ph + 0.08, _rgb("#E2E2E2"))
    s.shapes.add_picture(path, Inches(px), Inches(py), Inches(pw), Inches(ph))
    return px, py, pw, ph


def ai_tag(s, x, y, dark=False):
    d._round(s, x, y, 1.0, 0.26, _rgb("#000000") if not dark else _rgb("#FFFFFF"), 0.5)
    d._tx(s, x, y + 0.04, 1.0, 0.2, "AI 示意圖", 8.5, color="white" if not dark else "ink",
          bold=True, align=PP_ALIGN.CENTER)


def foot(s, dark=False):
    """有結論橫幅的頁，頁尾改白字疊在橫幅上。"""
    on_banner = any(abs(sh.top - Inches(H - 0.78)) < 2000 and sh.width >= Inches(W - 0.01)
                    for sh in s.shapes)
    if on_banner:
        d._tx(s, W - 1.0, H - 0.36, 0.6, 0.22, str(d.n), 8, color="white", align=PP_ALIGN.RIGHT)
    else:
        d._foot(s, dark)


def _cover(code, title, doctype, date, credits, img):
    s = d._slide("dark")
    d._pic(s, img, 0, 0, W, H)
    g = d._rect(s, 0, 0, 8.6, H, _rgb("#000000"))
    d._lin_grad(g, [("1E1A1D", 88000, 0), ("1E1A1D", 70000, 45000), ("1E1A1D", 0, 100000)], angle=0)
    d._rect(s, 0, 0, 0.2, H, "frame")
    d._tx(s, 1.05, 1.15, 7.0, 0.4, code, 15, color="accent", bold=True)
    d._tx(s, 1.0, 1.7, 7.0, 1.6, title[0], 96, color="white", bold=True)
    d._tx(s, 1.05, 3.45, 7.0, 0.7, title[1], 32, color="white", bold=True)
    d._rect(s, 1.05, 4.5, 0.72, 0.06, "frame")
    d._tx(s, 1.05, 4.7, 7.0, 0.4, doctype, 15, color="gold", bold=True)
    d._tx(s, 1.05, 5.25, 7.0, 0.3, date, 12, color="white", font=d.f["num"])
    d._tx(s, 1.05, 5.65, 7.0, 0.8, credits, 11, color="white", spacing=1.5)
    ai_tag(s, W - 1.3, H - 0.5, dark=True)


def _tag(s, x, y, text, col="frame", size=11.5, h=0.42):
    tw = 0.4 + _w(text, 0.17, 0.095)
    d._rect(s, x, y, tw, h, col)
    d._tx(s, x + 0.2, y + (h - 0.28) / 2 + 0.02, tw - 0.3, 0.28, text, size, color="white", bold=True)
    return tw


def exec_page(tag, title, desc, img=None, banner=None):
    s = d._slide("paper"); d._frame(s)
    d._pic(s, img, FRAME, FRAME, W - 2 * FRAME, 3.95, dim=0.06)
    _tag(s, FRAME + 0.3, 3.46, tag)
    d._tx(s, 0.72, 4.32, W - 1.5, 0.55, title, 22, bold=True)
    d._tx(s, 0.72, 5.02, W - 1.5, 1.4, desc, 13, color="mid", spacing=1.6)
    return s
d.exec_page = exec_page


def social_idea(code, channel, title, desc, img=None):
    s = d._slide("dark")
    ih = 5.3
    d._pic(s, img, 0, 0, W, ih, dim=0.08)
    tw = _tag(s, 0.62, ih - 0.7, "Social Idea " + code)
    _tag(s, 0.62 + tw, ih - 0.7, channel, col="dark")
    d._rect(s, 0, ih, W, H - ih, "dark")
    d._tx(s, 0.7, ih + 0.25, W - 1.4, 0.5, title, 22, color="white", bold=True)
    d._tx(s, 0.7, ih + 0.85, W - 1.4, 1.0, desc, 12.5, color="gold", spacing=1.5)
    return s
d.social_idea = social_idea


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
                    r.font.size = Pt(size if r_i else size)
    return s
d.table = big_table


def arrow(s, x, y, w, h, color="frame", shape=MSO_SHAPE.RIGHT_ARROW):
    a = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = d.c[color] if isinstance(color, str) else color
    a.line.fill.background(); a.shadow.inherit = False
    return a


def bars(s, items, x, y, w, row_h=0.5, maxv=None, hot=None, unit="篇"):
    maxv = maxv or max(v for _, v in items)
    for i, (name, v) in enumerate(items):
        yy = y + i * row_h
        d._tx(s, x, yy + 0.08, 1.9, 0.3, name, 13, bold=True, align=PP_ALIGN.RIGHT)
        bw = (w - 3.4) * v / maxv
        d._rect(s, x + 2.05, yy + 0.06, max(0.05, bw), row_h - 0.16,
                "frame" if (hot is None or i in hot) else _rgb("#D9D2D3"))
        d._tx(s, x + 2.15 + bw, yy + 0.08, 1.4, 0.3, f"{v:,} {unit}", 12.5, color="mid",
              bold=True, font=d.f["num"])


def num_card(s, x, y, w, big, lab, sub="", color="frame"):
    d._rect(s, x, y, w, 2.6, _rgb("#F7F5F5"))
    d._rect(s, x, y, w, 0.08, color)
    d._tx(s, x + 0.3, y + 0.35, w - 0.6, 1.0, big, 50, color=color, bold=True, font=d.f["num"])
    d._tx(s, x + 0.3, y + 1.45, w - 0.6, 0.4, lab, 14, bold=True)
    if sub:
        d._tx(s, x + 0.3, y + 1.88, w - 0.6, 0.6, sub, 10.5, color="mid", spacing=1.4)


def steps_right(s, x, y, w, items, start=1, size=13):
    for i, (t, sub) in enumerate(items):
        yy = y + i * 0.92
        o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(yy), Inches(0.44), Inches(0.44))
        o.fill.solid(); o.fill.fore_color.rgb = d.c["frame"]; o.line.fill.background()
        o.shadow.inherit = False
        d._tx(s, x, yy + 0.07, 0.44, 0.3, str(start + i), 13, color="white", bold=True,
              align=PP_ALIGN.CENTER, font=d.f["num"])
        d._tx(s, x + 0.62, yy + 0.02, w - 0.7, 0.36, t, size, bold=True)
        if sub:
            d._tx(s, x + 0.62, yy + 0.4, w - 0.7, 0.45, sub, 10.5, color="mid", spacing=1.35)


# =============================== 01 封面
_cover("LION TRAVEL × 阪急阪神百貨 × 騰雲", ("雙程票", "台日百貨雙向導流計畫"),
        "Partnership Proposal｜One Presentation", "2026.11",
        "提案對象：阪急阪神百貨 經營層 ／ 雄獅旅遊 經營層\n提案單位：騰雲",
        img=IMG + "cover.jpg")

# =============================== 02 Agenda
s = d.info("今天的 60 分鐘", label="Agenda")
ag = [("01", "我們看到什麼", "Pandora 實測 × 日台官方數據", "15 min"),
      ("02", "卡在哪裡", "三方的障礙點與機會點", "10 min"),
      ("03", "雙程票", "策略、IDEA、兩頁 LIFF 示意", "20 min"),
      ("04", "怎麼賺、怎麼跑", "收費模式、試算、時程、分工", "15 min")]
cw = (W - 1.5) / 4 - 0.18
for i, (n, t, sub, m) in enumerate(ag):
    x = 0.72 + i * (cw + 0.18)
    d._rect(s, x, 2.0, cw, 3.9, SOFT if i != 2 else d.c["frame"])
    col = "frame" if i != 2 else "white"
    d._tx(s, x + 0.3, 2.25, cw - 0.6, 1.0, n, 60, color=col, bold=True, font=d.f["num"])
    d._tx(s, x + 0.3, 3.55, cw - 0.6, 0.5, t, 21, color="ink" if i != 2 else "white", bold=True)
    d._tx(s, x + 0.3, 4.15, cw - 0.6, 0.8, sub, 12, color="mid" if i != 2 else "white", spacing=1.5)
    d._tx(s, x + 0.3, 5.35, cw - 0.6, 0.3, m, 12, color=col, bold=True, font=d.f["num"])
foot(s)

# =============================== 03 Brief Recap
s = d.info("Brief Recap：讓兩邊的客人，互相變成對方的客人", label="Brief Recap",
           banner="騰雲站在中間：搭通道、看數據、養熟客、做投放，按點擊與成交收費")
blocks = [("Goal", "◎", "建立雄獅 App ⇄ 日本百貨官網\n雙向導流，點擊與成交都能追蹤"),
          ("TA", "☺", "去程｜雄獅會員中的赴日台灣旅客\n回程｜阪急阪神百貨的日本顧客"),
          ("Message", "✦", "台灣客人落地前就是百貨熟客\n日本客人出發前就認識雄獅")]
for i, (t, ic, body) in enumerate(blocks):
    y = 1.85 + i * 1.32
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8), Inches(y), Inches(0.82), Inches(0.82))
    o.fill.solid(); o.fill.fore_color.rgb = d.c["frame"]; o.line.fill.background(); o.shadow.inherit = False
    d._tx(s, 0.8, y + 0.16, 0.82, 0.5, ic, 24, color="white", bold=True, align=PP_ALIGN.CENTER)
    d._tx(s, 1.85, y - 0.02, 1.6, 0.35, t, 15, color="frame", bold=True, font=d.f["num"])
    d._tx(s, 1.85, y + 0.32, 4.9, 0.9, body, 13, spacing=1.45)
roles = [("雄獅旅遊", "台灣旅客入口", "會員 App／LionTrip 國際版\n出團、自由行、雄獅幣"),
         ("阪急阪神百貨", "日本顧客入口", "官網、會員、POS 核銷\n首波：梅田兩本店＋博多＋MEN'S"),
         ("騰雲", "中間的系統", "中轉系統｜Pandora 雙邊情報\n熟客系統｜廣告推廣")]
for i, (t, k, body) in enumerate(roles):
    x = 7.05 + (i % 3) * 1.92
    col = "frame" if i < 2 else "dark"
    d._round(s, x, 1.95, 1.78, 3.7, SOFT if i < 2 else d.c["dark"], 0.08)
    d._tx(s, x + 0.18, 2.2, 1.45, 0.3, k, 10, color="frame" if i < 2 else "accent", bold=True)
    d._tx(s, x + 0.18, 2.55, 1.45, 0.9, t, 17, color="ink" if i < 2 else "white", bold=True, spacing=1.2)
    d._tx(s, x + 0.18, 3.55, 1.5, 2.0, body, 10.5, color="mid" if i < 2 else "gold", spacing=1.55)
foot(s)

# =============================== 04 章節：調查
d.divider("What we found.", "Pandora 社群聲量實測 × 日台官方統計\n兩次查詢，共 24,673 篇台灣社群貼文")

# =============================== 05 台灣客
d.stat_big("台灣人，是日本百貨最穩的客人", "673萬", "2025 訪日台灣旅客（人次）",
           ["在日消費 1.2 兆日圓，全球第二\n其中 32.9% 花在購物",
            "2026 年 8 月全國百貨免稅：客數 −9.5%\n台灣・香港・韓國仍持續成長",
            "42% 的台灣旅客，已經去過日本 6 次以上"],
           label="調查｜市場",
           banner="客源不確定的年代，台灣客是最穩的那一塊",
           source="Data source: 台灣觀光統計 2025（やまとごころ 2026）；觀光廳 訪日外國人消費動向調查 2025（xmy.tw 整理）；"
                  "日本百貨店協會 2026/08（訪日ラボ 2026/10/01）；JNTO 2025（旅報 ttnmedia）")
foot(d.p.slides[-1])

# =============================== 06 阪急阪神
s = d.info("阪急本店連續創新高，但入境客的組成正在換血", label="調查｜阪急阪神百貨",
           banner="中國客退潮留下的那一塊，要有人補上",
           source="Data source: H2O リテイリング 2026 年 6 月度売上速報；訪日ラボ 2026/05/20（H2O 2026 年 3 月期通期決算）；朝日新聞")
cw = (W - 1.5) / 3 - 0.2
num_card(s, 0.72, 1.95, cw, "117.1%", "阪急本店 2026/6 營收年比", "6 個月連續刷新歷史紀錄")
num_card(s, 0.72 + cw + 0.3, 1.95, cw, "+3成", "阪急阪神百貨 2026/6 免稅營收", "阪急うめだ本店＝全國免稅營收第一的單店")
num_card(s, 0.72 + 2 * (cw + 0.3), 1.95, cw, "−2成", "H2O 2026/3 期 通年入境營收", "中國客數 −4 成，其他地區穩定", color="dark")
foot(s)

# =============================== 07 Pandora 品牌聲量
s = d.info("日本行程的討論，有一大半在 OTA 手上", label="調查｜Pandora 品牌聲量",
           banner="雄獅贏在團體與主題行程；落地之後的「當地消費」，還沒有入口",
           source="Data source: Pandora 社群聲量實測，2025/11/01–2026/11/01，Threads／IG／Dcard／PTT／FB，"
                  "品牌 ×（日本｜大阪｜東京｜京都｜百貨｜購物｜行程｜團），N=10,401。雄獅計數含少量同名雜訊。")
bars(s, [("KKday", 4691), ("Klook", 3511), ("雄獅旅遊", 1682), ("可樂旅遊", 974),
         ("易遊網", 559), ("東南旅遊", 83)], 0.9, 1.95, 8.4, row_h=0.6, hot=[2])
d._round(s, 9.55, 2.0, 3.05, 3.4, SOFT, 0.06)
d._tx(s, 9.8, 2.2, 2.6, 0.3, "平台分布", 11, color="frame", bold=True)
d._tx(s, 9.8, 2.55, 2.6, 2.7, "Threads　6,764\nInstagram　2,184\nDcard　884\nPTT　508\nFB　61", 14,
      bold=True, spacing=1.7, font=d.f["num"])
foot(s)

# =============================== 08 Pandora 阪急話題
s = d.info("台灣人聊阪急，聊的是 B1、精品和退稅", label="調查｜Pandora 百貨聲量",
           banner="阪神虎的討論量，比退稅還多：這是阪急阪神獨有的牌",
           source="Data source: Pandora 社群聲量實測，實際覆蓋 2026/06/15–11/01，日本百貨 ×（退稅｜折扣｜優惠｜戰利品…），"
                  "N=14,272；阪急｜阪神子集 3,314 篇；阪神虎／甲子園／林威助為全資料集計數。")
bars(s, [("阪神虎・甲子園", 969), ("B1 美食・伴手禮", 444), ("精品・美妝", 122),
         ("優惠・折扣", 101), ("退稅・免稅", 72)], 0.9, 2.0, 8.6, row_h=0.62, hot=[0, 1])
d._round(s, 9.7, 2.0, 2.9, 3.2, d.c["dark"], 0.06)
d._tx(s, 9.95, 2.25, 2.4, 0.3, "阪急｜阪神 相關", 11, color="accent", bold=True)
d._tx(s, 9.95, 2.65, 2.4, 1.0, "3,314", 54, color="white", bold=True, font=d.f["num"])
d._tx(s, 9.95, 3.75, 2.4, 1.3, "篇台灣社群貼文\n4.5 個月內", 12, color="gold", spacing=1.5)
foot(s)

# =============================== 09 UGC 攻略
s = d.info("台灣人逛阪急，靠的是網友整理的攻略", label="調查｜UGC",
           banner="攻略在網友手上、優惠在櫃檯手上，中間沒有人接",
           source="UGC: threads.com/@osaka_rental_car/post/DcfLv9AkfYs（9.76 萬瀏覽）；threads.com/@mani_tokyo_go/post/DbZea3XD95j"
                  "　爬取日 2026/11/02")
fit(s, IMG + "ugc/u2-b1.png", 0.8, 1.75, 4.6, 4.3)
fit(s, IMG + "ugc/u5-umeda.png", 5.65, 1.75, 4.2, 4.3)
d._tx(s, 10.15, 2.1, 2.5, 3.6, "「去大阪真的拜託你們直接衝阪急百貨 B1！」\n\n9.76 萬人看過這篇攻略。\n\n百貨自己的聲音，在台灣社群幾乎聽不到。",
      13, bold=True, spacing=1.55)
foot(s)

# =============================== 10 UGC 退稅
s = d.info("退 10% 的好日子，過去了", label="調查｜UGC × 時事",
           banner="11/1 起先付後退：台灣人還是會買，只是更會算",
           source="UGC: threads.com/@linshibi/post/Dc8fX1kGqn0（52.1 萬瀏覽）；threads.com/@taiwan_japanticket/post/De_AVqZk9Lr"
                  "　爬取日 2026/11/02")
fit(s, IMG + "ugc/u1-linshibi.png", 0.8, 1.75, 4.1, 4.3)
fit(s, IMG + "ugc/u4-newrule.png", 5.1, 1.75, 3.2, 4.3)
d._pic(s, IMG + "taxrefund.jpg", 8.6, 1.75, 4.0, 2.4)
ai_tag(s, 8.7, 1.85)
d._tx(s, 8.6, 4.35, 4.0, 1.7, "570 日圓的稅金，\n退回來只剩 238 日圓。\n\n52.1 萬人看過這篇。", 14, bold=True, spacing=1.5)
foot(s)

# =============================== 11 雄獅品牌
s = d.info("雄獅最會的，是幫人找到出發的理由", label="調查｜雄獅品牌",
           banner="把「理由」延伸到落地之後：去哪買、怎麼買最划算",
           source="UGC: threads.com/@baron112233/post/DXrG0QTD4Yz（120 萬瀏覽）；風傳媒 2026/03/31（PTT Stock 轉載）；instagram.com/reel/DcBAiOmS4Zo")
fit(s, IMG + "ugc/u6-pikmin.png", 0.8, 1.75, 4.9, 4.3)
facts = [("32.87億", "2026/2 單月營收，全台旅行社第一"), ("120萬", "皮克敏團貼文瀏覽數"),
         ("24,472", "Fujirock「腹肌團」IG 按讚")]
for i, (b, t) in enumerate(facts):
    y = 1.85 + i * 1.38
    d._rect(s, 6.2, y, 6.4, 1.2, SOFT)
    d._rect(s, 6.2, y, 0.08, 1.2, "frame")
    d._tx(s, 6.55, y + 0.17, 2.8, 0.9, b, 38, color="frame", bold=True, font=d.f["num"])
    d._tx(s, 9.35, y + 0.4, 3.2, 0.5, t, 13, bold=True)
foot(s)

# =============================== 12 Cultural
d.truth("Cultural Relevancy", "台灣人在日本，\n有自己的主場。", img=IMG + "stadium.jpg",
        sub="阪神虎／甲子園相關討論 969 篇；富邦悍將 × 阪神虎聯名貼文 4,380♥\n"
            "阪神虎和阪急阪神百貨，屬於同一個集團\n"
            "Data source: Pandora 2026/06/15–11/01；instagram.com/p/DbUob8-CYnx　｜　AI 示意圖")

# =============================== 13 台日落差
s = d.info("反過來看：日本人來台灣，只有台灣人去日本的四分之一", label="調查｜日本市場",
           banner="百貨的日本熟客，是雄獅還沒打開的市場",
           source="Data source: travelvoice 2026/04/16（台灣觀光署 2025）；note.com「データから見る 4.5 倍のギャップ」")
d._tx(s, 0.9, 2.05, 5.0, 0.4, "台灣 → 日本", 16, color="mid", bold=True)
d._tx(s, 0.85, 2.45, 5.5, 1.8, "673萬", 110, color="frame", bold=True, font=d.f["num"])
d._tx(s, 7.6, 2.05, 5.0, 0.4, "日本 → 台灣", 16, color="mid", bold=True)
d._tx(s, 7.55, 2.45, 5.5, 1.8, "148萬", 110, color="dark", bold=True, font=d.f["num"])
d._round(s, 5.4, 3.05, 2.0, 0.8, d.c["accent"], 0.5)
d._tx(s, 5.4, 3.17, 2.0, 0.5, "4.5 倍", 22, color="white", bold=True, align=PP_ALIGN.CENTER)
d._tx(s, 0.9, 4.65, 11.5, 0.6, "2025 年人次。訪台日本人年增 12.4%，成長比整體訪台市場更快。", 13, color="mid")
foot(s)

# =============================== 14 章節：痛點
d.divider("卡在哪裡", "三方各有一塊拼圖，但沒有接在一起")

# =============================== 15 三方障礙／機會
d.table("三方的障礙點與機會點", ["", "障礙點", "機會點"],
        [["台灣旅客", "「退稅縮水了，優惠要自己翻攻略找」", "出發前就在雄獅 App 領好專屬禮遇"],
         ["日本百貨", "「台灣客很多，但不知道是誰、從哪來、會不會再來」", "每一次點擊、領券、核銷都留下紀錄"],
         ["雄獅旅遊", "「日本自由行的流量在 OTA，在日本人眼中沒有名字」", "百貨官網＝日本中高端客群的入口"]],
        label="痛點", col_w=[1.2, 3.6, 3.0], hot_row=None, size=16, row_h=1.0,
        banner="缺的不是流量，是一條能被追蹤的雙向通道")
foot(d.p.slides[-1])

# =============================== 16 挑戰
d.four_grid("要讓兩邊的客人互通，有三道門要先打開", "三個挑戰",
            [("挑戰 1\n系統不通", "雄獅 App、百貨官網、POS、會員系統各自獨立，客人走過去就斷線"),
             ("挑戰 2\n成效說不清", "導過去的客人買了多少，沒人算得出來，就談不了分潤"),
             ("挑戰 3\n個資與信任", "跨國會員資料不能隨便交換，兩邊都要守得住")],
            label="痛點｜挑戰")
foot(d.p.slides[-1])

# =============================== 17 突圍四格
d.four_grid("騰雲在中間，做四件事", "看得見、算得出、分得到",
            [("中轉系統", "雙語 LIFF 頁＋追蹤碼＋優惠券發放與核銷 API\n只交換事件，不交換個資"),
             ("Pandora\n雙邊市場情報", "台灣社群看日本百貨、日本社群看台灣旅遊，每週一份報告"),
             ("熟客系統", "同一位客人從點擊、領券、核銷到回訪，貼標分群、自動再行銷"),
             ("廣告推廣", "Meta／LINE／Google 雙邊投放，用核銷數據優化出價")],
            label="突圍策略", banner="每一次導流都有紀錄，才談得了按成果收費")
foot(d.p.slides[-1])

# =============================== 18 章節：策略
d.divider("Strategy.", "Product Truth × Fan Truth × Cultural Relevancy")

# =============================== 19 Venn
d.venn("三個真相交會的地方", ["Product Truth", "Fan Truth", "Cultural Relevancy"],
       ["雄獅：台灣營收最大旅行社\n阪急本店：免稅營收全國第一\n騰雲：追蹤到核銷的中轉系統",
        "「退8~10%的好日子\n已經過去了」\n台灣人還是會買，\n只是更會算",
        "日本是台灣人的灶腳\n42% 去過 6 次以上\n阪神虎是台灣人的主場"],
       "Proposition｜出發前，就是熟客。", label="策略")
foot(d.p.slides[-1])

# =============================== 20 Proposition
d.truth("Proposition", "出發前，\n就是熟客。", img=IMG + "depachika.jpg",
        sub="台灣客人落地前，已經是阪急的熟客。\n日本客人出發前，已經是雄獅的熟客。\nAI 示意圖")

# =============================== 21–24 build-up
d.quote("一年 673 萬人次的台灣客人\n大多數是走進店裡\n才第一次認識這家百貨", label="Thinking…")
d.quote("那如果\n他們在出發前\n就已經收到邀請函呢？", label="Thinking…")
d.quote("反過來也一樣\n阪急的日本熟客\n下一趟旅行，為什麼不是台灣？", label="Thinking…")
d.quote("旅行社最懂的一件事：\n一張票，要能去，\n也要能回來。", label="Way in", size=38)

# =============================== 25 IDEA
d.idea("IDEA", "雙程票\nRound Trip Pass",
       "一張票，兩個方向。\n雄獅 App 裡放百貨的門，\n百貨官網裡放雄獅的門。\n騰雲記下每一次進出，按點擊與成交分潤。",
       letter="", img=IMG + "idea-bg.jpg")

# =============================== 26 運作架構
s = d.info("雙程票怎麼運作：兩個入口、一個中轉、全程可追蹤", label="雙程票｜架構",
           banner="去程：台灣客 → 百貨　｜　回程：日本客 → 雄獅　｜　騰雲：記錄、核銷、結算")
def node(x, y, w, h, t, sub, fill, fg="ink", subc="mid"):
    d._round(s, x, y, w, h, fill, 0.12)
    d._tx(s, x + 0.15, y + 0.18, w - 0.3, 0.4, t, 14, color=fg, bold=True, align=PP_ALIGN.CENTER)
    d._tx(s, x + 0.15, y + 0.6, w - 0.3, h - 0.7, sub, 10, color=subc, align=PP_ALIGN.CENTER, spacing=1.35)
for row, (a, la, b, lb, tag) in enumerate([
        (("雄獅會員 App", "台灣旅客"), ("LIFF 中文頁", "百貨介紹・折扣碼・優惠"),
         ("阪急阪神 櫃檯／POS", "出示 QR 核銷"), None, "去程票"),
        (("阪急阪神 官網", "日本顧客"), ("LIFF 日文頁", "雄獅海外行程・下載優惠"),
         ("LionTrip App", "下載・首單訂購"), None, "回程票")]):
    y = 2.0 + row * 1.85
    d._round(s, 0.72, y + 0.42, 1.25, 0.42, "frame" if row == 0 else "dark", 0.5)
    d._tx(s, 0.72, y + 0.5, 1.25, 0.3, tag, 11, color="white", bold=True, align=PP_ALIGN.CENTER)
    node(2.15, y, 2.3, 1.3, a[0], a[1], SOFT)
    arrow(s, 4.55, y + 0.5, 0.5, 0.3)
    node(5.15, y, 2.3, 1.3, la[0], la[1], SOFT)
    arrow(s, 7.55, y + 0.5, 0.5, 0.3)
    node(10.25, y, 2.35, 1.3, b[0], b[1], SOFT)
    arrow(s, 9.65, y + 0.5, 0.5, 0.3)
d._round(s, 8.12, 1.95, 1.45, 3.25, d.c["dark"], 0.12)
d._tx(s, 8.17, 2.3, 1.35, 0.5, "騰雲\n中轉", 15, color="white", bold=True, align=PP_ALIGN.CENTER, spacing=1.2)
d._tx(s, 8.17, 3.25, 1.35, 1.8, "追蹤碼\n點擊紀錄\n核銷 API\n分潤結算", 10, color="gold",
      align=PP_ALIGN.CENTER, spacing=1.6)
foot(s)

# =============================== 27 LIFF A
s = d.info("去程票：雄獅 App 裡，放一扇阪急阪神的門", label="LIFF 示意 A｜雄獅端（中文）",
           banner="出發前領好禮遇，落地直接核銷：每一步都回報給百貨與雄獅")
d._pic(s, IMG + "liff-tw.jpg", 0.62, 1.55, 7.0, 3.92)
ai_tag(s, 0.75, 1.68)
steps_right(s, 7.95, 1.6, 4.7, [
    ("入口：會員 App「日本百貨禮遇」", "首頁 Banner＋行程頁（大阪／福岡團）＋出發前推播"),
    ("LIFF：介紹阪急阪神四家店", "阪急梅田本店・阪神梅田本店・博多阪急・阪急 MEN'S"),
    ("領券：結帳出示 QR，現折 5%", "折扣幅度為示意，以阪急阪神實際方案為準"),
    ("回饋：雄獅幣 2 倍", "綁定 L.I.O.N 會員等級，回台後還會再用")])
d._tx(s, 0.62, 5.6, 7.0, 0.4, "內容素材：台灣旅客專屬折扣碼／B1 甜點地圖／退稅新制懶人包／阪神虎主場日", 10.5, color="mid")
foot(s)

# =============================== 28 情境 A
d.exec_page("去程票｜使用情境", "落地那一刻，她已經是阪急的熟客",
            "出發前在雄獅 App 領券 → 抵達梅田直奔 B1 → 櫃檯出示 QR 核銷 → 騰雲記下這一筆\n"
            "點擊、領券、核銷、金額全部可追蹤，也是 CPC 與 GMV 分潤的計算依據（AI 示意圖）",
            img=IMG + "depachika.jpg")

# =============================== 29 LIFF B
s = d.info("回程票：阪急官網裡，放一扇雄獅的門", label="LIFF 示意 B｜百貨端（日文）",
           banner="百貨的日本熟客，第一次在信任的地方看見雄獅")
d._pic(s, IMG + "liff-jp.jpg", 0.62, 1.55, 7.0, 3.92)
ai_tag(s, 0.75, 1.68)
steps_right(s, 7.95, 1.6, 4.7, [
    ("入口：百貨官網・會員電子報", "「台湾へ、ふらっと。」專區與 Banner"),
    ("LIFF：雄獅的台灣與海外行程", "台北美食散步・九份十分一日遊・鐵道旅行・郵輪"),
    ("下載：LionTrip App 首單 ¥3,000 OFF", "優惠碼 UMEDA3000（示意），可追蹤到百貨來源"),
    ("回報：點擊、下載、訂單", "騰雲每週回報雙方，百貨也拿得到分潤")])
d._tx(s, 0.62, 5.6, 7.0, 0.4, "LionTrip App 已支援英文・日文・繁中（App Store 資訊）；行程數與客服時段為示意", 10.5, color="mid")
foot(s)

# =============================== 30 情境 B
d.exec_page("回程票｜使用情境", "百貨的日本熟客，下一趟旅行選台灣",
            "在阪急官網看到雄獅的台灣行程 → 下載 LionTrip App 領 ¥3,000 → 預訂九份一日遊\n"
            "百貨把熟客的信任借給雄獅，雄獅把台灣的行程帶給百貨的熟客（AI 示意圖）",
            img=IMG + "jp-couple.jpg")

# =============================== 31 收費模式
s = d.info("騰雲的角色像 trivago：站在中間，按成果收費", label="收費模式",
           banner="沒有成交就不收抽成：兩邊只為看得見的結果付錢")
d._round(s, 0.8, 2.1, 2.9, 3.3, SOFT, 0.08)
d._tx(s, 0.95, 2.35, 2.6, 0.4, "雄獅旅遊", 18, bold=True, align=PP_ALIGN.CENTER)
d._tx(s, 0.95, 2.85, 2.6, 2.4, "導客人去百貨\n＝百貨付費\n\n收客人回 App\n＝雄獅付費", 12, color="mid", align=PP_ALIGN.CENTER, spacing=1.5)
d._round(s, 9.65, 2.1, 2.9, 3.3, SOFT, 0.08)
d._tx(s, 9.8, 2.35, 2.6, 0.4, "阪急阪神百貨", 18, bold=True, align=PP_ALIGN.CENTER)
d._tx(s, 9.8, 2.85, 2.6, 2.4, "官網導客人去雄獅\n＝百貨收分潤\n\n台灣客人來核銷\n＝百貨付費", 12, color="mid", align=PP_ALIGN.CENTER, spacing=1.5)
arrow(s, 3.85, 3.5, 0.7, 0.4, shape=MSO_SHAPE.LEFT_RIGHT_ARROW)
arrow(s, 8.8, 3.5, 0.7, 0.4, shape=MSO_SHAPE.LEFT_RIGHT_ARROW)
d._round(s, 4.7, 1.95, 3.95, 3.6, d.c["dark"], 0.08)
d._tx(s, 4.85, 2.12, 3.65, 0.4, "騰雲收的三種費用", 14, color="accent", bold=True, align=PP_ALIGN.CENTER)
for i, (t, sub) in enumerate([("CPC 點擊費", "每次有效點擊計費（示意 ¥20）"),
                              ("CPA 核銷費（選配）", "領券並到店核銷才計費"),
                              ("GMV 抽成", "核銷訂單金額 × 費率（示意 3–5%）")]):
    y = 2.65 + i * 0.92
    d._round(s, 4.95, y, 3.45, 0.78, _rgb("#2E282C"), 0.15)
    d._tx(s, 5.1, y + 0.08, 3.2, 0.35, t, 14, color="white", bold=True)
    d._tx(s, 5.1, y + 0.43, 3.2, 0.3, sub, 10, color="gold")
foot(s)

# =============================== 32 試算
d.table("一年跑下來的樣子（試算示意）", ["", "去程｜台灣客 → 阪急阪神", "回程｜日本客 → 雄獅"],
        [["年有效點擊", "300,000 次", "50,000 次"], ["CPC", "¥20／次", "¥20／次"],
         ["點擊費小計", "¥600 萬", "¥100 萬"], ["核銷／成交率", "15%", "2%"],
         ["平均客單", "¥40,000", "¥120,000"], ["導購 GMV", "¥18 億", "¥1.2 億"],
         ["GMV 抽成", "3%", "5%"], ["抽成小計", "¥5,400 萬", "¥600 萬"]],
        label="收費模式｜試算", col_w=[1.4, 2.6, 2.6], hot_row=5, size=13, row_h=0.47,
        banner="雙向合計：年導購 GMV 約 ¥19.2 億，騰雲服務收入約 ¥6,700 萬（試算示意）",
        source="試算示意：所有假設須以雄獅會員赴日人數、阪急阪神實際客單與三方合約費率替換")
foot(d.p.slides[-1])

# =============================== 33 Pandora 情報
d.exec_page("騰雲｜Pandora 雙邊市場情報", "每週一份報告：兩邊的客人在聊什麼",
            "台灣社群：哪家百貨、哪個櫃位、哪個商品正在燒　｜　日本社群：日本人想去台灣哪裡\n"
            "直接決定下週 LIFF 放什麼優惠、百貨官網推哪條雄獅行程（畫面與數字為 AI 示意）",
            img=IMG + "pandora-dash.jpg")

# =============================== 34 熟客循環
s = d.info("熟客系統：一位客人去一次日本，變成每年都回來", label="騰雲｜熟客系統",
           banner="同一位客人的點擊、核銷、回訪串成一條線，兩邊都看得到")
loop = [("點擊", "LIFF 進站"), ("領券", "綁定會員 ID"), ("核銷", "櫃檯 QR"), ("貼標", "B1／精品／虎迷"),
        ("回訪", "下次出發前推播")]
cw = 2.05
for i, (t, sub) in enumerate(loop):
    x = 0.85 + i * (cw + 0.42)
    o = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.2), Inches(2.15), Inches(1.65), Inches(1.65))
    o.fill.solid(); o.fill.fore_color.rgb = d.c["frame"] if i != 4 else d.c["accent"]
    o.line.fill.background(); o.shadow.inherit = False
    d._tx(s, x + 0.2, 2.72, 1.65, 0.5, t, 20, color="white", bold=True, align=PP_ALIGN.CENTER)
    d._tx(s, x, 4.0, cw, 0.4, sub, 12, color="mid", bold=True, align=PP_ALIGN.CENTER)
    if i < 4:
        arrow(s, x + 1.95, 2.8, 0.45, 0.32)
d._tx(s, 0.85, 4.75, 11.6, 0.6, "個資不出境、不落地：雙方只交換匿名事件 ID 與核銷結果，會員資料仍留在各自系統", 12.5, bold=True, color="frame")
foot(s)

# =============================== 35 章節：Activation
d.divider("Activation.", "讓雙程票一上線，就有聲量", solid=False, img=IMG + "stadium.jpg")

# =============================== 36–38 Social Idea
d.social_idea("A-1", "雄獅 App × 阪神梅田本店 × 甲子園", "阪神虎主場日：雄獅甲子園應援團",
              "雄獅開甲子園觀賽團，行程含阪神梅田本店虎迷商品專屬優惠；台灣虎迷穿應援服逛百貨，社群自然擴散\n"
              "球團合作需另洽，此為提案方向（AI 示意圖）", img=IMG + "stadium.jpg")
d.social_idea("A-2", "雄獅 App LIFF ＋ Threads", "退稅補給站：新制縮水的，雄獅幫你補回來",
              "11/1 新制上路，網友算出退稅剩 3.7%。LIFF 首波主打「台灣旅客專屬 5% 禮遇」＋退稅新制懶人包，接住這波討論\n"
              "官方帳號到退稅討論串下回覆懶人包（Threads 海巡）（AI 示意圖）", img=IMG + "taxrefund.jpg")
d.social_idea("A-3", "阪急うめだ本店 催事場 × LionTrip", "台湾フェア × 雄獅：把台灣帶進阪急",
              "阪急本店的台灣物產展加開雄獅旅遊攤位，掃碼下載 LionTrip 領 ¥3,000；百貨的日本熟客現場就能訂台灣行程\n"
              "催事檔期與規模依阪急年度企劃（AI 示意圖）", img=IMG + "taiwan-fair.jpg")

# =============================== 39 時程
s = d.info("先從梅田跑起來，再擴到名單上的 34 家", label="時程",
           banner="Phase 0 用兩家本店驗證數字，數字對了再複製")
d.timeline(s, 1.95, ["2026/12", "2027/02", "2027/04", "2027/06", "2027/09", "2027/12"],
           [("Phase 0｜PoC：阪急梅田本店・阪神梅田本店", 0.0, 0.32),
            ("Phase 1｜擴大：博多阪急・阪急 MEN'S＋阪神虎開季", 0.22, 0.6),
            ("Phase 2｜地方百貨：名單 34 家依序接入", 0.52, 1.0)])
cw = (W - 1.5) / 3 - 0.2
for i, (t, body) in enumerate([
        ("Phase 0　2026/12–2027/02", "雙語 LIFF 上線、優惠方案定案\n追蹤碼與核銷 API 串接\n春節檔期測第一波數字"),
        ("Phase 1　2027/02–2027/07", "店舖擴到四家\n阪神虎開季 × 甲子園應援團\n櫻花季、暑假兩波投放"),
        ("Phase 2　2027/06–2027/12", "地方百貨分批接入\n雄獅團體行程排入地方百貨\n台湾フェア × 雄獅")]):
    x = 0.72 + i * (cw + 0.3)
    d._rect(s, x, 3.6, cw, 2.2, _rgb("#F7F5F5"))
    d._rect(s, x, 3.6, cw, 0.07, "frame")
    d._tx(s, x + 0.25, 3.82, cw - 0.5, 0.4, t, 13.5, color="frame", bold=True)
    d._tx(s, x + 0.25, 4.3, cw - 0.5, 1.5, body, 12, spacing=1.6)
foot(s)

# =============================== 40 名單
s = d.info("地方百貨，更需要台灣客人", label="Phase 2｜百貨名單",
           banner="大城市的免稅在成長，地方在苦戰：雄獅的團體行程，能把客人帶到地方",
           source="名單依客戶提供資料（共 34 家，＊為原始資料標記）；「10 都市好調・地方苦戰」見 訪日ラボ 2026/10/01")
names = ["阪急阪神集團＊", "仙台三越", "藤崎＊", "藤井百貨", "京急百貨", "Saikaya", "丸廣百貨", "八木橋",
         "水戶京成百貨", "Suzuran", "岡島", "長野東急百貨", "井上", "遠鐵百貨", "名鐵百貨", "大和百貨",
         "山陽百貨", "津松菱", "金澤丸越百貨", "京阪百貨", "丸由", "天滿屋", "福屋", "伊予鐵高島屋",
         "高知大丸", "博多大丸", "井筒屋", "濱屋百貨", "鶴屋百貨＊", "TOKIWA", "山形屋", "Ryubo",
         "櫻野百貨", "川德"]
cols, cw2, ch2 = 4, 1.72, 0.37
for i, n in enumerate(names):
    x = 0.72 + (i % cols) * (cw2 + 0.08)
    y = 1.75 + (i // cols) * (ch2 + 0.06)
    hot = i == 0
    d._round(s, x, y, cw2, ch2, d.c["frame"] if hot else SOFT, 0.3)
    d._tx(s, x, y + 0.07, cw2, 0.25, n, 10, color="white" if hot else "ink", bold=hot,
          align=PP_ALIGN.CENTER)
d._pic(s, IMG + "regional.jpg", 8.15, 1.75, 4.55, 4.5)
ai_tag(s, 8.25, 1.85)
foot(s)

# =============================== 41 KPI
d.table("KPI：每一層都看得到數字", ["層級", "指標", "Phase 0 目標（示意）"],
        [["曝光", "LIFF 頁瀏覽（雙邊）", "50 萬次"], ["點擊", "有效點擊／CTR", "6 萬次／12%"],
         ["領券", "優惠券領取數", "1.5 萬張"], ["核銷", "核銷率／導購 GMV", "40%／¥2.4 億"],
         ["回程", "LionTrip 下載／首單", "5,000 次／150 單"], ["熟客", "90 天內回訪率", "20%"]],
        label="KPI", col_w=[1.2, 2.6, 2.4], hot_row=3,
        banner="Phase 0 的數字，就是 Phase 1 簽約費率的依據",
        source="目標值為示意，需依雄獅會員規模、阪急阪神客單與投放預算調整")
foot(d.p.slides[-1])

# =============================== 42 分工
d.table("三方分工：各自守好自己的那一段", ["", "雄獅旅遊", "阪急阪神百貨", "騰雲"],
        [["入口", "會員 App 入口・推播", "官網・電子報入口", "雙語 LIFF 製作"],
         ["優惠", "雄獅幣・行程優惠", "折扣方案・核銷流程", "優惠券系統・核銷 API"],
         ["數據", "會員 ID（匿名）", "核銷結果（匿名）", "追蹤・歸因・結算報表"],
         ["推廣", "出團行程排入百貨", "催事場・店內露出", "Pandora 情報・雙邊投放"]],
        label="Work Division", col_w=[0.9, 2.2, 2.2, 2.2], size=14, row_h=0.8)
foot(d.p.slides[-1])

# =============================== 43 Closing
cl = d.closing("出發前，就是熟客。",
          "Next Step\n① 12 月：三方 kickoff，確認 PoC 店舖與優惠方案\n"
          "② 簽署資料交換原則：只交換匿名事件，不交換個資\n③ 2027/01：雙語 LIFF 上線測試，春節檔期跑第一波")

for sh in cl.shapes:
    if sh.has_text_frame and sh.text_frame.text.startswith("Next Step"):
        for para in sh.text_frame.paragraphs:
            for r in para.runs: r.font.color.rgb = d.c["gold"]; r.font.size = Pt(14)

d.save("deck.pptx")
