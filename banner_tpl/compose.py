"""把乾淨主視覺影片放進版型的主視覺框，再疊上透明品牌層，輸出動態 Banner。"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(ROOT, "banner_tpl/layout.json")))
VID = {"b2-clay": "bn-clay", "b3-taxrefund": "bn-tax", "b4-b1map": "bn-b1map", "b6-ticket": "bn-ticket",
       "b5-tigers": "bn-tigers", "b7-sakura": "bn-sakura", "b8-jp-clay": "bn-jp", "b10-jp-square": "bn-square",
       "b9-story": "bn-story"}
for name in (sys.argv[1:] or VID):
    l = L[name]; W, H = l["size"]; x, y, w, h = l["box"]
    src = os.path.join(ROOT, "assets/video/hero", l["hero"] + ".mp4")
    ov = os.path.join(ROOT, "assets/video/brand2", name + "-ov.png")
    out = os.path.join(ROOT, "assets/video/brand2", VID[name] + ".mp4")
    s = 1.0  # 全尺寸輸出
    fc = (f"color=white:s={W}x{H}:d=5[bg];"
          f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},unsharp=5:5:0.6[hv];"
          f"[bg][hv]overlay={x}:{y}[b1];[b1][1:v]overlay=0:0,scale={int(W*s)//2*2}:{int(H*s)//2*2}")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", ov, "-filter_complex", fc, "-t", "5",
                    "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", out], check=True)
    print("ok", out)
