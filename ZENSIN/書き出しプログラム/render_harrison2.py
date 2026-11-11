# ZENSIN 書き出し（ハリソン・フォード 案A）
# 指示書「最新の仕様」と 8〜15本目の形に合わせる：
#  1080×1920、黒背景、16:9 の角丸カード（幅1020・高さ574・半径80・縁70pxを最大55%暗く）、最初の約1.5秒で中央の線から上下に開く
#  字幕は一番上のレイヤー、行頭 x 80、最後の行の下端 y 723。リード白 / 本文クリーム #E9DCC0 / 強調語 白＋黒い発光
#  ロゴ x 474・y 1188・高さ188・不透明度60%、その下にタイトルと話者名
import os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS_NUM, FPS_DEN = 24000, 1001
FPS = FPS_NUM / FPS_DEN
SRC = "Harrison.mp4"
SEGS = [(141.20, 150.30), (157.30, 162.55), (355.40, 372.35), (460.10, 477.70)]
AUDIO = os.environ.get("AUDIO", "mix.wav")
OUT = sys.argv[1] if len(sys.argv) > 1 else "out.mp4"
LOGO = "logo.png" if os.path.exists("logo.png") else None
ONLY = None
if len(sys.argv) > 2:  # 確認用：指定の秒だけ PNG に書き出す
    ONLY = [float(x) for x in sys.argv[2].split(",")]

CARD_W, CARD_H, CARD_X = 1020, 574, 30
CARD_Y = (H - CARD_H) // 2  # 673
RADIUS, EDGE, EDGE_MAX = 80, 70, 0.55
OPEN_T = 1.5
CROP = "crop=1680:945:120:128"  # 右上の「N LIVE」(y 35〜120)を外す

CREAM = (233, 220, 192)
WHITE = (255, 255, 255)
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
INTER = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
SZ_LEAD, SZ_BODY, SZ_EMPH = 90, 120, 156  # 720基準 60/80/104 の1.5倍
TRACK = -0.07
X0, BOTTOM = 80, 723

fonts = {}
def font(size, path=SERIF, index=0):
    k = (size, path, index)
    if k not in fonts:
        fonts[k] = ImageFont.truetype(path, size, index=index)
    return fonts[k]

# ---- 字幕（リールの秒）。行は「／」、強調語は【】、最重要語は《》 ----
SUBS = [
    (0.10, 5.00, "正直／生涯功労賞は／少し【不思議】だ"),
    (5.00, 8.95, "まだ／キャリアの／【折り返し】／なのに"),
    (9.10, 11.10, "ちょっと／【早い】よね？"),
    (12.10, 13.95, "僕はまだ／【現役】の／俳優だ"),
    (14.45, 16.45, "この世界は／【入る】のも／難しい"),
    (17.55, 22.20, "ありがたいことに／【やめる】ほうが／難しかった"),
    (23.85, 25.60, "この仕事が／《好き》だから"),
    (26.95, 31.00, "俳優は／【いくつもの】／人生を／生きられる"),
    (32.55, 34.50, "僕は本当に／【運】がいい"),
    (36.20, 38.80, "【仲間】に／出会えた"),
    (40.20, 42.70, "挑める／【仕事】が／ある"),
    (44.00, 45.90, "今も／【続けて】／いられる"),
    (46.80, 48.70, "それを／【当たり前】だと／思わない"),
]
TITLE = "好きだから、やめられない。"
NAME_JA = "ハリソン・フォード"
NAME_EN = "HARRISON FORD"

def parse_line(line, lead):
    runs, buf, mode = [], "", None
    i = 0
    while i < len(line):
        c = line[i]
        if c in "【《":
            if buf: runs.append((buf, "lead" if lead else "body"))
            buf, mode = "", ("emph" if c == "【" else "top")
        elif c in "】》":
            runs.append((buf, mode)); buf, mode = "", None
        else:
            buf += c
        i += 1
    if buf: runs.append((buf, "lead" if lead else "body"))
    return runs

def run_style(kind):
    if kind == "lead": return SZ_LEAD, WHITE
    if kind == "body": return SZ_BODY, CREAM
    return SZ_EMPH, WHITE  # emph / top

def text_width(s, size):
    f = font(size)
    w = 0
    for ch in s:
        w += f.getlength(ch) + TRACK * size
    return w

def layout(sub):
    """各行の run を、ベースラインそろえで並べる。返り値: [(x, baseline, text, kind, size, color)]"""
    lines = sub.split("／")
    rows = []
    for li, line in enumerate(lines):
        runs = parse_line(line, li == 0 and len(lines) > 1)
        asc = max(font(run_style(k)[0]).getmetrics()[0] for _, k in runs)
        desc = max(font(run_style(k)[0]).getmetrics()[1] for _, k in runs)
        rows.append((runs, asc, desc))
    # 下から積む：最後の行の下端（字の下＝ベースライン＋小さめの余白）を BOTTOM に
    items = []
    y_bottom = BOTTOM
    placed = []
    for runs, asc, desc in reversed(rows):
        maxsize = max(run_style(k)[0] for _, k in runs)
        base = y_bottom - int(maxsize * 0.12)
        placed.append((runs, base))
        y_bottom = base - int(maxsize * 0.86) - 4  # 行間をつめる
    for runs, base in reversed(placed):
        x = X0
        for t, k in runs:
            size, col = run_style(k)
            items.append((x, base, t, k, size, col))
            x += text_width(t, size)
        if x > W - 50:
            print("WARN line too wide", sub, x, file=sys.stderr)
    return items

def draw_run(img, x, base, t, size, color, alpha=1.0):
    d = ImageDraw.Draw(img)
    f = font(size)
    asc = f.getmetrics()[0]
    cx = x
    for ch in t:
        d.text((cx, base - asc), ch, font=f, fill=color + (int(255 * alpha),))
        cx += f.getlength(ch) + TRACK * size

def ease_out(p):
    p = min(max(p, 0), 1)
    return 1 - (1 - p) ** 3

def render_sub(sub, t, t0, t1):
    """字幕1つを RGBA で描く（1080×1920）"""
    items = layout(sub)
    base_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    emph_layers = []
    a_in = ease_out((t - t0) / 0.4)
    a_out = 1.0 if t < t1 - 0.3 else max(0.0, (t1 - t) / 0.3)
    alpha = a_in * a_out
    dy = int(20 * (1 - a_in))
    for (x, base, txt, k, size, col) in items:
        if k in ("lead", "body"):
            draw_run(base_layer, x, base + dy, txt, size, col)
        else:
            delay, dur = (0.15, 0.35) if k == "emph" else (0.22, 0.45)
            p = (t - t0 - delay) / dur
            if p <= 0: continue
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw_run(lay, x, base + dy, txt, size, col)
            wfull = text_width(txt, size)
            # 左から右へ描き出し
            reveal = ease_out(p)
            arr = np.array(lay)
            cut = int(x + wfull * reveal + size * 0.15)
            arr[:, cut:, 3] = 0
            lay = Image.fromarray(arr)
            if k == "top":
                s = 1.12 - 0.12 * ease_out(p)
                if s != 1.0:
                    cxm, cym = x + wfull / 2, base + dy - size * 0.4
                    lay = lay.transform((W, H), Image.AFFINE,
                                        (1 / s, 0, cxm - cxm / s, 0, 1 / s, cym - cym / s), resample=Image.BICUBIC)
            glow = max(0.0, min(1.0, (p - 0.7) / 0.3))
            emph_layers.append((lay, glow))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # 通常の文字：薄い黒の影（2段のぼかし）
    a = np.array(base_layer)[:, :, 3]
    sh = Image.fromarray((a * 0.75).astype(np.uint8))
    sh1 = sh.filter(ImageFilter.GaussianBlur(6)); sh2 = sh.filter(ImageFilter.GaussianBlur(18))
    shadow = np.maximum(np.array(sh1), np.array(sh2))
    out = Image.alpha_composite(out, Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [Image.fromarray(shadow)]))
    out = Image.alpha_composite(out, base_layer)
    for lay, glow in emph_layers:
        if glow > 0:
            ga = np.array(lay)[:, :, 3].astype(np.float32)
            g1 = np.array(Image.fromarray(ga.astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))).astype(np.float32)
            g2 = np.array(Image.fromarray(ga.astype(np.uint8)).filter(ImageFilter.GaussianBlur(26))).astype(np.float32)
            gl = np.clip((g1 * 1.6 + g2 * 1.4) * glow, 0, 255).astype(np.uint8)
            out = Image.alpha_composite(out, Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [Image.fromarray(gl)]))
        out = Image.alpha_composite(out, lay)
    if alpha < 1:
        arr = np.array(out); arr[:, :, 3] = (arr[:, :, 3] * alpha).astype(np.uint8); out = Image.fromarray(arr)
    return out

# ---- 固定のレイヤー（ロゴ・タイトル・話者名） ----
def static_layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if LOGO:
        lg = Image.open(LOGO).convert("RGBA")
        h = 188; w = round(lg.width * h / lg.height)
        lg = lg.resize((w, h), Image.LANCZOS)
        a = np.array(lg); a[:, :, 3] = (a[:, :, 3] * 0.6).astype(np.uint8)
        lay.alpha_composite(Image.fromarray(a), ((W - w) // 2, 1188))
    def center(txt, y, f, fill, track=0.0):
        widths = [f.getlength(c) + track * f.size for c in txt]
        x = (W - (sum(widths) - track * f.size)) / 2
        for c, wv in zip(txt, widths):
            d.text((x, y), c, font=f, fill=fill); x += wv
    center(TITLE, 1415, font(56), CREAM + (255,))
    center(NAME_JA, 1495, font(30), WHITE + (255,))
    center(NAME_EN, 1540, ImageFont.truetype(INTER, 20), (255, 255, 255, 140), track=0.25)
    # タイトルにも薄い影
    a = np.array(lay)[:, :, 3]
    sh = Image.fromarray((a * 0.5).astype(np.uint8)).filter(ImageFilter.GaussianBlur(8))
    base = Image.merge("RGBA", [Image.new("L", (W, H), 0)] * 3 + [sh])
    return Image.alpha_composite(base, lay)

# ---- カードのマスク（角丸＋縁を暗く） ----
def card_mask():
    m = Image.new("L", (CARD_W, CARD_H), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, CARD_W - 1, CARD_H - 1), RADIUS, fill=255)
    m4 = m.resize((CARD_W * 4, CARD_H * 4)); m = m4.resize((CARD_W, CARD_H), Image.LANCZOS)
    # 縁からの距離で暗くする
    dist = np.array(m.filter(ImageFilter.GaussianBlur(EDGE / 2))).astype(np.float32) / 255
    dark = 1 - EDGE_MAX * np.clip(1 - dist * 1.0, 0, 1) ** 1.2
    return np.array(m).astype(np.float32) / 255, dark

mask, dark = card_mask()
STATIC = static_layer()

def frame_reader():
    flt = []
    for i, (a, b) in enumerate(SEGS):
        flt.append(f"[{i}:v]{CROP},scale={CARD_W}:{CARD_H}:flags=lanczos,eq=gamma=1.08:saturation=1.08,unsharp=5:5:0.4,setpts=PTS-STARTPTS[v{i}]")
    flt.append("".join(f"[v{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=1:a=0,fps={FPS_NUM}/{FPS_DEN}[v]")
    cmd = ["ffmpeg", "-loglevel", "error"]
    for a, b in SEGS: cmd += ["-ss", str(a), "-to", str(b), "-i", SRC]
    cmd += ["-filter_complex", ";".join(flt), "-map", "[v]", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = CARD_W * CARD_H * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n: break
        yield np.frombuffer(buf, np.uint8).reshape(CARD_H, CARD_W, 3)

def compose(fr, t):
    canvas = np.zeros((H, W, 3), np.float32)
    card = fr.astype(np.float32) * dark[:, :, None]
    # 開く動き：中央の細い線から上下に（最初は速く、だんだんゆっくり）
    hh = CARD_H if t >= OPEN_T else max(2, int(CARD_H * ease_out(t / OPEN_T)))
    top = (CARD_H - hh) // 2
    m = np.zeros_like(mask); m[top:top + hh] = mask[top:top + hh]
    if hh < CARD_H:  # 開いている途中も角を丸く
        sub = Image.new("L", (CARD_W, hh), 0)
        ImageDraw.Draw(sub).rounded_rectangle((0, 0, CARD_W - 1, hh - 1), min(RADIUS, hh // 2), fill=255)
        m = np.zeros_like(mask); m[top:top + hh] = np.array(sub).astype(np.float32) / 255
    region = canvas[CARD_Y:CARD_Y + CARD_H, CARD_X:CARD_X + CARD_W]
    canvas[CARD_Y:CARD_Y + CARD_H, CARD_X:CARD_X + CARD_W] = region * (1 - m[:, :, None]) + card * m[:, :, None]
    img = Image.fromarray(canvas.astype(np.uint8)).convert("RGBA")
    img = Image.alpha_composite(img, STATIC)
    for t0, t1, s in SUBS:
        if t0 <= t < t1:
            img = Image.alpha_composite(img, render_sub(s, t, t0, t1))
    return img.convert("RGB")

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO], capture_output=True, text=True).stdout)
nframes = int(dur * FPS)

if ONLY:
    frames = {}
    for i, fr in enumerate(frame_reader()):
        t = i / FPS
        for want in ONLY:
            if abs(t - want) < 0.5 / FPS:
                compose(fr, t).save(f"check_{want:05.2f}.png")
        if t > max(ONLY) + 1: break
    sys.exit(0)

enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", f"{FPS_NUM}/{FPS_DEN}", "-i", "-", "-i", AUDIO,
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i, fr in enumerate(frame_reader()):
    if i >= nframes: break
    enc.stdin.write(np.asarray(compose(fr, i / FPS)).tobytes())
    if i % 120 == 0: print(i, "/", nframes, flush=True)
enc.stdin.close(); enc.wait()
print("done", OUT)
