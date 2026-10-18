# -*- coding: utf-8 -*-
"""一键出图：SVG → 临时 HTML → Edge 无头截图 → PNG（2 倍分辨率）

用法: python build_all.py
依赖: Edge/Chrome 浏览器（用于把 SVG 渲染成 PNG）
"""
import os
import re
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
DIA = os.path.abspath(os.path.join(HERE, "..", "diagrams"))

# 画布尺寸（与 SVG 内部布局常量保持一致）
TARGETS = [("erd", 2250, 1210), ("class-diagram", 2250, 1234)]

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]


def find_browser():
    for p in BROWSERS:
        if os.path.exists(p):
            return p
    raise SystemExit("未找到 Edge/Chrome，请手动安装或用浏览器打开 SVG 另存为 PNG")


def main():
    subprocess.run([sys.executable, "make_diagrams.py"], cwd=HERE, check=True)
    browser = find_browser()

    for name, w, h in TARGETS:
        svg_path = os.path.join(DIA, name + ".svg")
        svg = open(svg_path, encoding="utf-8").read()
        svg = re.sub(r'width="\d+" height="\d+"', f'width="{w}" height="{h}"', svg, count=1)

        html_path = os.path.join(DIA, "_%s.html" % name)
        open(html_path, "w", encoding="utf-8").write(
            '<!doctype html><html><head><meta charset="utf-8">'
            "<style>html,body{margin:0;padding:0;background:#FBFCFD}svg{display:block}</style>"
            "</head><body>" + svg + "</body></html>")

        png = os.path.join(DIA, name + ".png")
        url = "file:///" + html_path.replace("\\", "/").replace(" ", "%20")
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=2", "--virtual-time-budget=3000",
                        f"--window-size={w},{h}", f"--screenshot={png}", url],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(html_path)
        print("rendered", name, os.path.getsize(png) // 1024, "KB")


if __name__ == "__main__":
    main()
