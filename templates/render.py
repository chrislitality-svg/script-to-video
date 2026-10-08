# -*- coding: utf-8 -*-
"""分段编码 → 逐段末帧校验 → concat → 音画合成
    python templates/render.py [project_dir] [--music audio/mix/mix_master.wav]
成片：<project>/out/video_v1.mp4"""
import json, pathlib, re, subprocess, sys
import numpy as np
from PIL import Image

args = sys.argv[1:]
music, proj, i = None, ".", 0
while i < len(args):
    if args[i] == "--music":
        music = args[i + 1]; i += 2
    else:
        proj = args[i]; i += 1
ROOT = pathlib.Path(proj).resolve()
OUT = ROOT / "out"
FPS = 30
TL = json.load(open(ROOT / "shots/timeline.json", encoding="utf8"))
N = int(TL["dur"] * FPS)
# 自动检测截图分段（任意分法都行）
import re
SEGS = []
for d in sorted(OUT.glob("frames_*")):
    nums = sorted(int(m.group(1)) for f in d.iterdir() if (m := re.fullmatch(r"(\d{6})\.jpg", f.name)))
    if nums:
        SEGS.append((d.name.replace("frames_", ""), nums[0], nums[-1] + 1))
SEGS.sort(key=lambda s: s[1])
assert sum(f1 - f0 for _, f0, f1 in SEGS) == N, f"帧数 {sum(f1-f0 for _,f0,f1 in SEGS)} != 时长帧数 {N}，先截完整"
print("分段:", SEGS)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:]); sys.exit(1)

for seg, f0, f1 in SEGS:
    run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-start_number", str(f0),
         "-i", str(OUT / f"frames_{seg}/%06d.jpg"),
         "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-vf", "scale=1080:1440:flags=lanczos", str(OUT / f"seg_{seg}.mp4")])
    print(f"seg_{seg}.mp4 {f1-f0} 帧")

def rms(a, b):
    return float(np.sqrt(np.mean((np.asarray(a, np.float64) - np.asarray(b, np.float64)) ** 2)))

for seg, f0, f1 in SEGS:  # 逐段末帧健康校验：抓无报错坏段
    src = Image.open(OUT / f"frames_{seg}/{f1-1:06d}.jpg").convert("RGB").resize((540, 720))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(OUT / f"seg_{seg}.mp4"),
                    "-vf", "select=eq(n\\," + str(f1 - f0 - 1) + ")", "-vframes", "1", str(OUT / "_last.png")], check=True)
    enc = Image.open(OUT / "_last.png").convert("RGB").resize((540, 720))
    r = rms(src, enc)
    print(f"seg_{seg} 末帧 RMS {r:.2f}", "OK" if r < 8 else "** BAD → 重编 **")
    if r >= 8:
        run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-start_number", str(f0),
             "-i", str(OUT / f"frames_{seg}/%06d.jpg"),
             "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p",
             "-vf", "scale=1080:1440:flags=lanczos", str(OUT / f"seg_{seg}.mp4")])

(OUT / "concat.txt").write_text("".join(f"file 'seg_{s}.mp4'\n" for s, _, _ in SEGS), encoding="utf8")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(OUT / "concat.txt"),
     "-c", "copy", str(OUT / "_video_only.mp4")])

cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(OUT / "_video_only.mp4")]
if music:
    cmd += ["-i", str(ROOT / music), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
            "-af", "volume=0.9,pan=stereo|c0=c0|c1=c0", "-c:a", "aac", "-b:a", "192k", "-shortest"]
else:
    cmd += ["-c", "copy"]
cmd += ["-movflags", "+faststart", str(OUT / "video_v1.mp4")]
run(cmd)
print("video_v1.mp4 完成")
