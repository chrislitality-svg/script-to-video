# -*- coding: utf-8 -*-
"""Playwright 逐帧截图：python templates/shoot.py <t0> <t1> <seg> [--html anim.html] [project_dir]
输出 <project>/out/frames_<seg>/NNNNNN.jpg（device_scale_factor=2）。"""
import pathlib, sys
from playwright.sync_api import sync_playwright

args = [a for a in sys.argv[1:] if not a.startswith("--")]
html = sys.argv[sys.argv.index("--html") + 1] if "--html" in sys.argv else "anim.html"
proj = args[3] if len(args) > 3 else "."
ROOT = pathlib.Path(proj).resolve()
f0, f1, seg = float(args[0]), float(args[1]), args[2]
out = ROOT / f"out/frames_{seg}"; out.mkdir(parents=True, exist_ok=True)
FPS = 30
with sync_playwright() as p:
    b = p.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text", "--hide-scrollbars", "--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": 1080, "height": 1440}, device_scale_factor=2)
    pg.goto((ROOT / "tools/web" / html).resolve().as_uri())
    pg.wait_for_timeout(400)
    for fi in range(int(f0 * FPS), int(f1 * FPS)):
        pg.evaluate(f"setTime({fi / FPS:.4f})")
        pg.screenshot(path=str(out / f"{fi:06d}.jpg"), type="jpeg", quality=93)
    b.close()
print(f"{seg}: {int(f1 * FPS) - int(f0 * FPS)} 帧 -> {out}")
