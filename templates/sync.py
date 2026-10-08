# -*- coding: utf-8 -*-
"""按配音实测时长重建 anim.html 的 TL/CUES + 生成 shots/timeline.json
    python templates/sync.py [project_dir]
规则：场景 dur = LEAD + vo + tail；字幕按手动 cues 的字重分摊 VO 窗口。
换配音后必须重跑；场景内 VO 对齐的动作时刻需按新旧时长比例缩放。"""
import json, pathlib, sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
LEAD = 0.25
TAIL = json.load(open(ROOT / "shots/tail.json", encoding="utf8")) if (ROOT / "shots/tail.json").exists() else {}
dur = json.load(open(ROOT / "audio/vo/vo_dur.json", encoding="utf8"))
LINES = json.load(open(ROOT / "shots/vo_lines.json", encoding="utf8"))["lines"]

shots, start = [], 0.0
for ln in LINES:
    sid = ln["id"]
    d = round(LEAD + dur[sid] + TAIL.get(sid, 0.55), 2)
    shots.append({"id": sid, "start": round(start, 2), "dur": d,
                  "vo": [{"at": LEAD, "dur": dur[sid], "text": ln["text"]}]})
    start = round(start + d, 2)
DUR = round(start, 2)
json.dump({"dur": DUR, "tempo": 1.0, "shots": shots},
          open(ROOT / "shots/timeline.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

# ---- CUES：手动分块按字重分摊 VO 窗口 ----
CUES = []
for sh in shots:
    sid = sh["id"]
    ln = next(l for l in LINES if l["id"] == sid)
    parts = ln.get("cues") or [ln["text"]]
    t0, t1 = sh["start"] + LEAD, sh["start"] + LEAD + dur[sid]
    if len(parts) == 1:
        CUES.append({"s": t0, "e": round(t1 + 0.1, 2), "zh": parts[0]}); continue
    ws = [max(2, sum(2 if ord(c) > 127 else 1 for c in p)) for p in parts]
    acc = t0
    for p, w in zip(parts, ws):
        e = acc + (t1 - t0) * w / sum(ws)
        CUES.append({"s": round(acc, 2), "e": round(e, 2), "zh": p}); acc = e
    CUES[-1]["e"] = round(t1 + 0.1, 2)

# ---- 写回 anim.html 的 TL 与 CUES ----
ph = ROOT / "tools/web/anim.html"
html = ph.read_text(encoding="utf8")
import re
html = re.sub(r'const TL=\{"dur":[\d.]+,"shots":\[.*?\]\};',
              'const TL={"dur":%s,"shots":[%s]};' % (DUR, ",".join(
                  '{"id":"%s","start":%s,"dur":%s}' % (s["id"], s["start"], s["dur"]) for s in shots)),
              html, count=1, flags=re.S)
html = re.sub(r'let CUES=\[.*?\];',
              'let CUES=[%s];' % ",".join('{"s":%s,"e":%s,"zh":"%s"}' % (c["s"], c["e"], c["zh"]) for c in CUES),
              html, count=1, flags=re.S)
ph.write_text(html, encoding="utf8")
print(f"总长 {DUR}s | TL/CUES 已写回 anim.html | timeline.json 已生成")
for s in shots: print(" ", s["id"], s["start"], s["dur"])
