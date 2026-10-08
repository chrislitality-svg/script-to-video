# 怎么做出好看的片子

任何会写代码的模型都按这份做，不依赖某一种模型的默认审美。管线仍是本仓库的 `templates/`：单文件 HTML、`setTime(t)`、Playwright、ffmpeg。不要改去 HyperFrames、Remotion、Three 工程或付费数字人，除非用户明确要求另开一条路。

蓝图、图纸、终端文档都不是没选风格时的外观。科普、故事、产品、节庆，用 brief 里那个底样式。

数字、人名、结论只来自 `shots/facts.md`。画面上的数要能指回某一行。示意性的图必须标成示意，不能写成实测。

## 1. 先写分镜，再画

问询结束、`shots/brief.json` 齐了之后，在配音之前写 `shots/storyboard.md`。一行一个镜头，对着将要说的那一句：

| 列 | 写什么 |
|---|---|
| 这句要让人想通的事 | 先写认知，再写画面。剖开、对比、拿掉、标出路径、把旧方案叠上新方案，选一个。不要「这句配一张图」。 |
| 画面上只发生的一件事 | 一镜一意。快的是动作，慢的是意思。意思没读完，不要把整屏倒在前 25% 然后停住。 |
| 运动为什么服务于这句 | 说得出原因才动。说不出，就不要这个招。 |
| 停留 | 这句口播还没说完，镜头不切走。 |

第 0 秒必须已经是一张完成的构图，不是半个字飞进来，也不是空台。信息流里，第一眼就是封面。

最后一镜是收束，不是新事实：把已经说过的结论收成一句，或让开场的那个物件回来。不要再引入 facts 里没有的数字，也不要没人要求就加广告口号。口播的最后一句要说完，嘴和字幕都落稳再结束。

用户没另要分镜确认时，写完就继续，不要再开一轮提问。

## 2. 字要在手机上读得完

- 一屏一句。中文单块字幕仍按技能正文，建议不超过 18 字。
- 字幕在说完之后还留得住：不少于这句口播再加约 0.6 秒，并且不要短于约 1.8 秒。标题卡不要一闪而过。
- 字进安全区。1080 宽的画，正文离边大约不少于 96px；竖屏按比例收。不要压住脸、主物件和平台会挡住的底边（大约画面下方 15% 留给字幕和界面）。
- 主标题要大到缩成约 360px 宽仍能读。小标签不是第二套正文。
- 一套字体一个声音：正文一种，需要「机器在说话」时才用等宽，而且不要每条片子都加。发光只给标题或那一个信号色，不要满屏发光。
- 变形容器里换字，先出后进，禁止两句叠在一起。

`painted-animation` 仍默认画面里不放说明文字，字幕走片外或 srt。

## 3. 运动要有原因

同一类东西用同一种手感，全片不要一会儿弹簧一会儿匀速漂。没有理由的匀速滑动，看起来最便宜。

从这些做法里挑，一条片子两三种就够，并且要重复同一种语法，不要每镜换一套：

- 前景变成转场：眼下这个字或形放大穿过去，下一场已经在后面，中间没有空帧。
- 一个物件活过好几镜：选中的卡片、笔、圆点换身份，不要每句整屏换页。
- 一层主运动，加上错开的小动作。不要整帧一起开始、一起停。
- 先让人读完，再快出、慢进。全片不能一个速度。至少有一处明显加快或放慢，有一处喘口气。
- 硬切可以，但主体、方向和材料要接得上，切完运动还在。默认淡入淡出不是风格。
- 动作要有结果：扫过之后出现发现，按下之后状态变了。说「缓存」的那个词出现时，画面上的东西才出现、移动或被比较。只把字放出来，就是幻灯片。
- 这一句的主角不要缩在角落。讲到它的那一镜，它至少占画面高度的大约三分之一；全片最重要的那一镜，让它占住可用画面的大部分，不要一张小卡片飘在空场里。
- 手绘、蜡笔、剪纸、像素：笔触可以一拍二（大约每秒 12 次），镜头和光仍逐帧平滑。阶梯式的镜头会像卡顿。

切的时候把要带到下一镜的物件放在同一像素上，上一镜末帧和下一镜首帧对得上。

## 4. 不要掉进没人点名的默认脸

没给设计方向时，模型容易做成同一套：米白底、标题里斜体衬线点一个词、01/02/03、满屏等宽小标签、胶囊按钮、每张卡片发光、所有东西弹一下。底样式自己就是这样才保留，而且一镜最多一次。

同样不要默认：深色底加居中大字再全部淡入淡出。只有用户选了暗色、终端、科幻或「信号」这类底样式才用暗底。面向日常消费者的片子，开场不要压成看不清的暗调，除非风格本身就是夜景或默片。

用户说「涂鸦」但没指明是火柴人、烂涂鸦还是圆珠笔时，不要猜，回到风格问询，给 4–6 个目录里的真实 id。不要把两套画风揉成第三种没名字的线、五官和色板。混搭仍只许 brief 里那一层：字体、材质或运动。

参考片只学节奏和转场语法。不搬别人的版式、角色、标志、镜头和旋律。

## 5. 声音：沿用本仓库的混音，不新发明参数

口播压乐、母带和音效上限以 `references/audio.md` 为准，由 `templates/mix.py` 执行，不要改脚本去追别的仓库的 LUFS：

- 人声按 RMS 归一到约 -16.5 dB，配乐约 -23 dB，人声处配乐大约再掉 8 dB（包络 -60%）。
- 母带仍是两遍 loudnorm，-14 LUFS，真峰值 -1.5 dBTP。
- 每场景音效不超过 2 个，只打在看得到的动作上。不要铺 whoosh。

在这个上限里再守三条，都是摆放，不是新参数：

- 配乐情绪跟题材走，不要每条都配成科技发布会。家庭、服务、故事用留白或沉稳；用户说「你定」时仍用现成轻快程序配乐。
- 大约一半的切点没有音效。转场若要一声，用短、不轰的一下，不要低频很长的风声。同一声不要连用两次。
- 有口播时，乐在人声下。模型听不见，交付时说明你只看了响度表，请用户听一遍。

## 6. 目检时看图，不看自己的代码

审计归零不够。每一镜截内容最满的一帧，再出一张大约每秒一帧的接触印样，以及开场、每次切换前后、收束帧。快速动作拼一条连续帧。缩到约 360px 宽再看一遍字。

看这些，并写上时间点：

- 第 0 秒是不是已经成立。
- 有没有空白帧、切的时候新旧字叠在一起、字幕挡住主体。
- 主体够不够大，留白是风格还是空。
- 字的颜色和底是不是糊在一起。
- 这一镜还像不像 brief 里的底样式。跑成蓝图蓝底，而底样式不是 `blueprint`，就是失败。
- 数字能不能在 facts 里找到。

改完再截。确认你看的是这一次渲染的图：等渲染进程结束，或写到新目录。上一轮留在磁盘上的帧不能拿来证明这次改好了。干净、不报错，仍然可以因为空、慢、太像幻灯片而不合格。

色检仍按技能正文：底样式是 `blueprint` 才做 B>G>R。其他风格用 brief 的 `color_check`。纸色、夜景会让「四角必须暗」这类通用检查误报，以看图为准，不要为了通过检查把风格改掉。

## 来源

规则是转述，不是原文。长提示词、画风配方、品牌片分镜都没有贴进来。

| 读过的文件 | 用了什么 |
|---|---|
| [lemomo-ai/lemo-opuscar `DIRECTOR.md`](https://github.com/lemomo-ai/lemo-opuscar/blob/main/DIRECTOR.md) / [`TECHNIQUE.md`](https://github.com/lemomo-ai/lemo-opuscar/blob/main/TECHNIQUE.md) | 三秒内有事发生；字幕停留；快慢交替；一声对一个动作；画面是时间的函数；接触印样 |
| [tuzhechen2005/opus-video-skills `kinetic-reel`](https://github.com/tuzhechen2005/opus-video-skills/blob/main/skills/kinetic-reel/SKILL.md) | 一镜要有机制；切在拍上；事实与示意分开；转场少用噪声 whoosh |
| [同仓库 `painted-animation`](https://github.com/tuzhechen2005/opus-video-skills/blob/main/skills/painted-animation/SKILL.md) | 一次只给一个阅读点；动作快、意思留住；收尾呼应开场 |
| [Kianzzz/xilo-opus-video `craft-rules.md`](https://github.com/Kianzzz/xilo-opus-video/blob/main/skills/xilo-opus-video/references/craft-rules.md) | 一屏一句、约 2.5 秒可读；主体约三分之一；手机宽度；避开「暗底居中大字淡入淡出」 |
| [A3-Media/opus-video-skills `craft.md`](https://github.com/A3-Media/opus-video-skills/blob/main/skills/video-director/references/craft.md) / [`video-review`](https://github.com/A3-Media/opus-video-skills/blob/main/skills/video-review/SKILL.md) | 点名要避开的默认脸；一镜一意；字号与安全区；揭示不要堆在前 25% |
| [liuzhaowei1/Digital-OPUS-VIDEO-SKILL `docs/CRAFT.md`](https://github.com/liuzhaowei1/Digital-OPUS-VIDEO-SKILL/blob/main/docs/CRAFT.md) | 先定认知动作；一套字体一个声音；安全边距 |
| [grapeot/opus-video-audio-skill 帧技能](https://github.com/grapeot/opus-video-audio-skill/blob/master/skills/procedural-video-frames/SKILL.md) | 看图不看数；不要审到上一轮的旧帧；每个数字要有来源 |
| [cclank/lanshu-create-ai-presenter-video](https://github.com/cclank/lanshu-create-ai-presenter-video/blob/main/references/styled-explainer.md) | 口播是时钟；第 0 秒是封面；词到了才演；收束一帧复习；事实只来自事实表。九种演法的 id 在 `references/styles.md` |
| [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit/blob/main/business-motion-film/references/motion-grammar.md) | 前景转场、贯穿物件、换速度、动作要有结果、第 0 帧已经完成。不搬那 28 支发布片的版式 |
| [threerocks/hand-drawn-styles `PROTOCOL.md`](https://github.com/threerocks/hand-drawn-styles/blob/main/PROTOCOL.md) | 「涂鸦」有歧义时停下让人选；禁止把两套配方揉成第三套。配方正文没有抄 |

没能用上的，写在 `references/styles.md` 末尾。
