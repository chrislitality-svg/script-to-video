# 声音管线

三层：配音（信息）→ 配乐（情绪）→ 音效（标点）。终值 -14 LUFS / TP -1.5。

## 一、配音

| 方案 | 成本 | 质量 | 何时用 |
|---|---|---|---|
| edge-tts（默认） | 免费在线 | 良好，音色多 | 默认；Yunxi 年轻男声/Yunjian 浑厚 |
| Qwen3-TTS 音色克隆 | 本地 GPU（6GB 可跑 1.7B fp16） | 优，可克隆参考音色 | 需要特定音色/系列片声音一致 |
| ChatTTS / IndexTTS | 本地 | 良好 | 备选 |

纪律：
- 年份逐字转写（2022→二零二二）、小数点转"点"、引号剔除——写进 tts_text()。
- 必须重试 + 断点续跑（在线 TTS 偶发空响应）。
- 每句一个 wav，实测时长写 json——**配音时长就是时间轴的源头**。
- 音色选定后全片固定 seed，可复现。

## 二、配乐

- 默认 `templates/music.py` 程序合成：C 大调 C-G-Am-F，Karplus-Strong 拨弦琶音 +
  正弦 pad + 合成鼓组，BPM 108。**程序合成的意义：情绪可精确控制 + 零版权风险**。
- 用外部音乐时：确认授权；波形图选段（`ffmpeg showwavespic` 看structure，取主段）；
  截段 + 淡入淡出 + RMS 归一到 -23dB 左右（母带过的曲目响，压低才不抢人声）。

## 三、混音公式（templates/mix.py）

```
VO:   每 wav 按 RMS 归一到 -16.5 dB，放于 场景start+0.25
MUSIC: RMS 归一到 -23 dB，fade in 1.2s / out 2.8s
DUCK:  人声包络（0.35s 滑窗）附近音乐 -60%（≈-8dB）
SFX:   thud = sin(2π·f·exp(-6t)·t)·exp(-9t)；whoosh 带通噪声；tick 指数衰减噪声
       ——每场景 ≤2 个，只配砸落/盖章
LIMIT: 峰值包络限幅 attack 即时 / release 60ms / 天花板 -3dBFS
       （ffmpeg alimiter 行为异常，自写更可控）
MASTER: loudnorm 两遍 I=-14 TP=-1.5 LRA=11，第二遍带 measured 参数
```

ffmpeg 陷阱：
- 单声道→立体声用 `pan=stereo|c0=c0|c1=c0` 显式复制（`-ac 2` 会做 -3dB 能量补偿）；
- 合成末尾 `volume=0.9` 防 AAC 过冲，TP 留 -1dB 余量。

## 四、质检

- loudnorm summary：I 达标 ±0.5、TP ≤-1.5；
- volumedetect：mean ≈ -15dB、max ≤ -1.3dB；
- 无静音轨（音轨存在且 mean > -40dB）。
