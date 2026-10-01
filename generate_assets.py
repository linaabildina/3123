from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math, random

ROOT = Path(__file__).resolve().parent
W, H = 1672, 941

def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def centered(draw, xy, text, f, fill, stroke=0, stroke_fill=None):
    box = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
    x = xy[0] - (box[2] - box[0]) / 2
    y = xy[1] - (box[3] - box[1]) / 2
    draw.text((x, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)

# ---------- Fantasy visual background ----------
img = Image.new("RGB", (W, H), (8, 2, 24))
px = img.load()
for y in range(H):
    t = y / (H - 1)
    for x in range(W):
        u = x / (W - 1)
        moon = max(0, 1 - math.hypot((u - .63) * 2.2, (t - .17) * 2.8))
        center = max(0, 1 - math.hypot((u - .5) * 1.35, (t - .55) * 1.5))
        r = int(7 + 42 * moon + 22 * center)
        g = int(2 + 8 * center)
        b = int(22 + 70 * moon + 42 * center)
        px[x, y] = (r, g, b)

draw = ImageDraw.Draw(img, "RGBA")
random.seed(3123)

# glowing moon
for rr in range(110, 48, -4):
    a = max(8, int(45 * (110 - rr) / 62))
    draw.ellipse((W*.67-rr, H*.14-rr, W*.67+rr, H*.14+rr), fill=(190,130,255,a))
draw.ellipse((W*.67-52, H*.14-52, W*.67+52, H*.14+52), fill=(220,210,255,245))
draw.ellipse((W*.67-45, H*.14-45, W*.67+45, H*.14+45), fill=(180,170,240,220))

# distant mountains / cliffs
for layer, col in [
    (0, (18, 8, 52, 255)),
    (1, (25, 10, 72, 255)),
    (2, (35, 12, 88, 255)),
]:
    y0 = 350 + layer * 70
    pts = [(0, H), (0, y0)]
    for x in range(0, W + 80, 80):
        yy = y0 - abs(math.sin(x/145 + layer))*110 - random.randint(0, 45)
        pts.append((x, yy))
    pts += [(W, y0), (W, H)]
    draw.polygon(pts, fill=col)

# waterfalls
for x in [150, 260, 1080, 1190, 1320]:
    top = random.randint(270, 410)
    length = random.randint(180, 330)
    draw.line((x, top, x + 8, top + length), fill=(100, 130, 255, 130), width=20)
    draw.line((x, top, x + 4, top + length), fill=(190, 180, 255, 150), width=7)

# pagodas / lanterns
def pagoda(x, y, s):
    c = (255, 75, 180, 210)
    dark = (16, 5, 35, 245)
    draw.rectangle((x-s*.18, y-s*.55, x+s*.18, y), fill=dark, outline=c, width=max(1, int(s*.025)))
    for yy, ww in [(y-s*.55, s*.48), (y-s*.36, s*.65), (y-s*.17, s*.82)]:
        draw.polygon([(x-ww/2, yy), (x+ww/2, yy), (x+ww*.36, yy+s*.08), (x-ww*.36, yy+s*.08)], fill=dark, outline=c)
    draw.ellipse((x-s*.06, y-s*.40, x+s*.06, y-s*.28), fill=(255, 160, 80, 230))

for x, y, s in [(90,390,70),(330,330,55),(510,285,45),(760,315,52),(1010,280,62),(1210,335,58),(1390,300,80),(1550,370,55)]:
    pagoda(x,y,s)

# foreground platform
draw.polygon([(0,H*.78),(W*.72,H*.72),(W,H*.78),(W,H),(0,H)], fill=(8,4,22,245))
for y in range(int(H*.80), H, 35):
    draw.line((0,y,W,y), fill=(100,55,150,90), width=2)

# cherry blossoms and floating petals
for _ in range(250):
    x = random.randrange(W)
    y = random.randrange(H)
    r = random.choice([2,3,4,6,8])
    a = random.randrange(70, 220)
    draw.ellipse((x-r,y-r,x+r,y+r), fill=(255,70,210,a))
    if r >= 6:
        draw.ellipse((x-r*2,y-r*.35,x+r*2,y+r*.35), fill=(255,130,235,a//2))

# right-side fantasy character silhouette/glow to echo the reference
cx, cy = int(W*.84), int(H*.48)
for rr in range(330, 190, -8):
    a = int(2 + (330-rr)*0.35)
    draw.ellipse((cx-rr, cy-rr, cx+rr, cy+rr), outline=(220,75,255,a), width=5)
draw.ellipse((cx-95, cy-165, cx+95, cy+25), fill=(115,55,150,150), outline=(255,170,255,170), width=3)
draw.polygon([(cx-115,cy-110),(cx-205,cy+250),(cx+20,cy+315),(cx+160,cy-70)], fill=(24,8,42,220), outline=(195,75,255,160))

# ---------- Wheel-ready center space ----------
for rr in range(520, 300, -8):
    a = int(3 + (520-rr)*0.12)
    draw.ellipse((W*.48-rr, H*.51-rr, W*.48+rr, H*.51+rr), outline=(185,65,255,a), width=4)

# no countdown/time text: intentionally removed
img.save(ROOT / "roulette_background.jpg", quality=94, optimize=True)

# ---------- Transparent wheel ----------
S = 900
wheel = Image.new("RGBA", (S, S), (0,0,0,0))
wd = ImageDraw.Draw(wheel, "RGBA")
cx = cy = S / 2
bbox = (42, 42, S-42, S-42)

prizes = [
    "10 000 000\nюаней",
    "Игровой\nпредмет",
    "Заказать\nмузыку",
    "Секретный\nприз",
]
segments = [
    (175, 22, 42, 245),
    (20, 70, 180, 245),
    (205, 15, 225, 245),
    (95, 25, 175, 245),
]

# outer glow
for r in range(432, 405, -3):
    wd.ellipse((cx-r,cy-r,cx+r,cy+r), outline=(210,70,255,max(15,110-(432-r)*3)), width=5)

start = -90
for i, label in enumerate(prizes):
    end = start + 90
    wd.pieslice(bbox, start=start, end=end, fill=segments[i], outline=(255,215,145,255), width=5)
    wd.arc((58,58,S-58,S-58), start=start+2, end=end-2, fill=(255,255,255,55), width=4)
    mid = math.radians((start+end)/2)
    tx = cx + math.cos(mid)*245
    ty = cy + math.sin(mid)*245
    f = font(31, True)
    lines = label.split("\n")
    for j, line in enumerate(lines):
        centered(wd, (tx, ty + (j-(len(lines)-1)/2)*38), line, f, (255,250,240,255), 2, (35,5,55,220))
    start = end

# ornate rim
wd.ellipse(bbox, outline=(255,220,145,255), width=14)
wd.ellipse((67,67,S-67,S-67), outline=(135,45,205,255), width=8)
wd.ellipse((375,375,525,525), fill=(30,7,52,255), outline=(255,220,145,255), width=10)
wd.ellipse((405,405,495,495), fill=(150,45,235,255), outline=(255,245,210,255), width=5)
centered(wd, (450,450), "PW", font(34, True), (255,245,255,255))

wheel.save(ROOT / "wheel_layer.webp", quality=96, method=6)
print("Generated roulette_background.jpg and wheel_layer.webp")
