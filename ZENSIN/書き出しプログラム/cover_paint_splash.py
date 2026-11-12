# ZENSIN リールカバー（参考：絵の具が飛び散る背景＋人物＋英語タイトル＋日本語サブ）
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
rng = np.random.default_rng(int(sys.argv[3]) if len(sys.argv) > 3 else 7)
TITLE = sys.argv[1] if len(sys.argv) > 1 else "LOVE WHAT YOU DO"
SUB = sys.argv[2] if len(sys.argv) > 2 else "〜好きだから、やめられない〜"
OUT = sys.argv[4] if len(sys.argv) > 4 else "cover.png"

WARM = [(232, 74, 28), (245, 128, 30), (250, 176, 40), (214, 40, 40), (255, 200, 60)]
COOL = [(30, 110, 200), (40, 160, 230), (20, 70, 150), (90, 190, 240), (10, 40, 110)]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

# 紙
paper = np.full((H, W, 3), 246, np.float32)
paper += rng.normal(0, 3.5, (H, W, 1))
canvas = paper.copy()

def blob_mask(cx, cy, r, rough=0.45):
    """ぎざぎざの縁の絵の具のかたまり"""
    ang = np.arctan2(yy - cy, xx - cx)
    d = np.hypot(xx - cx, yy - cy)
    k = rng.integers(5, 11)
    wob = sum(rng.uniform(0.05, rough / 2) * np.sin(ang * rng.integers(2, 13) + rng.uniform(0, 6.28)) for _ in range(k))
    m = np.clip((r * (1 + wob) - d) / 6, 0, 1)
    return m

def paint(mask, col, alpha=0.9):
    global canvas
    a = (mask * alpha)[..., None]
    canvas = canvas * (1 - a) + np.array(col, np.float32) * a

def side_col(x):
    # 左は暖色、右は寒色
    return WARM[rng.integers(len(WARM))] if x < W * 0.5 + rng.normal(0, 120) else COOL[rng.integers(len(COOL))]

# 水彩のにじみ（いくつもの大きさのノイズを重ねた形）
def noise_field(scales=(260, 120, 50, 18), weights=(1.0, 0.6, 0.35, 0.2)):
    f = np.zeros((H, W), np.float32)
    for sc, wt in zip(scales, weights):
        g = rng.random((H // sc + 3, W // sc + 3)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((W + 3 * sc, H + 3 * sc), Image.BICUBIC)
        im = im.filter(ImageFilter.GaussianBlur(max(2, sc / 3)))
        a = np.asarray(im).astype(np.float32)[:H, :W] / 255
        f += (a - 0.5) * wt
    return f
def wash(col, env, thr, alpha, edge=True):
    global canvas
    n = noise_field()
    m = np.clip((n + env - thr) * 6, 0, 1)
    m = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))) / 255
    if edge:  # 水彩の縁が少し濃くなる
        e = np.clip(m - np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))) / 255, 0, 1) * 1.6
        m = np.clip(m * 0.75 + e, 0, 1)
    a = (m * alpha)[..., None]
    canvas = canvas * (1 - a) + np.array(col, np.float32) * a
# 位置ごとの「濃さ」：左上〜左は暖色、右上〜右は寒色、下は両方
lx = np.exp(-((xx - 230) ** 2) / (2 * 300 ** 2)) * np.exp(-((yy - 800) ** 2) / (2 * 620 ** 2))
rx = np.exp(-((xx - 850) ** 2) / (2 * 300 ** 2)) * np.exp(-((yy - 800) ** 2) / (2 * 620 ** 2))
bot = np.clip((yy - 1450) / 300, 0, 1)
for col in [(250, 176, 40), (245, 128, 30), (232, 74, 28), (214, 40, 40), (150, 20, 30)]:
    wash(col, lx * 0.9 + bot * 0.35 * (xx < W / 2), 0.62 + rng.uniform(-0.05, 0.08), rng.uniform(0.55, 0.85))
for col in [(90, 190, 240), (40, 160, 230), (30, 110, 200), (20, 70, 150), (10, 40, 110)]:
    wash(col, rx * 0.9 + bot * 0.35 * (xx >= W / 2), 0.62 + rng.uniform(-0.05, 0.08), rng.uniform(0.55, 0.85))
# 筆のかすれ
for _ in range(18):
    cx, cy = rng.uniform(0, W), rng.normal(820, 380)
    w, h = rng.uniform(140, 360), rng.uniform(10, 30)
    th = rng.uniform(-0.6, 0.6)
    c, s_ = np.cos(th), np.sin(th)
    u = (xx - cx) * c + (yy - cy) * s_
    v = -(xx - cx) * s_ + (yy - cy) * c
    hair = np.sin(v * rng.uniform(0.8, 1.6) + rng.uniform(0, 6)) * 0.5 + 0.5
    m = np.clip(1 - np.abs(u) / w, 0, 1) ** 0.5 * np.clip(1 - np.abs(v) / h, 0, 1) * (hair > 0.35)
    m = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))) / 255
    paint(m, side_col(cx), rng.uniform(0.35, 0.7))
# 飛び散り（小さな点）
for _ in range(700):
    x = rng.uniform(0, W); y = rng.uniform(0, H)
    if rng.random() < 0.5 and 300 < x < 780 and y < 1400: continue
    r = rng.exponential(4) + 0.8
    y0, y1, x0, x1 = int(max(0, y - 30)), int(min(H, y + 30)), int(max(0, x - 30)), int(min(W, x + 30))
    m = np.clip((r - np.hypot(xx[y0:y1, x0:x1] - x, yy[y0:y1, x0:x1] - y)) / 1.2, 0, 1)
    a = (m * rng.uniform(0.6, 1.0))[..., None]
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - a) + np.array(side_col(x), np.float32) * a
# 下の垂れ
for _ in range(110):
    x = rng.uniform(0, W); top = rng.uniform(1560, 1820); w = rng.uniform(2, 9)
    m = np.clip((w - np.abs(xx - x)) / 1.5, 0, 1) * (yy > top)
    col = np.array(side_col(x) if rng.random() < 0.8 else (25, 25, 30), np.float32)
    a = (m * rng.uniform(0.6, 1.0))[..., None]
    canvas = canvas * (1 - a) + col * a
# 上の角の筆の円
for (cx, cy, col) in [(180, 210, (245, 150, 30)), (900, 210, (40, 150, 230))]:
    d = np.hypot(xx - cx, yy - cy)
    ring = np.clip(1 - np.abs(d - 125) / 7, 0, 1) * (rng.random((H, W)) > 0.2)
    paint(ring, col, 0.8)
    paint(np.clip(1 - np.abs(d - 98) / 3, 0, 1), col, 0.45)

bg = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)).convert("RGBA")

# 人物
src = Image.open("cut_504.png").convert("RGBA").crop((0, 0, 1920, 1080))
# 下に足りない分は、いちばん下の行をのばして体を続ける（あとで絵の具で隠れる）
arr = np.array(src)
ext = np.repeat(arr[-1:, :, :], 520, axis=0)
src = Image.fromarray(np.concatenate([arr, ext], axis=0))
scale = 1.05
cut = src.resize((int(src.width * scale), int(src.height * scale)), Image.LANCZOS)
px, py = (W - cut.width) // 2, 300
# 人物の縁にうっすら影
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
a = cut.split()[3].filter(ImageFilter.GaussianBlur(18))
sh.paste((0, 0, 0, 255), (px + 8, py + 8), a)
sh.putalpha(sh.split()[3].point(lambda v: int(v * 0.35)))
bg = Image.alpha_composite(bg, sh)
bg.alpha_composite(cut, (px, py))

# 下の絵の具を人物の上にも少し重ねる（参考の雰囲気）
over = np.array(bg).astype(np.float32)
fade = np.clip((yy - 1640) / 220, 0, 1)
for _ in range(60):
    x = rng.uniform(0, W); top = rng.uniform(1660, 1860); w = rng.uniform(4, 14)
    m = np.clip((w - np.abs(xx - x)) / 2, 0, 1) * (yy > top)
    col = np.array(side_col(x), np.float32)
    a = (m * rng.uniform(0.6, 0.95))[..., None]
    over[..., :3] = over[..., :3] * (1 - a) + col * a
for _ in range(18):
    cx = rng.uniform(0, W); cy = rng.normal(1850, 60)
    m = blob_mask(cx, cy, rng.uniform(50, 120), rough=0.12) * fade
    m = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))) / 255
    a = (m * 0.85)[..., None]
    over[..., :3] = over[..., :3] * (1 - a) + np.array(side_col(cx), np.float32) * a
bg = Image.fromarray(np.clip(over, 0, 255).astype(np.uint8))

# 金の細い枠（二重）
d = ImageDraw.Draw(bg)
GOLD = (196, 160, 92, 255)
d.rectangle((22, 22, W - 23, H - 23), outline=GOLD, width=3)
d.rectangle((36, 36, W - 37, H - 37), outline=GOLD, width=1)

# タイトル
def text_center(img, txt, font, y, fill, stroke=0, stroke_fill=(0, 0, 0), shadow=True, track=0):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    widths = [font.getlength(c) + track for c in txt]
    x = (W - (sum(widths) - track)) / 2
    for c, w in zip(txt, widths):
        dd.text((x, y), c, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += w
    if shadow:
        a = lay.split()[3].filter(ImageFilter.GaussianBlur(10))
        shl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        shl.putalpha(a.point(lambda v: int(v * 0.85)))
        img = Image.alpha_composite(img, shl)
    return Image.alpha_composite(img, lay)

f_title = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf", 112)
while f_title.getlength(TITLE) > W - 120:
    f_title = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf", f_title.size - 4)
f_sub = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 46, index=0)
TY = 1040
bg = text_center(bg.convert("RGBA"), TITLE, f_title, TY, (255, 255, 255, 255), stroke=2, stroke_fill=(30, 30, 30), track=-2)
bg = text_center(bg, SUB, f_sub, TY + f_title.size + 18, (255, 255, 255, 255), stroke=2, stroke_fill=(30, 30, 30), track=2)
bg.convert("RGB").save(OUT)
print("saved", OUT)
