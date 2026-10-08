---
name: script-to-video
description: >
  把任何一份文稿（工程纪实、报告、论文、说明书、科普资料）变成一条 3:4 竖版
  科普/宣传短视频（1080×1440，60–150 秒）。纯代码渲染：单文件 HTML 确定性时间轴
  → Playwright 逐帧截图 → ffmpeg 编码合成。无需剪辑软件、无需 AI 视频生成 API、
  全程本地零成本、逐帧可复现。适用于：已有文稿要做视频；数据叙事/知识科普短视频；
  需要批量、可审计、可复现的视频生产；模型（任何编程能力强的 LLM）直接执行生产。
---

# script-to-video · 文稿 → 竖版科普短视频

三条总纲，所有决策回到它们：

1. **确定性时间轴**：动画是纯函数 `setTime(t)`——同一时刻永远渲染同一画面。这带来
   任意跳帧审计、多进程分段截图、循环可证明、改一个常量全片变速。
2. **配音实测时长驱动时间轴**：先配音、量出每句时长，再排场景边界——音画天然同步，
   不需要 ASR 对齐。
3. **用户的眼睛不该是第一道质检**：程序化审计（越界/重叠）归零是截图的前置条件，
   关键帧目检是美观的最后一道门。

## 流程（九步，任何一步不过关就退回上游）

```
文稿 ─▶ ① 数据宪法 ─▶ ② 文案+字幕分块 ─▶ ③ 配音（实测时长）
     ─▶ ④ 时间轴 sync ─▶ ⑤ 动画 anim.html ─▶ ⑥ 双审计归零 + 关键帧目检
     ─▶ ⑦ 配乐 + 混音 + 母带 ─▶ ⑧ 逐帧截图 → 编码 → 合成 ─▶ ⑨ 七项校验 → 交付
```

### ① 数据宪法
通读文稿，把所有要进片子的数字/事实/人名固化成一张清单（写进 `shots/facts.md`）。
之后任何画面、文案、字幕**只能引用清单**，禁止临场发挥。
- 可验证的数字放大，不可验证的细节留白（宁可信息少，不可信息假）。
- 每个数字只讲一次，放在情绪峰值。
- 数字必须"有事发生"地出现：配绘制生长、同步计数、砸落。

### ② 文案与字幕分块
写口播稿（`shots/vo_lines.json`）：一句一行，每句 4–12 秒，全片 8–16 句。
- 开场 5 秒决定完播：钱/冲突/悬念三选一压进第一句（如"如果给你 X，去修一条路——敢接吗？"）。
- 结构参考：钩子 → 难题 → 否决 → 解法 → 检验 → 结算 → 人物 → 收尾（可裁剪）。
- 每句手动指定字幕分块（`"cues": [...]`，单块 ≤18 字），比机械按标点切更稳。

### ③ 配音
`python templates/vo_tts.py`（默认 edge-tts，免费；本地有 GPU 时可换音色克隆模型，
见 references/audio.md）。每句输出 wav + 实测时长 `audio/vo/vo_dur.json`。
- 中文数字年份逐字转写（2022 → 二零二二）；小数点转"点"。
- TTS 偶发空响应：脚本须重试 + 断点续跑。

### ④ 时间轴同步
`python templates/sync.py`：场景时长 = 0.25s 提前量 + 句长 + 尾部呼吸（0.5–1.9s），
自动把 TL（时间轴）、CUES（字幕）写回 `anim.html`，并生成 `shots/timeline.json` 供混音用。
换配音后**必须重跑**，且按新旧时长比例缩放场景内 VO 对齐的动作时刻。

### ⑤ 动画
复制 `templates/anim.html` 改场景。骨架已含：蓝图风设计系统、工具函数、审计器、
扫描线转场、字幕层、3 个示例场景。核心模式：
- 每场景 `defscene(id, cam=>{...; return (t,d)=>{...}})`，render 是纯函数。
- 两层运动：主动作（画线/砸落）+ 持续层（虚线行进/漂浮/脉冲）。
- 摄像机永远有 1.4%–3% 缓推——画面不是静帧。
- "先出后进"：旧元素完全退场再进新元素，杜绝交叉叠加。
- 视觉规范与动效语言：**读 references/design-system.md 和 references/motion.md**。

### ⑥ 审计 + 目检（质量门，不可跳过）
浏览器里跑 `auditText()`（文字越界）与 `auditOverlap()`（元素重叠），**归零才能截图**。
审计器抓不到"丑"：每场景选内容峰值帧截图目检（文字裁切/构图空洞/风格跑色/图形形状），
硬伤立即修。设计意图性重叠给元素加 `data-okov="1"` 豁免。

### ⑦ 声音
`python templates/music.py` 程序合成轻快配乐（零版权风险）；或用自备曲目（注意版权）。
`python templates/mix.py`：VO 按 RMS 归一 → 配乐 ducking（人声附近压低）→
音效只留重音（每场景 ≤2 个 thud，拒绝 whoosh 铺底——音效是标点不是背景）→
自写峰值包络限幅 → ffmpeg loudnorm 两遍到 -14 LUFS / TP -1.5。

### ⑧ 渲染
```
python templates/shoot.py 0 <dur> a --html anim.html   # ×N 段并行
python templates/render.py                              # 编码→末帧校验→拼接→合成
```
Playwright 逐帧截图（device_scale_factor=2，JPEG q93）→ 分段 x264 crf19 →
**逐段末帧 vs 源图校验（RMS<8，抓无报错坏段）** → concat → 音画合成
（pan 显式复制为立体声、+faststart）。

### ⑨ 七项校验
`python templates/check.py`：无缝循环（首末帧 RMS<5）· 音轨存在 · 字幕可见性 ·
风格色序（每帧 B>G>R 防跑色）· 空白帧 · 体积/时长 · faststart。全 PASS 才交付。
交付物：成片 mp4 + srt 字幕 + 发布文案（标题≤15字/一句话简介/标签）。

## 环境

```
python 3.10+，pip install playwright numpy soundfile pillow edge-tts
playwright install chromium
ffmpeg（PATH 中可用）
```

## 目录约定（每个工程项目）

```
<project>/
├── shots/vo_lines.json    # 文案+字幕分块（唯一的内容源）
├── shots/facts.md         # 数据宪法
├── shots/timeline.json    # sync.py 生成，供混音
├── tools/web/anim.html    # 动画（从 templates/anim.html 复制改造）
├── audio/vo|music|mix/    # 声音
└── out/                   # 帧、分段、成片
```

## 红线

- 不编造：数据、人名、事件必须有来源；`[待核实]` 不清零不进配音。
- 红色只表达"判定"语义（淘汰/验收章），绝不做装饰。
- 引用外部音乐先确认授权；默认用程序合成配乐。
- 涉及真实人物/企业后缀名与数字，交付前逐项核对数据宪法。

## 参考

| 文件 | 内容 |
|---|---|
| references/design-system.md | 视觉系统：色彩纪律、字号三级、图签、制图语法 |
| references/motion.md | 动效语言清单：何时用哪种动效、参数 |
| references/audio.md | 声音管线：TTS 选型、混音公式、母带目标 |
| references/pitfalls.md | 踩坑清单（按代价排序，出问题先查这里） |
| templates/ | 可直接运行的骨架与管线脚本 |
