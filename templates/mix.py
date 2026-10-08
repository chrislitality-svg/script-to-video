# -*- coding: utf-8 -*-
"""混音：VO + 配乐(ducking) + 音效(重音) → audio/mix/mix_v1.wav → loudnorm 母带
    python templates/mix.py [project_dir]
音效在 shots/timeline.json 的每场景 "fx" 里声明：
  {"type":"thud","at":1.2,"f":80,"amp":0.5}  （at=场景局部秒）
音效是标点不是背景：每场景 ≤2 个。"""
import json, math, pathlib, subprocess, sys
import numpy as np
import soundfile as sf

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SR = 48000
TL = json.load(open(ROOT / "shots/timeline.json", encoding="utf8"))
SC = {s["id"]: s for s in TL["shots"]}
DUR, N = TL["dur"], int(TL["dur"] * SR)
rng = np.random.default_rng(2026)
N_MUSIC = (ROOT / "audio/music/bright.wav").exists()

def load(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True).stdout
    x = np.frombuffer(p, dtype=np.float32).astype(np.float64)
    assert len(x) > 0, f"空音频：{path}"
    return x

def place(buf, x, t):
    i = int(t * SR)
    if i >= N or i + len(x) <= 0: return
    a, b = max(0, -i), min(len(x), N - i)
    buf[i + a:i + b] += x[a:b]

def env_fade(x, fin, fout):
    if fin > 0: n = int(fin * SR); x[:n] *= np.linspace(0, 1, n)
    if fout > 0: n = int(fout * SR); x[-n:] *= np.linspace(1, 0, n)
    return x

def s_thud(f0=80, amp=.5):
    t = np.arange(int(.45 * SR)) / SR
    return (np.sin(2 * np.pi * (f0 * np.exp(-t * 6)) * t) * np.exp(-t * 9) + (rng.random(len(t)) - .5) * np.exp(-t * 60) * .4) * amp

vo, mus, sfx = np.zeros(N), np.zeros(N), np.zeros(N)

for sid, s in SC.items():
    for j, v in enumerate(s.get("vo", [])):
        f = ROOT / f"audio/vo/takes/{sid}_t{j+1}.wav"
        if not f.exists():
            print(f"  [warn] {sid} 无配音，跳过"); continue
        w = load(f"audio/vo/takes/{sid}_t{j+1}.wav")
        w = w / (np.sqrt(np.mean(w ** 2)) + 1e-9) * 10 ** (-16.5 / 20)
        place(vo, w, s["start"] + v["at"])

if N_MUSIC:
    x = load("audio/music/bright.wav")[:N]
    if len(x) < N: x = np.pad(x, (0, N - len(x)))
    x = env_fade(x.copy(), 1.2, 2.8)
    mus += x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * 10 ** (-23.0 / 20)
    sm = np.convolve(np.abs(vo), np.ones(int(.35 * SR)) / int(.35 * SR), "same")
    mus *= 1 - 0.60 * np.clip(sm * 6, 0, 1)  # ducking

for sid, s in SC.items():
    for fx in s.get("fx", []):
        if fx["type"] == "thud":
            place(sfx, s_thud(fx.get("f", 80), fx.get("amp", .5)), s["start"] + fx["at"])

mix = vo + mus + sfx
CEIL = 0.7079  # -3dBFS 峰值包络限幅
need = np.minimum(1.0, CEIL / np.maximum(np.abs(mix), 1e-9))
rel = np.exp(-1 / (0.060 * SR))
g = np.empty_like(need); cur = 1.0
for i in range(len(need)):
    cur = need[i] if need[i] < cur else cur * rel + need[i] * (1 - rel)
    g[i] = cur
mix *= np.minimum(np.convolve(g, np.ones(24) / 24, "same"), need)
out = ROOT / "audio/mix"; out.mkdir(parents=True, exist_ok=True)
sf.write(out / "mix_v1.wav", mix, SR, subtype="PCM_24")
print(f"mix_v1.wav {DUR:.1f}s 峰值 {20 * math.log10(np.max(np.abs(mix)) + 1e-9):.2f} dBFS")

# loudnorm 两遍 → -14 LUFS / TP -1.5
probe = subprocess.run(["ffmpeg", "-v", "info", "-i", str(out / "mix_v1.wav"),
                        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "mix_v1.wav"),
                "-af", ("loudnorm=I=-14:TP=-1.5:LRA=11:"
                        f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                        f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                        f"offset={m['target_offset']}"), "-ar", "48000", str(out / "mix_master.wav")], check=True)
print("mix_master.wav -14 LUFS 完成")
