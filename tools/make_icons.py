#!/usr/bin/env python3
"""生成 lens-km PWA 图标。

用法:  python3 tools/make_icons.py
输出:  icons/icon-192.png, icons/icon-512.png, icons/icon-maskable-512.png,
       icons/apple-touch-icon-180.png, icons/favicon-32.png, icons/icon.svg
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

BILINEAR = Image.Resampling.BILINEAR
LANCZOS = Image.Resampling.LANCZOS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'icons')

ACCENT = (0, 255, 136)        # --accent #00ff88
INK = (18, 22, 28)            # 背景顶部
INK2 = (5, 7, 11)             # 背景底部
PAPER = (243, 246, 248)       # 纸张
LINE = (176, 186, 196)        # 文字行
LINE_DARK = (120, 132, 145)

SS = 4  # 超采样倍数


def gradient(size):
    """竖向渐变背景"""
    img = Image.new('RGB', (1, size))
    px = img.load()
    if px is None:
        raise RuntimeError('无法创建渐变图像')
    for y in range(size):
        t = y / max(1, size - 1)
        px[0, y] = tuple(int(INK[i] + (INK2[i] - INK[i]) * t) for i in range(3))
    return img.resize((size, size), BILINEAR)


def draw_artwork(size, rounded=True, scale=1.0, offset=(0, 0)):
    """绘制取景框 + 纸张 + 扫描线"""
    s = size * SS
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))

    # --- 背景 ---
    bg = gradient(s).convert('RGBA')
    mask = Image.new('L', (s, s), 0)
    md = ImageDraw.Draw(mask)
    if rounded:
        md.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 0.225), fill=255)
    else:
        md.rectangle([0, 0, s - 1, s - 1], fill=255)
    img.paste(bg, (0, 0), mask)

    # --- 绿色取景框四角 ---
    d = ImageDraw.Draw(img)
    vf = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vf)
    L = s * 0.20 * scale          # 取景框边长
    T = s * 0.17 * scale          # 边长（上下）
    ox, oy = offset[0] * s, offset[1] * s
    cx, cy = s / 2 + ox, s / 2 + oy
    x0, x1 = cx - s * 0.295 * scale, cx + s * 0.295 * scale
    y0, y1 = cy - s * 0.325 * scale, cy + s * 0.325 * scale
    arm = s * 0.095 * scale
    th = max(2, int(s * 0.036 * scale))
    for (px, py, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)):
        vd.line([(px, py), (px + dx * arm, py)], fill=ACCENT + (255,), width=th)
        vd.line([(px, py), (px, py + dy * arm)], fill=ACCENT + (255,), width=th)
    img = Image.alpha_composite(img, vf)

    # --- 纸张 ---
    d = ImageDraw.Draw(img)
    pw, ph = s * 0.335 * scale, s * 0.455 * scale
    px0, py0 = cx - pw / 2, cy - ph / 2
    d.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], radius=int(s * 0.028 * scale), fill=PAPER + (255,))

    # --- 文字行 ---
    lh = ph * 0.05
    gap = ph * 0.082
    top = py0 + ph * 0.15
    for i, frac in enumerate((0.78, 0.62, 0.70)):
        y = top + i * gap
        col = LINE_DARK if i == 0 else LINE
        d.rounded_rectangle(
            [px0 + pw * 0.13, y, px0 + pw * (0.13 + 0.74 * frac), y + lh],
            radius=int(lh / 2), fill=col + (255,))
    # 底部小色块，暗示"已识别内容"
    d.rounded_rectangle(
        [px0 + pw * 0.13, top + 3 * gap + lh * 0.4, px0 + pw * 0.13 + pw * 0.30, top + 3 * gap + lh * 1.4],
        radius=int(lh / 2), fill=ACCENT + (110,))

    # --- 扫描线（带辉光）---
    glow = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    ly = py0 + ph * 0.80
    gd.rectangle([px0 - s * 0.02, ly - s * 0.006, px0 + pw + s * 0.02, ly + s * 0.006], fill=ACCENT + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(s * 0.018))
    img = Image.alpha_composite(img, glow)
    d = ImageDraw.Draw(img)
    d.rectangle([px0 - s * 0.01, ly - s * 0.0045, px0 + pw + s * 0.01, ly + s * 0.0045], fill=ACCENT + (255,))

    return img


def save(img, size, path):
    img = img.resize((size, size), LANCZOS)
    img.save(path, 'PNG', optimize=True)
    print('written', os.path.relpath(path, ROOT), f'{size}x{size}')


def main():
    os.makedirs(OUT, exist_ok=True)

    # 普通图标：圆角背景 + 完整取景框
    art = draw_artwork(512, rounded=True, scale=1.0)
    save(art, 192, os.path.join(OUT, 'icon-192.png'))
    save(art, 512, os.path.join(OUT, 'icon-512.png'))
    save(art, 32, os.path.join(OUT, 'favicon-32.png'))

    # maskable：满幅背景 + 缩小到安全区
    m = draw_artwork(512, rounded=False, scale=0.72)
    save(m, 512, os.path.join(OUT, 'icon-maskable-512.png'))

    # iOS apple-touch-icon：满幅、无透明
    a = draw_artwork(512, rounded=False, scale=0.86)
    save(a, 180, os.path.join(OUT, 'apple-touch-icon-180.png'))

    # SVG 源文件（矢量，可缩放，与 PNG 版式一致）
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#12161C"/>
      <stop offset="1" stop-color="#05070B"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-300%" width="160%" height="700%">
      <feGaussianBlur stdDeviation="9"/>
    </filter>
  </defs>
  <rect width="512" height="512" rx="115" fill="url(#bg)"/>
  <g fill="none" stroke="#00ff88" stroke-width="18" stroke-linecap="round" stroke-linejoin="round">
    <path d="M105 138 V105 A16 16 0 0 1 121 89 H154"/>
    <path d="M358 89 H391 A16 16 0 0 1 407 105 V138"/>
    <path d="M407 374 V407 A16 16 0 0 1 391 423 H358"/>
    <path d="M154 423 H121 A16 16 0 0 1 105 407 V374"/>
  </g>
  <rect x="170" y="139" width="172" height="234" rx="14" fill="#F3F6F8"/>
  <g>
    <rect x="192" y="174" width="99" height="12" rx="6" fill="#788491"/>
    <rect x="192" y="193" width="79" height="12" rx="6" fill="#B0BAC4"/>
    <rect x="192" y="212" width="89" height="12" rx="6" fill="#B0BAC4"/>
    <rect x="192" y="236" width="52" height="12" rx="6" fill="#00ff88" opacity="0.45"/>
  </g>
  <rect x="160" y="320" width="192" height="12" rx="6" fill="#00ff88" opacity="0.55" filter="url(#glow)"/>
  <rect x="165" y="323" width="182" height="6" rx="3" fill="#00ff88"/>
</svg>
'''
    with open(os.path.join(OUT, 'icon.svg'), 'w') as f:
        f.write(svg)
    print('written', os.path.relpath(os.path.join(OUT, 'icon.svg'), ROOT))


if __name__ == '__main__':
    main()
