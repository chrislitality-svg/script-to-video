# -*- coding: utf-8 -*-
"""程序合成轻快配乐（零版权风险）：C 大调琶音 + pad + 鼓组
    python templates/music.py [project_dir]  → audio/music/bright.wav (~140s)
情绪不对就改 BPM / progression / 音色参数——这正是程序合成的意义。"""
import pathlib, sys
import numpy as np
import soundfile as sf

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SR, BPM = 48000, 108
BEAT = 60 / BPM; BAR = BEAT * 4
rng = np.random.default_rng(2026)
NOTE = lambda n: 440 * 2 ** ((n - 69) / 12)

def ks(f0, dur, amp=.5, damp=.996):  # Karplus-Strong 拨弦
    n = int(dur * SR); p = max(2, int(SR / f0))
    buf = rng.uniform(-1, 1, p); out = np.empty(n)
    for i in range(n):
        j = i % p; buf[j] = damp * .5 * (buf[j] + buf[(j + 1) % p]); out[i] = buf[j]
    return out * np.exp(-np.arange(n) / SR * 2.2) * np.minimum(1, np.arange(n) / (SR * .002)) * amp

def sine(f0, dur, amp=.3, a=.02, r=.3):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f0 * t) * np.minimum(1, t / a) * np.minimum(1, (dur - t) / r) * amp

def kick(amp=.5):
    n = int(.16 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(120 * np.exp(-t * 22) + 42) / SR) * np.exp(-t * 16) * amp

def hat(amp=.16):
    n = int(.05 * SR); x = np.diff(rng.uniform(-1, 1, n), prepend=0) * .5
    return x * np.exp(-np.arange(n) / SR * 90) * amp

def clap(amp=.3):
    n = int(.12 * SR); x = np.zeros(n)
    for k, off in enumerate((0, .011, .023)):
        i = int(off * SR); burst = rng.uniform(-1, 1, n - i) * np.exp(-np.arange(n - i) / SR * (60 + k * 30)); x[i:] += burst
    band = np.convolve(np.diff(x, prepend=0), np.ones(6) / 6, "same")
    return band / (np.abs(band).max() + 1e-9) * amp

CH = {"C": (60, 64, 67), "G": (55, 59, 62), "Am": (57, 60, 64), "F": (53, 57, 60)}
BASS = {"C": 36, "G": 31, "Am": 33, "F": 29}
prog = (["C", "G", "Am", "F"] * 8 + ["F", "G", "C", "Am"] * 6 + ["C", "G", "Am", "F"] * 8 + ["C"])
TOTAL = len(prog) * BAR + 5
mus = np.zeros(int(TOTAL * SR))
place = lambda x, t: mus.__setitem__(slice(int(t * SR), int(t * SR) + len(x)),
                                     mus[int(t * SR):int(t * SR) + len(x)] + x[:max(0, min(len(x), len(mus) - int(t * SR)))])

PENTA = [72, 74, 76, 79, 81, 84, 86, 88]
for b, ch in enumerate(prog):
    t0 = 1.0 + b * BAR; root = CH[ch]
    for nn in root: place(sine(NOTE(nn - 12), BAR * 1.05, .045, a=.4, r=.9), t0)
    for bt in (0, 2): place(sine(NOTE(BASS[ch]), BEAT * 1.6, .22, a=.008, r=.25), t0 + bt * BEAT)
    for bt in range(4):
        ts = t0 + bt * BEAT
        place(kick(.5), ts) if bt % 2 == 0 else place(clap(.3), ts)
        for et in range(2): place(hat(.13 if et else .19), ts + et * BEAT / 2)
    arp = [root[0], root[1], root[2], root[1] + 12, root[2], root[1], root[0] + 12, root[1] + 12]
    for et in range(8):
        if et in (3, 6): continue
        place(ks(NOTE(arp[et] - 12), .5, .16, .997), t0 + et * BEAT / 2)
        if rng.random() >= .3:
            note = PENTA[int((b * 3 + et * 5 + rng.integers(0, 4)) % 8)]
            place(ks(NOTE(note), .55, .3, .9975), t0 + et * BEAT / 2)

d1, d2 = int(.087 * SR), int(.131 * SR)  # 轻混响
rev = np.zeros_like(mus)
for dd in (d1, d2): rev[dd:] += mus[:-dd] * .18
mus = (mus + rev * .5) / (np.abs(mus).max() * 1.16 + 1e-9)
n = len(mus)
mus[:int(1.2 * SR)] *= np.linspace(0, 1, int(1.2 * SR))
mus[-int(2.5 * SR):] *= np.linspace(1, 0, int(2.5 * SR))
out = ROOT / "audio/music"; out.mkdir(parents=True, exist_ok=True)
sf.write(out / "bright.wav", mus.astype(np.float32), SR, subtype="PCM_16")
print(f"bright.wav {n / SR:.1f}s  BPM {BPM}")
