---
name: script-to-video
description: >
  把一份文稿做成一条可复现的短视频。画面风格不预设：先用多轮问询定风格
  （一种，或底样式加一层点缀）、时长、配音，未知时再问画幅和配乐情绪，
  然后才开始生产。纯代码渲染：单文件 HTML 的确定性时间轴 → Playwright
  逐帧截图 → ffmpeg。蓝图×瑞士数据只是风格目录里的一项，不是默认外观。
  适用于：已有文稿要做宣发、讲解、叙事或数据短片；需要可审计、逐帧可复现；
  任何会写代码的模型直接执行。不要在用户没选风格时做成工程科普蓝图。
---

# script-to-video · 文稿 → 短视频

三条总纲：

1. **先问再画**。风格、时长、配音没有落到 `shots/brief.json` 之前，不写画面、不配音、不截图。用户第一句话里已经说清的项，记下来，不要再问。
2. **确定性时间轴**。动画是纯函数 `setTime(t)`：同一时刻永远是同一帧。才能跳帧审计、分段截图、改一个常量全片变速。
3. **配音实测驱动时间轴**。先配音、量出每句时长，再排场景。数字和人名只来自数据宪法，不临场编。

蓝图色板不是全局规范。`references/design-system.md`（原仓库）只在选中 `blueprint` 时生效。其他风格各自声明不超过 5 色，并写一行色检。

## 0. 开场问询

一次只问一个问题，用用户正在用的语言。细则和 `brief.json` 字段见 `references/brief.md`。风格必须是 `references/styles.md` 里的真实 id，禁止自造风格名。

顺序：

1. **风格**。一种，或混搭（一个底 + 一层点缀）。给 4–6 个跟题材相配的真实 id，加上「混搭」和「你来定」。不要把整张目录倒出来。`blueprint` 只是选项之一。题材不是工程、硬件、专利、制图时，不要把它放进首推，更不要在用户没说话时偷偷选它。
2. **时长**。用户说「你定」时才用 60 秒。允许范围 30–150 秒。
3. **配音**。只许这四只 edge-tts：沉稳男声 `zh-CN-YunyangNeural`、年轻男声 `zh-CN-YunxiNeural`、清晰女声 `zh-CN-XiaoxiaoNeural`、活泼女声 `zh-CN-XiaoyiNeural`，再加语速慢/中/快（`rate`：`-8%` / `+0%` / `+12%`）。选定后写入 `shots/vo_lines.json` 的 `voice` 和 `rate`。原脚本 `templates/vo_tts.py` 从这里读，没有写死音色，不要另加 `--voice`。
4. **画幅**、**配乐情绪**。只有前三项都定了、而这两项用户还没说时才问。画幅用户说「你定」时用 3:4（1080×1440，因为现有骨架是这个尺寸）。这只是画幅默认，不是视觉风格默认。

「你来定」风格：你选一个贴题的 id，用一句话说明，写入 brief，然后进入下一步。不要选 `blueprint`，除非题材本身是工程制图或用户提到了蓝图。

混搭：`mix.base` 是底样式，决定调色板（≤5 色）。`mix.accent` 只贡献一层，而且必须声明是 `type`（字体与排版）、`texture`（材质、网点、纸纹）或 `motion`（运动方式）里的哪一种。禁止把两套调色板平均成第三种没名字的颜色。点缀的 id 也必须在目录里。

问完立刻写入 `shots/brief.json`。缺字段就还在问询里，不要开画。

## 流程（问询之后九步，一步不过关就退回）

```
文稿 ─▶ ① 数据宪法 ─▶ ② 文案+字幕分块 ─▶ ③ 配音（实测时长）
     ─▶ ④ 时间轴 sync ─▶ ⑤ 动画 anim.html ─▶ ⑥ 双审计归零 + 关键帧目检
     ─▶ ⑦ 配乐 + 混音 + 母带 ─▶ ⑧ 逐帧截图 → 编码 → 合成 ─▶ ⑨ 七项校验 → 交付
```

### ① 数据宪法

通读文稿，把要进片子的数字、事实、人名写成 `shots/facts.md`。画面、文案、字幕只能引用这张清单。

- 可核对的数字放大，核对不了的细节留白。宁可少，不可假。
- 每个数字只讲一次，放在情绪高点，并且「有事发生」：生长、计数或砸落，具体做法服从所选风格，不要一律画成工程标注。
- `[待核实]` 不清零，不进配音。

### ② 文案与字幕分块

`shots/vo_lines.json`：一句一行。60 秒左右大约 8–12 句，每句大约 4–12 秒；时长不是 60 秒时按比例增减，全片仍落在 brief 的 `duration_s` 附近。

- 开场几秒要有钩子，但钩子的口气跟风格走，不要每条都写成工程设问。
- 结构可以是钩子、难题、转折、解法、收尾，按文稿裁，不要套死「否决 / 验收章」。
- 每句自带字幕分块（`"cues"`，单块建议 ≤18 字）。`painted-animation` 默认画面不放说明文字：字幕可以烧在片外或只做 srt，不要在画里堆字。

`voice` 用 brief 里的 `voice_id`。`rate` 用 `voice_note` 里的语速（慢 `-8%`、中 `+0%`、快 `+12%`）。

### ③ 配音

`python templates/vo_tts.py`（edge-tts，读 json 里的 `voice` 和 `rate`）。每句 wav，时长写入 `audio/vo/vo_dur.json`。

- 中文年份逐字（2022 → 二零二二），小数点说「点」。
- 空响应要重试，已有 wav 跳过。
- 音色克隆见原仓库 `references/audio.md`，那是升级选项，不是这一步的默认。

### ④ 时间轴同步

`python templates/sync.py`：场景时长 = 0.25 秒提前 + 句长 + 尾部呼吸（约 0.5–1.9 秒）。把时间轴和字幕写回 `anim.html`，并写出 `shots/timeline.json`。

换配音后必须重跑，并按新旧时长比例缩放句内与口播对齐的动作。

### ⑤ 动画

从 `templates/anim.html` 起改，但先按 brief 换掉蓝图皮。骨架里的网格、图签、色值只在 `blueprint` 时保留。

- 每场景 `defscene(id, cam=>{...; return (t,d)=>{...}})`，render 是纯函数。禁止跨帧状态和 `Math.random()`。
- 主动作之外留一层持续运动。摄像机可以缓推，幅度服从风格：蓝图约 1.4%–3%；水彩、水墨、默片不要照搬这个百分比。
- 先出后进，避免叠在一起读不清。
- 动效原理仍可读原仓库 `references/motion.md`，但「盖红章、维界线、扫描线」只属于蓝图或用户点名的点缀，不是每条片子的必选项。
- 混搭时：底样式的调色板和构图语法不动；点缀只出现在声明的那一层。

### ⑥ 审计 + 目检

浏览器里 `auditText()`（越界）和 `auditOverlap()`（重叠）归零，才能截图。故意重叠加 `data-okov="1"`。

审计不管好不好看。每个场景截一张内容最满的帧，看裁切、空洞、跑色、图形是否还像选定的风格。硬伤当时改。

### ⑦ 声音

配乐默认仍是程序合成，零版权。原 `templates/music.py` 没有情绪参数，固定 C 大调、BPM 108、输出 `audio/music/bright.wav`。

- `music_mood` 为「轻快」或用户说「你定」：直接用这个脚本。
- 其他情绪：只在项目副本里改 BPM 和和弦进行，把改了什么记在 brief 的 `source_note`。不要给脚本发明一套没实现的命令行参数，也不要换未授权的成曲。
- `python templates/mix.py`：口播按 RMS 归一，配乐在人声处 ducking，音效只打重音（每场景不超过 2 个，不铺 whoosh），自写峰值限幅，ffmpeg loudnorm 两遍到 -14 LUFS / TP -1.5。

### ⑧ 渲染

```
python templates/shoot.py 0 <dur> a --html anim.html   # 可分段并行
python templates/render.py
```

Playwright 逐帧（device_scale_factor=2，JPEG q93）→ 分段 x264 crf19 → 每段末帧对源图（RMS<8）→ concat → 音画（立体声用 pan 复制，+faststart）。

画幅不是 3:4 时，先改骨架的画布尺寸和审计安全区，再截图。不要只在编码时硬拉。

### ⑨ 七项校验

`python templates/check.py` 的七项都要过，但第 4 项按风格分叉：

| 条件 | 第 4 项 |
|---|---|
| 底样式是 `blueprint` 且没有换调色板 | 保持原检查：抽样帧 B>G>R。红色只用于判定（淘汰、验收），次数等于判定次数。 |
| 其他任何风格或混搭 | **不要**跑 B>G>R。改成 brief 里那一行 `color_check`：抽样帧的主色落在声明的 ≤5 色里，跑出色失败。 |

其余六项不变：首末帧循环 RMS<5、有音轨、字幕带看得见（画面内无字幕的风格改为检查 srt 覆盖口播）、无空白帧、体积与时长、faststart。全过才交付。

交付：mp4、srt、发布文案（标题建议 ≤15 字、一句话、标签）。文案里的数字回查数据宪法。

## 环境

```
python 3.10+，pip install playwright numpy soundfile pillow edge-tts
playwright install chromium
ffmpeg（PATH 中可用）
```

脚本在原仓库 `templates/`。本升级只改技能说明，不替换那些脚本。

## 目录

```
<project>/
├── shots/brief.json       # 问询结果，开画前必须有
├── shots/vo_lines.json    # 文案、字幕分块、voice、rate
├── shots/facts.md
├── shots/timeline.json
├── tools/web/anim.html
├── audio/vo|music|mix/
└── out/
```

## 红线

- 不编造数据、人名、事件。来源里没有的数字不进画面。
- 不把蓝图当成没选风格时的外观。
- 红色「只表判定」只约束 `blueprint`。剪纸、海报等风格里的红是材质，不受这条限制。
- 外部音乐先确认授权。默认程序合成。
- 真实人物和机构的数字，交付前对一遍数据宪法。

## 参考

| 文件 | 何时读 |
|---|---|
| references/brief.md | 问询话术和 brief.json |
| references/styles.md | 可选风格。问询前先读，只推荐表里有的 id |
| references/design-system.md | **仅** `blueprint`。色彩、字号、图签、制图。不是全局 |
| references/motion.md | 动效原理；具体招数要服从当前风格 |
| references/audio.md | TTS 备选、混音、母带 |
| references/pitfalls.md | 出问题先查 |
| templates/ | 原仓库骨架与管线，本升级未改 |
