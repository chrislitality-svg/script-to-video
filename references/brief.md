# 开场问询

一次一句。用用户的语言。第一句话里已经有的项写进 `shots/brief.json`，跳过对应问题。全部必填项齐了再进入 SKILL 的第 ① 步。

风格 id 只能来自 `styles.md`。不要发明「电影感」「高级灰」这类不在表里的名字；用户这么说时，把它映射到表里最接近的一个 id，告诉用户映射了哪一个，得到确认再写入。用户拒绝就再给一轮 4–6 个，仍然一次一句。

## 问题顺序

### 1. 风格

先用一句话复述题材（工程 / 故事 / 数据 / 产品 / 节庆……），再给 4–6 个相配的 id，外加两个固定选项。

话术（按题材换掉例子，id 必须真实存在）：

> 这条片子想用哪种画面？可以说一个名字，也可以混搭。
> 贴题的有：`ink-wash` 水墨、`whiteboard` 白板讲解、`dataviz` 数据叙事、`kinetic-reel` 动态大字、`painted-animation` 水彩卡通。
> 也可以回「混搭」，或「你来定」。

上面五个只是讲法示例。工程、硬件、专利才把 `blueprint` 放进这 4–6 个。科普不等于蓝图：科学内容可以是白板、数据叙事、水彩或铜版画。

- 用户给出一个 id：`style_ids` 只有它，`mix` 为 `null`。
- 「你来定」：你选一个贴题 id，一句话说明为什么，写入后不再问风格。非工程不选 `blueprint`。
- 「混搭」：下一句只问这一件——底是哪个 id，点缀是哪个 id，点缀属于字体（`type`）、材质（`texture`）还是运动（`motion`）。底决定调色板。不要问第三套颜色。

混搭问法：

> 混搭需要一个底、再加一层。底用哪个（决定颜色）？点缀用哪个，是字体、材质，还是运动？例如底 `iso-infographic`，点缀 `risograph` 的套印颗粒（材质）。

### 2. 时长

> 大概多长？30 到 150 秒都可以。没想法就说「你定」，我按 60 秒做。

超出范围：说一句范围，请对方给一个范围内的数。只问这一次，对方坚持则用最近的边界（30 或 150）并在 `source_note` 里记下原话。

### 3. 配音

> 配音用哪种？
> 1. 沉稳男声 `zh-CN-YunyangNeural`
> 2. 年轻男声 `zh-CN-YunxiNeural`
> 3. 清晰女声 `zh-CN-XiaoxiaoNeural`
> 4. 活泼女声 `zh-CN-XiaoyiNeural`
> 语速：慢、中、快。说「你定」的话，讲解用 1、中速；故事用 2 或 4、中速。

`voice_note` 写人话，例如「沉稳男声，中速」。语速进 `vo_lines.json` 的 `rate`：慢 `-8%`，中 `+0%`，快 `+12%`。

原 `templates/vo_tts.py` 读取 `shots/vo_lines.json` 的 `voice` 和 `rate`，没有命令行音色参数。不要改脚本来加 `--voice`。

### 4. 画幅（仅未知时）

> 画幅？3:4 竖版、9:16 竖版、16:9 横版，或 1:1。说「你定」就用 3:4。

3:4 只因为现有 HTML 骨架是 1080×1440。它不是风格默认。

### 5. 配乐（仅未知时）

> 配乐情绪？轻快、沉稳、紧张、留白。说「你定」就用现成的轻快程序配乐（C 大调，BPM 108）。

`templates/music.py` 没有情绪开关。轻快 / 你定：原样运行。其他情绪只在项目副本里改 BPM 和和弦，不新增命令行参数，不用未授权曲子。

## 选完之后补上的两行（不问用户，除非底样式不是蓝图且你拿不准）

非 `blueprint`，或混搭的底不是 `blueprint`：在 brief 里自己写好

- `palette`：最多 5 个 `#RRGGBB`，来自底样式，不跟点缀平均。
- `color_check`：一行人话，说明抽样帧怎样算跑色。例如「主色应落在纸白、墨黑、花青里；出现工程蓝底即失败」。

`blueprint` 且没有换调色板：`palette` 固定为 `#0E2843`、`#E9F2FB`、`#8FB3D4`、`#FFC24B`、`#FF6157`，`color_check` 写「抽样帧 B>G>R；红色像素只出现在判定镜头」。辅色 `#5D82A6` 若用上，放进 palette 时拿掉一个非红辅色，仍不超过 5。红不进装饰。

## brief.json

路径：`shots/brief.json`。

```json
{
  "style_ids": ["ink-wash"],
  "mix": null,
  "duration_s": 60,
  "aspect": "3:4",
  "voice_id": "zh-CN-YunyangNeural",
  "voice_note": "沉稳男声，中速",
  "music_mood": "留白",
  "palette": ["#F4F0E6", "#1A1A1A", "#3E5C56", "#8A8A8A"],
  "color_check": "抽样帧以纸色和墨色为主；出现 #0E2843 工程蓝底即失败",
  "source_note": "风格来自公开目录 references/styles.md，不是 X 收藏。用户原话：水墨，大约一分钟，男声稳一点。"
}
```

混搭时 `mix` 不为 null，`style_ids` 仍列出底和点缀，底在前：

```json
{
  "style_ids": ["iso-infographic", "risograph"],
  "mix": { "base": "iso-infographic", "accent": "risograph", "layer": "texture" },
  "duration_s": 90,
  "aspect": "16:9",
  "voice_id": "zh-CN-XiaoxiaoNeural",
  "voice_note": "清晰女声，中速",
  "music_mood": "轻快",
  "palette": ["#F6F3EC", "#1F2A44", "#E26D5A", "#2F6F4E", "#E0B15A"],
  "color_check": "底色是等距信息图的浅纸色，不是蓝图深蓝；网点只作为颗粒，不引入第六种主色",
  "source_note": "公开目录。点缀只取 risograph 的套印错位，调色板不与底平均。"
}
```

| 字段 | 类型 | 约束 |
|---|---|---|
| `style_ids` | string[] | 1 个，或混搭时 2 个（底、点缀）。都必须在 styles.md |
| `mix` | null 或对象 | 对象含 `base`、`accent`、`layer`。`layer` 只能是 `type`、`texture`、`motion` |
| `duration_s` | number | 30–150。仅当用户说「你定」时填 60 |
| `aspect` | string | `3:4`、`9:16`、`16:9`、`1:1`。用户说「你定」时填 `3:4` |
| `voice_id` | string | 只能是 Yunyang、Yunxi、Xiaoxiao、Xiaoyi 四只 zh-CN Neural |
| `voice_note` | string | 音色人话 + 慢/中/快 |
| `music_mood` | string | `轻快`、`沉稳`、`紧张`、`留白` 之一 |
| `palette` | string[] | 1–5 个十六进制色。蓝图用规范色；其他风格自定并写明 |
| `color_check` | string | 一行。非蓝图禁止写 B>G>R |
| `source_note` | string | 用户原话里和选择有关的部分；标明风格来自公开目录，不是收藏 |

`palette` 和 `color_check` 是色检所必需，和上面八个选择一起写。不要另做一份口头设定。

示例里的非蓝图色值只说明字段形状，不是上游规定的色板。开画前按底样式的 `STYLE.md` 重写 `palette`，仍不超过 5 色。蓝图那五个色是 design-system 里的真实色值。

未读到用户 X 收藏。`source_note` 不得声称某个风格来自收藏帖。以后若补进收藏，在 styles.md 加行，并在这里注明帖子链接。
