"""雄獅品牌 Banner 版型：HTML 排版 → Chrome 輸出。mode=full 出靜態圖；mode=ov 出透明主視覺洞的疊層給動態用。"""
import os, subprocess, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
A = "file://" + ROOT + "/assets/img/"

BANNERS = {
 "b2-clay":   dict(kind="out", hero="clay", dept="hhd-short", eyebrow="雄獅會員限定", h="出發前，<br>就是熟客。", sub="日本百貨優惠專區｜95折＋免稅", cta="立即領券"),
 "b3-taxrefund": dict(kind="out", hero="tax", dept="hhd-short", eyebrow="11/1 退稅新制", h="退稅縮水？<br>雄獅幫你補回來", sub="雄獅會員專屬 95折＋免稅券", cta="限時領取"),
 "b4-b1map":  dict(kind="out", hero="b1map", dept="hankyu-honten", eyebrow="阪急うめだ本店", h="阪急 B1<br>甜點地圖", sub="伴手禮 95折＋免稅｜雄獅會員限定", cta="看甜點地圖"),
 "b6-ticket": dict(kind="out", hero="ticket", dept="hhd-short", eyebrow="台北 ⇄ 大阪", h="一張票，<br>行程＋百貨", sub="報名大阪團，隨票附贈百貨 95折券", cta="看大阪行程"),
 "b5-tigers": dict(kind="out", hero="tigers", dept="hhd-short", eyebrow="阪神梅田本店 × 雄獅", h="虎迷限定<br>應援商品 95折", sub="雄獅甲子園應援團 報名中", cta="立即報名", accent="#FFD000"),
 "b7-sakura": dict(kind="out", hero="sakura", dept="hhd-short", eyebrow="2027 春假", h="櫻花季<br>先領券再出發", sub="日本百貨禮遇 95折＋免稅", cta="3/1 開放領取"),
 "b8-jp-clay": dict(kind="in", hero="jpclay", dept="hhd-short", eyebrow="百貨店会員さま限定", h="台湾へ、<br>ふらっと。", sub="LionTrip アプリで台湾ツアー ¥3,000 OFF", cta="アプリで予約"),
 "b10-jp-square": dict(kind="square", hero="jiufen", dept="hhd-short", eyebrow="会員さまへ、台湾旅のご提案", h="台湾フェア、開催中。", sub="LionTrip アプリで台湾ツアー ¥3,000 OFF", cta="詳しくはこちら"),
 "b11-lt-hankyu": dict(kind="in", hero="b1map", dept="hankyu-honten", eyebrow="LionTrip Members Only", h="Hankyu B1<br>Sweets &amp; Gifts", sub="5% OFF + Tax-free｜阪急うめだ本店", cta="Get Coupon"),
 "b9-story":  dict(kind="story", hero="umeda", dept="hhd-short", eyebrow="雄獅會員限定", h="出發前，<br>就是熟客。", sub="阪急阪神・藤崎・鶴屋 等70家日本百貨", cta="往上滑 立即領券"),
}
SIZE = {"out": (2100, 900), "in": (2100, 900), "square": (1080, 1080), "story": (1080, 1920)}
HERO_BOX = {"out": (780, 0, 1320, 900), "in": (780, 0, 1320, 900), "square": (0, 0, 1080, 620), "story": (0, 0, 1080, 980)}

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:%(W)dpx;height:%(H)dpx;overflow:hidden;font-family:'Noto Sans TC','PingFang TC','Hiragino Sans',sans-serif;background:%(bodybg)s;position:relative}
.hero{position:absolute;left:%(hx)dpx;top:%(hy)dpx;width:%(hw)dpx;height:%(hh)dpx;background:url('%(heroimg)s') center/cover;}
.chip{display:inline-flex;align-items:center;gap:18px;background:#fff;border-radius:999px;padding:14px 28px;box-shadow:0 8px 24px rgba(0,0,0,.12)}
.chip img{display:block}
.x{color:#B9B0B2;font-size:26px;font-weight:300}
"""

def page(name, b, mode):
    W, H = SIZE[b["kind"]]
    hx, hy, hw, hh = HERO_BOX[b["kind"]]
    hero = A + "heroes/" + b["hero"] + ".jpg"
    lion, dept, lt = A + "brand/lion.png", A + "brand/" + b["dept"] + ".png", A + "brand/liontrip.png"
    mark = A + "brand/lion-mark-white.png"
    accent = b.get("accent", "#FFFFFF")
    jp = b["kind"] in ("in", "square")
    bodybg = "transparent" if mode == "ov" else "#fff"
    css = CSS % dict(W=W, H=H, hx=hx, hy=hy, hw=hw, hh=hh, heroimg=hero if mode == "full" else "", bodybg=bodybg)
    heroDiv = '<div class="hero"></div>' if mode == "full" else ""
    if b["kind"] == "out":
        dh = 34 if b["dept"] == "hhd-short" else 44
        body = f"""
<style>
.panel{{position:absolute;left:0;top:0;width:900px;height:900px;background:linear-gradient(150deg,#F5414B 0%,#E8303A 55%,#D1202B 100%);clip-path:polygon(0 0,100% 0,86% 100%,0 100%)}}
.mark{{position:absolute;left:470px;top:430px;width:520px;opacity:.10}}
.edge{{position:absolute;left:0;top:0;width:900px;height:900px;clip-path:polygon(100% 0,100.6% 0,86.6% 100%,86% 100%);background:#fff}}
.txt{{position:absolute;left:84px;top:78px;width:700px;color:#fff}}
.eb{{display:inline-block;margin-top:58px;font-size:32px;font-weight:700;color:{'#E8303A' if accent=='#FFFFFF' else '#1A1A1A'};background:{accent};padding:6px 20px;border-radius:8px}}
h1{{font-size:{92 if len(b['h'])<16 else 80}px;line-height:1.16;font-weight:900;margin-top:24px;letter-spacing:.01em;text-shadow:0 4px 18px rgba(120,0,10,.25)}}
.sub{{font-size:34px;font-weight:700;margin-top:26px;opacity:.96}}
.cta{{display:inline-flex;align-items:center;gap:14px;margin-top:40px;background:#fff;color:#E8303A;font-size:36px;font-weight:900;padding:18px 40px;border-radius:999px;box-shadow:0 10px 26px rgba(120,0,10,.25)}}
.cta i{{font-style:normal;font-size:30px}}
.tsp{{position:absolute;left:84px;bottom:42px;color:rgba(255,255,255,.75);font-size:20px;letter-spacing:.08em}}
</style>
{heroDiv}<div class="panel"></div><img class="mark" src="{mark}"><div class="edge"></div>
<div class="txt"><div class="chip"><img src="{lion}" style="height:52px"><span class="x">×</span><img src="{dept}" style="height:{dh}px"></div><br>
<div class="eb">{b['eyebrow']}</div><h1>{b['h']}</h1><div class="sub">{b['sub']}</div><div class="cta">{b['cta']}<i>›</i></div></div>
<div class="tsp">T-SPACE by TURNCLOUD｜雄獅旅遊 App 日本百貨優惠專區</div>"""
    elif b["kind"] == "in":
        body = f"""
<style>
.panel{{position:absolute;left:0;top:0;width:900px;height:900px;background:#FFFDFB;clip-path:polygon(0 0,100% 0,86% 100%,0 100%)}}
.bar{{position:absolute;left:0;top:0;width:14px;height:900px;background:#C8102E}}
.edge{{position:absolute;left:0;top:0;width:900px;height:900px;clip-path:polygon(100% 0,101.2% 0,87.2% 100%,86% 100%);background:#C8102E}}
.txt{{position:absolute;left:96px;top:84px;width:700px;color:#1E1A1D;font-family:'Hiragino Sans','Noto Sans TC',sans-serif}}
.eb{{display:inline-block;margin-top:60px;font-size:30px;font-weight:700;color:#fff;background:#C8102E;padding:6px 20px}}
h1{{font-family:'Hiragino Mincho ProN',serif;font-size:96px;line-height:1.2;font-weight:600;margin-top:26px}}
.sub{{font-size:32px;font-weight:600;margin-top:24px;color:#3A3335}}
.cta{{display:inline-flex;gap:14px;margin-top:40px;background:#FF3568;color:#fff;font-size:34px;font-weight:700;padding:18px 40px;border-radius:999px}}
</style>
{heroDiv}<div class="panel"></div><div class="bar"></div><div class="edge"></div>
<div class="txt"><div class="chip" style="box-shadow:0 6px 20px rgba(0,0,0,.08);border:1px solid #EEE"><img src="{dept}" style="height:34px"><span class="x">×</span><img src="{lt}" style="height:44px"></div><br>
<div class="eb">{b['eyebrow']}</div><h1>{b['h']}</h1><div class="sub">{b['sub']}</div><div class="cta">{b['cta']} ›</div></div>"""
    elif b["kind"] == "square":
        body = f"""
<style>
.panel{{position:absolute;left:0;top:620px;width:1080px;height:460px;background:#FFFDFB}}
.rule{{position:absolute;left:0;top:614px;width:1080px;height:8px;background:#C8102E}}
.txt{{position:absolute;left:0;top:650px;width:1080px;text-align:center;font-family:'Hiragino Sans',sans-serif;color:#1E1A1D}}
.eb{{font-size:26px;color:#6B6265;margin-top:26px}}
h1{{font-family:'Hiragino Mincho ProN',serif;font-size:72px;font-weight:600;margin-top:10px}}
.sub{{font-size:28px;margin-top:12px}}
.cta{{display:inline-block;margin-top:22px;background:#9E0E26;color:#fff;font-size:28px;padding:12px 60px}}
.top{{position:absolute;left:40px;top:36px}}
</style>
{heroDiv}<div class="panel"></div><div class="rule"></div>
<div class="top"><div class="chip"><img src="{dept}" style="height:30px"><span class="x">×</span><img src="{lt}" style="height:40px"></div></div>
<div class="txt"><div class="eb">{b['eyebrow']}</div><h1>{b['h']}</h1><div class="sub">{b['sub']}</div><div class="cta">{b['cta']}</div></div>"""
    else:  # story
        body = f"""
<style>
.panel{{position:absolute;left:0;top:930px;width:1080px;height:990px;background:linear-gradient(160deg,#F5414B,#E8303A 50%,#FF6A2B);clip-path:polygon(0 50px,100% 0,100% 100%,0 100%)}}
.mark{{position:absolute;left:560px;top:1250px;width:620px;opacity:.12}}
.top{{position:absolute;left:0;top:60px;width:1080px;text-align:center}}
.card{{position:absolute;left:150px;top:1040px;width:780px;height:330px;background:linear-gradient(135deg,#17284F,#0A1F44);border-radius:28px;transform:rotate(-4deg);box-shadow:0 26px 50px rgba(60,0,0,.35);text-align:center;color:#F2C879;padding-top:36px}}
.card .s{{font-size:34px;font-weight:700}} .card .b{{font-size:120px;font-weight:900;line-height:1.05;font-family:'Noto Serif TC','Hiragino Mincho ProN',serif}} .card .c{{font-size:58px;font-weight:900}}
.txt{{position:absolute;left:0;top:1430px;width:1080px;text-align:center;color:#fff}}
h1{{font-size:92px;font-weight:900;line-height:1.2}}
.sub{{font-size:34px;font-weight:700;margin-top:18px}}
.cta{{display:inline-block;margin-top:44px;background:#fff;color:#E8303A;font-size:38px;font-weight:900;padding:22px 56px;border-radius:999px}}
</style>
{heroDiv}<div class="panel"></div><img class="mark" src="{mark}">
<div class="top"><div class="chip"><img src="{lion}" style="height:50px"><span class="x">×</span><img src="{dept}" style="height:32px"></div></div>
<div class="card"><div class="s">{b['eyebrow']}</div><div class="b">95<span style="font-size:70px">折</span></div><div class="c">＋免稅</div></div>
<div class="txt"><h1>{b['h'].replace('<br>','')}</h1><div class="sub">{b['sub']}</div><div class="cta">{b['cta']}</div></div>"""
    return W, H, f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{body}</body></html>"


def render(name, mode, out):
    W, H, html = page(name, BANNERS[name], mode)
    tmp = os.path.join(ROOT, "banner_tpl", f"_{name}_{mode}.html")
    open(tmp, "w").write(html)
    args = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
            f"--force-device-scale-factor={2 if mode == 'full' else 1}", "--virtual-time-budget=1500", f"--screenshot={out}", "file://" + tmp]
    if mode == "ov":
        args.insert(4, "--default-background-color=00000000")
    subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    os.remove(tmp)


if __name__ == "__main__":
    names = sys.argv[1:] or list(BANNERS)
    os.makedirs(os.path.join(ROOT, "assets/img/banners_v2"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "assets/video/brand2"), exist_ok=True)
    for n in names:
        render(n, "full", os.path.join(ROOT, "assets/img/banners_v2", n + ".png"))
        render(n, "ov", os.path.join(ROOT, "assets/video/brand2", n + "-ov.png"))
        print("ok", n)
    json.dump({k: dict(kind=v["kind"], hero=v["hero"], box=HERO_BOX[v["kind"]], size=SIZE[v["kind"]]) for k, v in BANNERS.items()},
              open(os.path.join(ROOT, "banner_tpl/layout.json"), "w"))
