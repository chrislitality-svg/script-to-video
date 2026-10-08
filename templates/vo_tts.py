# -*- coding: utf-8 -*-
"""逐句配音（edge-tts，免费在线）→ audio/vo/takes/<id>_t1.wav (48k mono)
    python templates/vo_tts.py [project_dir]
读 shots/vo_lines.json，时长汇总写 audio/vo/vo_dur.json。
重试 + 断点续跑（已存在的 wav 跳过）。"""
import asyncio, json, pathlib, subprocess, sys
import edge_tts

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
CFG = json.load(open(ROOT / "shots/vo_lines.json", encoding="utf8"))
out = ROOT / "audio/vo/takes"; out.mkdir(parents=True, exist_ok=True)

async def gen(line):
    mp3, wav = out / f"{line['id']}.mp3", out / f"{line['id']}_t1.wav"
    if not wav.exists():
        for k in range(4):
            try:
                await edge_tts.Communicate(line["text"], CFG["voice"], rate=CFG.get("rate", "+0%")).save(str(mp3))
                if mp3.exists() and mp3.stat().st_size > 2000: break
            except Exception as e:
                print(f"retry {line['id']} #{k}: {e}", flush=True); await asyncio.sleep(2 + k * 2)
        else:
            raise RuntimeError(f"{line['id']} TTS failed")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ar", "48000", "-ac", "1", str(wav)], check=True)
        mp3.unlink(missing_ok=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                             capture_output=True, text=True).stdout.strip())
    return line["id"], d

async def main():
    durs = {}
    for ln in CFG["lines"]:
        sid, d = await gen(ln)
        durs[sid] = round(d, 3); print(sid, d, flush=True)
    json.dump(durs, open(ROOT / "audio/vo/vo_dur.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print("total", round(sum(durs.values()), 2))

asyncio.run(main())
