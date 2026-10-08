# -*- coding: utf-8 -*-
"""成品七项校验：python templates/check.py [project_dir]
全 PASS 才交付。任何 FAIL 都要先修片子再改阈值。"""
import json, pathlib, subprocess, sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
V = ROOT / "out/video_v1.mp4"
TL = json.load(open(ROOT / "shots/timeline.json", encoding="utf8"))
DUR = TL["dur"]
ok = True

def sh_err(cmd): return subprocess.run(cmd, capture_output=True, text=True).stderr
def frame_at(t, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(V), "-vframes", "1", str(dst)], check=True)
    return np.asarray(Image.open(dst).convert("RGB"), dtype=np.float64)

# 1) 无缝循环：首帧 vs 末帧
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(V), "-vf", "select=eq(n\\,0)", "-vframes", "1", str(ROOT / "out/_c1.png")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", str(V), "-vframes", "1", str(ROOT / "out/_c2.png")], check=True)
a = np.asarray(Image.open(ROOT / "out/_c1.png").convert("RGB").resize((270, 360)), np.float64)
b = np.asarray(Image.open(ROOT / "out/_c2.png").convert("RGB").resize((270, 360)), np.float64)
r = float(np.sqrt(np.mean((a - b) ** 2)))
print(f"1) 循环首末帧 RMS {r:.2f}  {'PASS' if r < 5 else 'FAIL'}"); ok &= r < 5

# 2) 音轨
p = sh_err(["ffmpeg", "-i", str(V), "-af", "volumedetect", "-f", "null", "-"])
mv = [l for l in p.splitlines() if "mean_volume" in l]
print(f"2) 音轨 {mv[0].split(': ')[-1] if mv else 'N/A'}  {'PASS' if mv else 'FAIL'}"); ok &= bool(mv)

# 3) 字幕可见性：抽 cue 中点，底部带亮像素
CUES = []
import re
html = (ROOT / "tools/web/anim.html").read_text(encoding="utf8")
for s, e, zh in re.findall(r'\{"s":([\d.]+),"e":([\d.]+),"zh":"(.*?)"\}', re.search(r'let CUES=\[(.*?)\];', html, re.S).group(1)):
    CUES.append((float(s) + float(e)) / 2)
for i, t in enumerate(CUES[::max(1, len(CUES) // 8)][:8]):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(V), "-vframes", "1", str(ROOT / "out/_c3.png")], check=True)
    im = np.asarray(Image.open(ROOT / "out/_c3.png").convert("L"), dtype=np.float64)
    band = im[1300:1420, 200:880]
    ratio = float((band > 140).mean())
    st = ratio >= 0.008  # 短句药丸小，阈值放宽
    print(f"3) 字幕@{t:.1f}s 亮像素 {ratio*100:.1f}%  {'PASS' if st else 'FAIL'}"); ok &= st

# 4) 风格色序：均匀 24 帧 B>G>R
bad = 0
for i in range(24):
    im = frame_at(i * DUR / 24 + .2, ROOT / "out/_c4.png").reshape(-1, 3)
    m = im.mean(axis=0)
    if not (m[2] > m[1] > m[0]): bad += 1
print(f"4) 蓝图色序 跑色 {bad}/24  {'PASS' if bad == 0 else 'FAIL'}"); ok &= bad == 0

# 5) 空白帧
zero = 0
for i in range(8):
    im = frame_at(2 + i * (DUR - 4) / 7, ROOT / "out/_c5.png")
    if im.std() < 1.0: zero += 1
print(f"5) 空白帧 {zero}/8  {'PASS' if zero == 0 else 'FAIL'}"); ok &= zero == 0

# 6) 体积/时长/分辨率
info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                  "format=duration,size:stream=width,height", "-of", "json", str(V)],
                                 capture_output=True, text=True).stdout)
dur, size = float(info["format"]["duration"]), int(info["format"]["size"])
wh = info["streams"][0]["width"], info["streams"][0]["height"]
st = size <= 500 * 1024 * 1024 and abs(dur - DUR) < 1.0
print(f"6) {wh[0]}x{wh[1]} {dur:.2f}s {size/1048576:.1f}MB  {'PASS' if st else 'FAIL'}"); ok &= st

# 7) faststart
head = open(V, "rb").read(4096)
moov, mdat = head.find(b"moov"), head.find(b"mdat")
st = moov != -1 and (mdat == -1 or moov < mdat)
print(f"7) faststart  {'PASS' if st else 'FAIL'}"); ok &= st

print("\n总体:", "ALL PASS" if ok else "存在问题")
