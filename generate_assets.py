from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import math, random

ROOT = Path(__file__).resolve().parent
W, H = 1672, 941

def font(size, bold=False):
    candidates = [
        r"C:\\Windows\\Fonts\\arialbd.ttf" if bold else r"C:\\Windows\\Fonts\\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def centered(draw, xy, text, f, fill, stroke=0, stroke_fill=None):
    box = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
    x = xy[0] - (box[2]-box[0])/2
    y = xy[1] - (box[3]-box[1])/2
    draw.text((x, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)

# --- Background ---
img = Image.new("RGB", (W, H))
px = img.load()
for y in range(H):
    t = y / (H-1)
    for x in range(W):
        u = x / (W-1)
        glow = max(0, 1 - math.hypot((u-.5)*1.7, (t-.46)*1.35))
        r = int(8 + 25*glow + 10*(1-t))
        g = int(2 + 5*glow)
        b = int(22 + 52*glow + 18*(1-u))
        px[x, y] = (r, g, b)

draw = ImageDraw.Draw(img, "RGBA")
random.seed(3123)
for _ in range(180):
    x, y = random.randrange(W), random.randrange(H)
    a = random.randrange(35, 150)
    r = random.choice([1,1,2,3])
    draw.ellipse((x-r,y-r,x+r,y+r), fill=(220,185,255,a))

# top ornament
centered(draw, (W/2, 54), "PERFECT WORLD", font(34, True), (235,220,255,235))
centered(draw, (W/2, 91), "КОЛЕСО ФОРТУНЫ", font(28, True), (184,130,255,230))
draw.line((W*.30, 116, W*.70, 116), fill=(170,95,255,150), width=2)

# central glow behind wheel
for rr in range(620, 360, -8):
    alpha = int(2 + (620-rr)*0.05)
    draw.ellipse((W*.5-rr, H*.51-rr, W*.5+rr, H*.51+rr), outline=(145,65,255,alpha), width=5)

# bottom button
bx0, by0, bx1, by1 = W*.35, H*.805, W*.65, H*.925
for i in range(18, 0, -1):
    a = int(25 + (18-i)*5)
    draw.rounded_rectangle((bx0-i,by0-i,bx1+i,by1+i), radius=28+i, fill=(121,39,220,a))
draw.rounded_rectangle((bx0,by0,bx1,by1), radius=28, fill=(104,35,190,235), outline=(228,180,255,255), width=3)
centered(draw, ((bx0+bx1)/2, (by0+by1)/2), "КРУТИТЬ", font(34, True), (255,245,255,255))
centered(draw, (W/2, H*.965), "Один шанс — один приз", font(17), (205,178,235,180))

img.save(ROOT / "roulette_background.jpg", quality=94, optimize=True)

# --- Transparent wheel ---
S = 900
wheel = Image.new("RGBA", (S, S), (0,0,0,0))
wd = ImageDraw.Draw(wheel, "RGBA")
cx = cy = S/2
bbox = (42, 42, S-42, S-42)
prizes = ["10 000 000\nюаней", "Игровой\nпредмет", "Заказать\nмузыку", "Секретный\nприз"]
segments = [(92,45,155,235), (120,65,190,245), (165,80,225,220), (115,55,180,245)]

# shadow rings
for r in range(430, 404, -2):
    wd.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(0,0,0,max(20,130-(430-r)*4)), width=4)

start = -90
for i, label in enumerate(prizes):
    end = start + 90
    wd.pieslice(bbox, start=start, end=end, fill=segments[i], outline=(255,215,145,255), width=4)
    # inner highlight
    wd.arc((58,58,S-58,S-58), start=start+2, end=end-2, fill=(255,255,255,45), width=3)
    mid = math.radians((start+end)/2)
    tx = cx + math.cos(mid)*245
    ty = cy + math.sin(mid)*245
    lines = label.split("\n")
    f = font(31, True)
    for j, line in enumerate(lines):
        centered(wd, (tx, ty + (j-(len(lines)-1)/2)*38), line, f, (255,250,240,255), 2, (45,10,65,210))
    start = end

# gold rim
wd.ellipse(bbox, outline=(255,220,145,255), width=14)
wd.ellipse((67,67,S-67,S-67), outline=(120,50,185,255), width=6)
wd.ellipse((385,385,515,515), fill=(49,15,75,255), outline=(255,220,145,255), width=10)
wd.ellipse((420,420,480,480), fill=(190,80,255,255), outline=(255,245,210,255), width=5)
centered(wd, (450, 450), "PW", font(34, True), (255,245,255,255))

# pointer marker at top (part of background layer is intentionally separate)
wheel.save(ROOT / "wheel_layer.webp", quality=96, method=6)

print("Generated roulette_background.jpg and wheel_layer.webp")
