"""把雄獅／LionTrip／阪急阪神百貨的正式 logo 做成聯名品牌條，套到靜態 Banner 與動態影片。

去程（雄獅台灣版 App）：底部白色品牌條＝雄獅旅遊 × 百貨 logo ＋ 紅色「雄獅會員限定」膠囊
回程（日本側）：底部白色品牌條＝阪急阪神百貨店 × LionTrip ＋ 粉紅「百貨店会員さま限定」膠囊
限動 9:16：頂部白色聯名膠囊（下方已有 CTA 按鈕，不加底條）
"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(ROOT, "assets/img/logos")
SRC = os.path.join(ROOT, "assets/img/banners")
OUT = os.path.join(ROOT, "assets/img/banners_brand")
VSRC = os.path.join(ROOT, "assets/video")
VOUT = os.path.join(ROOT, "assets/video/brand")
F_TC = os.path.expanduser("~/Library/Fonts/NotoSansTC-Bold.otf")
F_JP = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
RED, LT_PINK, DEPT_RED = (240, 55, 66), (255, 53, 104), (200, 16, 46)

# 名稱: (方向, 百貨 logo, 膠囊文字)
SPEC = {
    "b2-clay":      ("out", "hhd-short", "雄獅會員限定｜日本百貨優惠專區"),
    "b3-taxrefund": ("out", "hhd-short", "雄獅會員限定｜日本百貨優惠專區"),
    "b4-b1map":     ("out", "hankyu-honten", "雄獅會員限定｜阪急 B1 甜點地圖"),
    "b5-tigers":    ("out", "hhd-short", "雄獅 × 阪神梅田本店｜虎迷限定"),
    "b6-ticket":    ("out", "hhd-short", "雄獅會員限定｜行程附贈百貨券"),
    "b7-sakura":    ("out", "hhd-short", "雄獅會員限定｜春假百貨禮遇"),
    "b8-jp-clay":   ("in", "hhd-short", "百貨店会員さま限定"),
    "b10-jp-square": ("in", "hhd-short", "百貨店会員さま限定"),
    "b9-story":     ("chip", "hhd-short", ""),
}
VIDEO = {"bn-clay": "b2-clay", "bn-tax": "b3-taxrefund", "bn-b1map": "b4-b1map", "bn-tigers": "b5-tigers",
         "bn-ticket": "b6-ticket", "bn-sakura": "b7-sakura", "bn-jp": "b8-jp-clay",
         "bn-square": "b10-jp-square", "bn-story": "b9-story"}


def logo(name, h):
    im = Image.open(os.path.join(LOGO, name + ".png")).convert("RGBA")
    return im.resize((max(1, int(im.width * h / im.height)), h), Image.LANCZOS)


def times(draw, cx, cy, s, color=(170, 160, 162)):
    w = max(2, s // 7)
    draw.line([(cx - s, cy - s), (cx + s, cy + s)], fill=color, width=w)
    draw.line([(cx - s, cy + s), (cx + s, cy - s)], fill=color, width=w)


def lockup(direction, dept, h):
    """回傳一張透明底的聯名 logo 組（雄獅在前或百貨在前）。"""
    if direction == "out":
        a, b = logo("lion", int(h * 1.0)), logo(dept, int(h * (0.62 if dept == "hhd-short" else 0.8)))
    else:
        a, b = logo(dept, int(h * 0.62)), logo("liontrip", int(h * 0.82))
    gap = int(h * 0.55)
    W = a.width + b.width + gap * 2
    im = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    im.alpha_composite(a, (0, (h - a.height) // 2))
    im.alpha_composite(b, (a.width + gap * 2, (h - b.height) // 2))
    times(ImageDraw.Draw(im), a.width + gap, h // 2, int(h * 0.16))
    return im


def bar(width, direction, dept, text, square=False):
    bh = max(80, int(width * (0.11 if square else 0.075)))
    im = Image.new("RGBA", (width, bh), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    accent = RED if direction == "out" else DEPT_RED
    d.rectangle([0, 0, width, max(3, bh // 22)], fill=accent)
    pad = int(bh * 0.42)
    lk = lockup(direction, dept, int(bh * 0.52))
    im.alpha_composite(lk, (pad, (bh - lk.height) // 2 + bh // 40))
    if text:
        font = ImageFont.truetype(F_TC if direction == "out" else F_JP, int(bh * 0.27))
        tw = d.textlength(text, font=font)
        ph = int(bh * 0.56)
        pw = int(tw + ph * 0.9)
        x1 = width - pad
        x0 = x1 - pw
        y0 = (bh - ph) // 2 + bh // 40
        pill = RED if direction == "out" else LT_PINK
        d.rounded_rectangle([x0, y0, x1, y0 + ph], radius=ph // 2, fill=pill)
        d.text((x0 + (pw - tw) / 2, y0 + ph / 2), text, font=font, fill="white", anchor="lm")
    return im


def chip(width, dept):
    h = int(width * 0.1)
    lk = lockup("out", dept, int(h * 0.58))
    pw = lk.width + int(h * 0.9)
    im = Image.new("RGBA", (pw, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, pw - 1, h - 1], radius=h // 2, fill=(255, 255, 255, 240))
    im.alpha_composite(lk, ((pw - lk.width) // 2, (h - lk.height) // 2))
    return im


def brand_image(name):
    direction, dept, text = SPEC[name]
    src = Image.open(os.path.join(SRC, name + ".jpg")).convert("RGBA")
    if direction == "chip":
        c = chip(src.width, dept)
        src.alpha_composite(c, ((src.width - c.width) // 2, int(src.width * 0.05)))
        out = src
    else:
        b = bar(src.width, direction, dept, text, square=src.height > src.width * 0.7)
        out = Image.new("RGBA", (src.width, src.height + b.height), "white")
        out.alpha_composite(src, (0, 0))
        out.alpha_composite(b, (0, src.height))
    out.convert("RGB").save(os.path.join(OUT, name + ".jpg"), quality=90)
    return out.size


def brand_video(vname):
    name = VIDEO[vname]
    direction, dept, text = SPEC[name]
    src = os.path.join(VSRC, vname + ".mp4")
    w, h = map(int, subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "csv=p=0", src]).decode().strip().split(","))
    ov = os.path.join(VOUT, vname + "-ov.png")
    if direction == "chip":
        c = chip(w, dept)
        c.save(ov)
        fc = f"[0:v][1:v]overlay=(W-w)/2:{int(w * 0.05)}"
    else:
        b = bar(w, direction, dept, text, square=h > w * 0.7)
        bh = b.height + (b.height % 2)
        b.save(ov)
        fc = f"[0:v]pad=iw:ih+{bh}:0:0:white[p];[p][1:v]overlay=0:{h}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", ov, "-filter_complex", fc,
                    "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p", "-an",
                    "-movflags", "+faststart", os.path.join(VOUT, vname + ".mp4")], check=True)
    os.remove(ov)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(VOUT, exist_ok=True)
    for n in SPEC:
        print(n, brand_image(n))
    for v in VIDEO:
        brand_video(v)
        print("video", v)
