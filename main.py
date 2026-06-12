"""
Solar System Mission Control
============================
Student   : Hüseyin Tunay Çelik  |  ID: 97294
Course    : 3D Graphics — WSB Merito Wroclaw
Instructor: Vishnu Suresh

Controls:
  Mouse drag   - rotate camera
  Scroll       - zoom in/out
  R            - reset camera
  P            - pause/resume
  +/-          - speed up/slow down
  W/A/S/D/Space/Ctrl - freeflight controls
"""

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import time as _time
import numpy as np
import os
import urllib.request
from PIL import Image

# ═══════════════════════════════════════════════
# TEXTURE SETUP
# ═══════════════════════════════════════════════
TEXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures")
os.makedirs(TEXTURES_DIR, exist_ok=True)

TEXTURE_FILES = {
    "Sun": ("sunmap.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/sunmap.jpg"),
    "Mercury": ("mercurymap.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/mercurymap.jpg"),
    "Venus": ("venusmap.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/venusmap.jpg"),
    "Earth": ("earthmap1k.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/earthmap1k.jpg"),
    "Mars": ("marsmap1k.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/marsmap1k.jpg"),
    "Jupiter": ("jupitermap.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/jupitermap.jpg"),
    "Saturn": ("saturnmap.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/saturnmap.jpg"),
    "SaturnRings": ("saturnringcolor.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/saturnringcolor.jpg"),
    "Uranus": ("uranusmap.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/uranusmap.jpg"),
    "Neptune": ("neptunemap.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/neptunemap.jpg"),
    "Moon": ("moonmap1k.jpg", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/moonmap1k.jpg"),
    "Background": ("galaxy_starfield.png", "https://raw.githubusercontent.com/jeromeetienne/threex.planets/master/images/galaxy_starfield.png")
}

TEXTURES = {k: None for k in TEXTURE_FILES.keys()}

def load_texture(path):
    try:
        img = Image.open(path)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = img.convert("RGBA").tobytes()
        w, h = img.size
        
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, w, h, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        return tex_id
    except Exception as e:
        print(f"Error loading texture {path}: {e}")
        return None

def load_ring_texture(path):
    try:
        img = Image.open(path).convert("RGBA")
        datas = img.getdata()
        new_data = []
        for item in datas:
            r, g, b, a = item
            brightness = (r + g + b) / 3.0
            if brightness < 15:
                new_data.append((0, 0, 0, 0))
            else:
                alpha = int(min(255, brightness * 1.5))
                new_data.append((r, g, b, alpha))
        img.putdata(new_data)
        
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = img.tobytes()
        w, h = img.size
        
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        return tex_id
    except Exception as e:
        print(f"Error loading ring texture {path}: {e}")
        return None

def draw_loading_screen(win, message, progress_fraction):
    ww, wh = glfw.get_window_size(win)
    fw, fh = glfw.get_framebuffer_size(win)
    if ww <= 0 or wh <= 0 or fw <= 0 or fh <= 0:
        return
        
    glViewport(0, 0, fw, fh)
    glClearColor(0.0, 0.005, 0.012, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, ww, wh, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    bx = ww // 2 - 250
    by = wh // 2 - 60
    bw = 500
    bh = 120
    
    chamfer(bx, by, bw, bh, 10, fill=(0.0, 0.03, 0.07, 0.95), border=(0.0, 0.88, 0.80, 0.8), lw=2.0)
    brackets(bx, by, bw, bh, 14, (0.0, 0.88, 0.80, 1.0), 2.0)
    
    putc("INITIALIZING CELESTIAL DATA", ww // 2, by + 18, 1.4, (1.0, 0.72, 0.08, 1.0))
    putc(message.upper(), ww // 2, by + 45, 1.1, (0.0, 0.88, 0.80, 1.0))
    
    pbar_w = bw - 40
    pbar_h = 14
    px = bx + 20
    py = by + 75
    
    box(px, py, pbar_w, pbar_h, (0.0, 0.14, 0.12, 0.9))
    bdr(px, py, pbar_w, pbar_h, (0.0, 0.88, 0.80, 0.3))
    
    fill_w = int(pbar_w * progress_fraction)
    if fill_w > 0:
        box(px, py, fill_w, pbar_h, (0.20, 0.88, 0.48, 1.0))
        
    pct_text = f"{int(progress_fraction * 100)}%"
    putc(pct_text, ww // 2, py + 18, 1.1, (0.90, 0.92, 0.95, 1.0))
    
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    
    glfw.swap_buffers(win)
    glfw.poll_events()

def download_and_load_textures(win):
    global TEXTURES
    keys = list(TEXTURE_FILES.keys())
    total = len(keys)
    
    for i, key in enumerate(keys):
        fname, url = TEXTURE_FILES[key]
        local_path = os.path.join(TEXTURES_DIR, fname)
        
        draw_loading_screen(win, f"Loading: {key} texture...", i / total)
        
        if not os.path.exists(local_path):
            draw_loading_screen(win, f"Downloading: {key} texture...", i / total)
            try:
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(req) as response:
                    with open(local_path, 'wb') as out_file:
                        out_file.write(response.read())
            except Exception as e:
                print(f"Failed to download {key} from {url}: {e}")
                
        if os.path.exists(local_path):
            draw_loading_screen(win, f"Compiling: {key} shader...", (i + 0.5) / total)
            if key == "SaturnRings":
                TEXTURES[key] = load_ring_texture(local_path)
            else:
                TEXTURES[key] = load_texture(local_path)
        else:
            print(f"Skipping texture compilation for {key} (file missing)")
            
    draw_loading_screen(win, "Ready to launch simulation!", 1.0)
    _time.sleep(0.3)

# ═══════════════════════════════════════════════
# GLOBALS
# ═══════════════════════════════════════════════
cam_yaw   = 30.0
cam_pitch = -20.0
cam_dist  = 58.0
target_cam_dist = 58.0
focus_x = focus_y = focus_z = 0.0
prev_focus_idx = 3
transition_alpha = 1.0
last_mx = last_my = 0.0
mouse_down = False

time_scale     = 1.0
last_nz_speed  = 1.0
SPEED_MAX      = 20.0
slider_drag    = False
sldr_x = sldr_y = sldr_w = 0.0  # knob position for hit testing

cam_mode    = "Orbit"
focus_idx   = 3           # default = Earth
show_orbits = True
show_belt   = True
show_twink  = True
show_labels = True

ship_x, ship_y, ship_z = 0.0, 8.0, 40.0
radar_a   = 0.0
blink_on  = True
t_blink   = 0.0
t_start   = _time.time()

BTNS = []  # {id, x, y, w, h, hover}

# ═══════════════════════════════════════════════
# STAR FIELD
# ═══════════════════════════════════════════════
np.random.seed(42)
N_STARS = 900
_sth = np.random.uniform(0, 2*math.pi, N_STARS)
_sph = np.random.uniform(0, math.pi,   N_STARS)
_sr  = np.random.uniform(160, 200, N_STARS)
_sb  = np.random.uniform(0.35, 1.0, N_STARS)
SX = _sr * np.sin(_sph) * np.cos(_sth)
SY = _sr * np.sin(_sph) * np.sin(_sth)
SZ = _sr * np.cos(_sph)

# ═══════════════════════════════════════════════
# ASTEROID BELT
# ═══════════════════════════════════════════════
N_AST = 1100
AR    = np.random.uniform(26.5, 30.5, N_AST)
ASPD  = np.random.uniform(1.5,  2.5,  N_AST)
APH   = np.random.uniform(0,  360, N_AST)
ATLT  = np.random.uniform(-0.6, 0.6, N_AST)

# ═══════════════════════════════════════════════
# PLANETS
# (name, radius, orb_r, orb_spd, ax_spd, R, G, B, spec, shine, rings)
# ═══════════════════════════════════════════════
PLANETS = [
    ("Mercury", 0.38,  8.0, 4.74, 10,  0.62, 0.60, 0.58, 0.15, 8,   False,  7.00),
    ("Venus",   0.95, 12.0, 3.50,  6,  0.93, 0.78, 0.42, 0.4,  18,  False,  3.39),
    ("Earth",   1.00, 17.0, 2.98, 15,  0.22, 0.50, 0.88, 0.6,  45,  False,  0.00),
    ("Mars",    0.53, 23.0, 2.41, 14,  0.82, 0.32, 0.22, 0.25, 12,  False,  1.85),
    ("Jupiter", 2.60, 33.0, 1.31, 35,  0.82, 0.68, 0.46, 0.35, 18,  False,  1.30),
    ("Saturn",  2.20, 44.0, 0.97, 32,  0.96, 0.84, 0.58, 0.45, 22,  True,   2.49),
    ("Uranus",  1.40, 54.0, 0.68, 20,  0.58, 0.84, 0.96, 0.4,  20,  False,  0.77),
    ("Neptune", 1.35, 63.0, 0.54, 22,  0.18, 0.28, 0.88, 0.55, 28,  False,  1.77),
]

SCI = {
    "Sun":     {"kind":"G-TYPE STAR",     "temp":"5778 K",    "mass":"1.989e30 kg", "dist":"0.000 AU", "moons":"0",   "col":(1.00,0.86,0.35)},
    "Mercury": {"kind":"ROCKY PLANET",    "temp":"167 C",     "mass":"3.301e23 kg", "dist":"0.387 AU", "moons":"0",   "col":(0.62,0.60,0.58)},
    "Venus":   {"kind":"ROCKY PLANET",    "temp":"464 C",     "mass":"4.867e24 kg", "dist":"0.723 AU", "moons":"0",   "col":(0.93,0.78,0.42)},
    "Earth":   {"kind":"ROCKY PLANET",    "temp":"15 C",      "mass":"5.972e24 kg", "dist":"1.000 AU", "moons":"1",   "col":(0.22,0.50,0.88)},
    "Mars":    {"kind":"ROCKY PLANET",    "temp":"-65 C",     "mass":"6.417e23 kg", "dist":"1.524 AU", "moons":"2",   "col":(0.82,0.32,0.22)},
    "Jupiter": {"kind":"GAS GIANT",       "temp":"-108 C",    "mass":"1.898e27 kg", "dist":"5.203 AU", "moons":"95",  "col":(0.82,0.68,0.46)},
    "Saturn":  {"kind":"GAS GIANT",       "temp":"-139 C",    "mass":"5.683e26 kg", "dist":"9.537 AU", "moons":"146", "col":(0.96,0.84,0.58)},
    "Uranus":  {"kind":"ICE GIANT",       "temp":"-197 C",    "mass":"8.681e25 kg", "dist":"19.19 AU", "moons":"27",  "col":(0.58,0.84,0.96)},
    "Neptune": {"kind":"ICE GIANT",       "temp":"-201 C",    "mass":"1.024e26 kg", "dist":"30.07 AU", "moons":"16",  "col":(0.18,0.28,0.88)},
}

MOON_R = 0.27; MOON_ORB = 2.8; MOON_SPD = 13.0

# ═══════════════════════════════════════════════
# 5x7 PIXEL FONT — fixed-width, no overlap
# ═══════════════════════════════════════════════
F5 = {
    'A':["01110","10001","10001","11111","10001","10001","10001"],
    'B':["11110","10001","10001","11110","10001","10001","11110"],
    'C':["01111","10000","10000","10000","10000","10000","01111"],
    'D':["11110","10001","10001","10001","10001","10001","11110"],
    'E':["11111","10000","10000","11110","10000","10000","11111"],
    'F':["11111","10000","10000","11110","10000","10000","10000"],
    'G':["01111","10000","10000","10111","10001","10001","01110"],
    'H':["10001","10001","10001","11111","10001","10001","10001"],
    'I':["11111","00100","00100","00100","00100","00100","11111"],
    'J':["00111","00010","00010","00010","00010","10010","01100"],
    'K':["10001","10010","10100","11000","10100","10010","10001"],
    'L':["10000","10000","10000","10000","10000","10000","11111"],
    'M':["10001","11011","10101","10001","10001","10001","10001"],
    'N':["10001","11001","10101","10011","10001","10001","10001"],
    'O':["01110","10001","10001","10001","10001","10001","01110"],
    'P':["11110","10001","10001","11110","10000","10000","10000"],
    'Q':["01110","10001","10001","10001","10101","10010","01101"],
    'R':["11110","10001","10001","11110","10100","10010","10001"],
    'S':["01111","10000","10000","01110","00001","00001","11110"],
    'T':["11111","00100","00100","00100","00100","00100","00100"],
    'U':["10001","10001","10001","10001","10001","10001","01110"],
    'V':["10001","10001","10001","10001","01010","01010","00100"],
    'W':["10001","10001","10001","10101","10101","11011","10001"],
    'X':["10001","01010","01010","00100","01010","01010","10001"],
    'Y':["10001","10001","01010","00100","00100","00100","00100"],
    'Z':["11111","00001","00010","00100","01000","10000","11111"],
    '0':["01110","10011","10101","10101","11001","10001","01110"],
    '1':["00100","01100","00100","00100","00100","00100","01110"],
    '2':["01110","10001","00001","00110","01100","10000","11111"],
    '3':["11110","00001","00001","01110","00001","00001","11110"],
    '4':["00010","00110","01010","10010","11111","00010","00010"],
    '5':["11111","10000","10000","11110","00001","00001","11110"],
    '6':["00110","01000","10000","11110","10001","10001","01110"],
    '7':["11111","00001","00010","00100","00100","00100","00100"],
    '8':["01110","10001","10001","01110","10001","10001","01110"],
    '9':["01110","10001","10001","01111","00001","00001","01110"],
    '.':["00000","00000","00000","00000","00000","01100","01100"],
    ':':["01100","01100","00000","00000","01100","01100","00000"],
    '-':["00000","00000","00000","11111","00000","00000","00000"],
    '/':["00001","00010","00010","00100","01000","01000","10000"],
    '+':["00000","00100","00100","11111","00100","00100","00000"],
    '=':["00000","11111","00000","00000","11111","00000","00000"],
    ' ':["00000","00000","00000","00000","00000","00000","00000"],
    '%':["11000","11001","00010","00100","01000","10011","00011"],
    '!':["00100","00100","00100","00100","00100","00000","00100"],
    '[':["01100","01000","01000","01000","01000","01000","01100"],
    ']':["00110","00010","00010","00010","00010","00010","00110"],
    '>':["10000","01000","00100","00010","00100","01000","10000"],
    '<':["00001","00010","00100","01000","00100","00010","00001"],
    '#':["01010","01010","11111","01010","11111","01010","01010"],
}

def _char(x, y, c, sc, col):
    rows = F5.get(c.upper() if c.upper() in F5 else c, F5[' '])
    glColor4f(*col)
    for ri, bits in enumerate(rows):
        for ci, px in enumerate(bits):
            if px == '1':
                x0 = x + ci*sc; y0 = y + ri*sc
                glBegin(GL_QUADS)
                glVertex2f(x0,    y0);    glVertex2f(x0+sc, y0)
                glVertex2f(x0+sc, y0+sc); glVertex2f(x0,   y0+sc)
                glEnd()

def put(s, x, y, sc=1.5, col=(0.0, 0.88, 0.80, 1.0)):
    """Left-anchored text. Returns end X."""
    cx = float(x)
    for c in str(s):
        _char(cx, y, c, sc, col)
        cx += 6.0*sc
    return cx

def putc(s, cx, y, sc=1.5, col=(0.0, 0.88, 0.80, 1.0)):
    """Center-anchored text."""
    w = len(str(s)) * 6.0 * sc
    put(s, cx - w/2.0, y, sc, col)

def putr(s, rx, y, sc=1.5, col=(0.0, 0.88, 0.80, 1.0)):
    """Right-anchored text."""
    w = len(str(s)) * 6.0 * sc
    put(s, rx - w, y, sc, col)

def tw(s, sc=1.5):  return len(str(s)) * 6.0 * sc
def th(sc=1.5):     return 7.0 * sc

# ═══════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════
CYAN   = (0.00, 0.88, 0.80, 1.0)
CYAN_F = (0.00, 0.88, 0.80, 0.15)
CYAN_B = (0.00, 0.88, 0.80, 0.30)
AMBER  = (1.00, 0.72, 0.08, 1.0)
AMBER_F= (1.00, 0.72, 0.08, 0.18)
GREEN  = (0.20, 0.88, 0.48, 1.0)
GREEN_F= (0.20, 0.88, 0.48, 0.12)
RED    = (1.00, 0.24, 0.24, 1.0)
RED_F  = (1.00, 0.24, 0.24, 0.16)
DIM    = (0.28, 0.52, 0.52, 1.0)
WHITE  = (0.90, 0.92, 0.95, 1.0)
PBKG   = (0.00, 0.03, 0.07, 0.91)
PBKG2  = (0.00, 0.04, 0.09, 0.80)

# ═══════════════════════════════════════════════
# 2D DRAW HELPERS
# ═══════════════════════════════════════════════
def box(x, y, w, h, col):
    glColor4f(*col)
    glBegin(GL_QUADS)
    glVertex2f(x,   y);   glVertex2f(x+w, y)
    glVertex2f(x+w, y+h); glVertex2f(x,   y+h)
    glEnd()

def bdr(x, y, w, h, col, lw=1.0):
    glColor4f(*col); glLineWidth(lw)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x,   y);   glVertex2f(x+w, y)
    glVertex2f(x+w, y+h); glVertex2f(x,   y+h)
    glEnd(); glLineWidth(1.0)

def hln(x, y, w, col, lw=1.0):
    glColor4f(*col); glLineWidth(lw)
    glBegin(GL_LINES); glVertex2f(x,y); glVertex2f(x+w,y); glEnd()
    glLineWidth(1.0)

def dot_grid(x, y, w, h, sp, col):
    glColor4f(*col); glPointSize(1.5)
    glBegin(GL_POINTS)
    gx = x + sp
    while gx < x+w:
        gy = y + sp
        while gy < y+h:
            glVertex2f(gx, gy); gy += sp
        gx += sp
    glEnd(); glPointSize(1.0)

def circ2d(cx, cy, r, col, filled=False, n=40):
    glColor4f(*col)
    glBegin(GL_TRIANGLE_FAN if filled else GL_LINE_LOOP)
    if filled: glVertex2f(cx, cy)
    for i in range(n):
        a = 2*math.pi*i/n
        glVertex2f(cx + math.cos(a)*r, cy + math.sin(a)*r)
    glEnd()

def arc2d(cx, cy, r, a0, a1, col, lw=1.0, n=32):
    glColor4f(*col); glLineWidth(lw)
    glBegin(GL_LINE_STRIP)
    for i in range(n+1):
        a = a0 + (a1-a0)*i/n
        glVertex2f(cx+math.cos(a)*r, cy+math.sin(a)*r)
    glEnd(); glLineWidth(1.0)

def chamfer(x, y, w, h, c=8, fill=None, border=None, lw=1.2):
    pts = [(x+c,y),(x+w-c,y),(x+w,y+c),(x+w,y+h-c),
           (x+w-c,y+h),(x+c,y+h),(x,y+h-c),(x,y+c)]
    if fill:
        glColor4f(*fill)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x+w/2, y+h/2)
        for px,py in pts: glVertex2f(px,py)
        glVertex2f(pts[0][0],pts[0][1])
        glEnd()
    if border:
        glColor4f(*border); glLineWidth(lw)
        glBegin(GL_LINE_LOOP)
        for px,py in pts: glVertex2f(px,py)
        glEnd(); glLineWidth(1.0)

def brackets(x, y, w, h, sz=14, col=None, lw=1.8):
    col = col or CYAN
    glColor4f(*col); glLineWidth(lw)
    for pts in [
        [(x,y+sz),(x,y),(x+sz,y)],
        [(x+w-sz,y),(x+w,y),(x+w,y+sz)],
        [(x,y+h-sz),(x,y+h),(x+sz,y+h)],
        [(x+w-sz,y+h),(x+w,y+h),(x+w,y+h-sz)],
    ]:
        glBegin(GL_LINE_STRIP)
        for px,py in pts: glVertex2f(px,py)
        glEnd()
    glLineWidth(1.0)

def sec_hdr(x, y, w, label):
    """[> LABEL ─────────] divider, returns new y."""
    sc = 1.2
    put("[>", x, y, sc, CYAN)
    ex = put(" " + label + " ", x + tw("[>",sc), y, sc, AMBER)
    hln(ex, y + th(sc)/2, (x+w) - ex - tw("]",sc), CYAN_B)
    put("]", x+w-tw("]",sc), y, sc, CYAN)
    return int(y + th(sc) + 6)

def row(x, y, w, label, val, lc=None, vc=None, sc=1.3):
    lc = lc or DIM; vc = vc or CYAN
    put(label, x, y, sc, lc)
    putr(val, x+w, y, sc, vc)
    return int(y + th(sc) + 4)

# ═══════════════════════════════════════════════
# BUTTON
# ═══════════════════════════════════════════════
def _active(bid):
    if bid=="mode_orbit":  return cam_mode=="Orbit"
    if bid=="mode_fly":    return cam_mode=="FreeFly"
    if bid=="tog_orbits":  return show_orbits
    if bid=="tog_belt":    return show_belt
    if bid=="tog_twink":   return show_twink
    if bid=="tog_labels":  return show_labels
    if bid=="play_pause":  return time_scale > 0
    if bid.startswith("focus_"): return focus_idx==int(bid[6:]) and cam_mode=="Orbit"
    return False

def btn(bid, label, x, y, w, h):
    active = _active(bid)
    hover  = next((b["hover"] for b in BTNS if b["id"]==bid), False)
    c8 = 6
    if active:
        chamfer(x,y,w,h,c8, fill=CYAN_F, border=CYAN, lw=1.6)
        tc = AMBER
    elif hover:
        chamfer(x,y,w,h,c8, fill=(*CYAN[:3],0.08), border=(*CYAN[:3],0.5))
        tc = CYAN
    else:
        chamfer(x,y,w,h,c8, fill=PBKG2, border=(*DIM[:3],0.5))
        tc = DIM
    sc = 1.2
    putc(label, x+w/2, y+(h-th(sc))/2, sc, tc)
    BTNS.append({"id":bid,"x":x,"y":y,"w":w,"h":h,"hover":hover})

def get_body_position(idx, t):
    if idx == 0:
        return (0.0, 0.0, 0.0)
    p = PLANETS[idx - 1]
    orb_r = p[2]
    ospd = p[3]
    incl = p[11]
    oa = math.radians((ospd * t) % 360)
    
    x = math.cos(oa) * orb_r
    z = math.sin(oa) * orb_r
    
    incl_rad = math.radians(incl)
    y_tilted = -z * math.sin(incl_rad)
    z_tilted = z * math.cos(incl_rad)
    
    return (x, y_tilted, z_tilted)

def get_default_dist(idx):
    if idx == 0: return 58.0
    rad = PLANETS[idx-1][1]
    if idx == 6: # Saturn
        return rad * 16.0
    return rad * 14.0

def _click(bid):
    global cam_mode,focus_idx,show_orbits,show_belt,show_twink
    global show_labels,time_scale,last_nz_speed
    global prev_focus_idx, transition_alpha, target_cam_dist
    if   bid=="mode_orbit":  cam_mode="Orbit"
    elif bid=="mode_fly":    cam_mode="FreeFly"
    elif bid=="tog_orbits":  show_orbits = not show_orbits
    elif bid=="tog_belt":    show_belt   = not show_belt
    elif bid=="tog_twink":   show_twink  = not show_twink
    elif bid=="tog_labels":  show_labels = not show_labels
    elif bid=="play_pause":
        if time_scale==0: time_scale=last_nz_speed
        else: last_nz_speed=time_scale; time_scale=0.0
    elif bid.startswith("focus_"):
        new_idx = int(bid[6:])
        if new_idx != focus_idx:
            prev_focus_idx = focus_idx
            focus_idx = new_idx
            transition_alpha = 0.0
            target_cam_dist = get_default_dist(focus_idx)
            cam_mode = "Orbit"

def _fname():
    return "Sun" if focus_idx==0 else PLANETS[focus_idx-1][0]

def _fpos(st):
    return get_body_position(focus_idx, st)

def _clock():
    el=_time.time()-t_start
    return "T+%02d:%02d:%02d" % (int(el//3600), int((el%3600)//60), int(el%60))

# ═══════════════════════════════════════════════
# 3D BILLBOARD LABEL  (small, not overlapping)
# ═══════════════════════════════════════════════
def label3d(text, wx, wy, wz):
    """Draw a small billboard label in 3D. Scale is FIXED = 0.09."""
    SC = 0.09
    glPushMatrix()
    glTranslatef(wx, wy, wz)
    mv = glGetFloatv(GL_MODELVIEW_MATRIX)
    # Neutralize rotation (billboard)
    for i in range(3):
        for j in range(3):
            mv[i][j] = 1.0 if i==j else 0.0
    glLoadMatrixf(mv)
    glDisable(GL_LIGHTING)
    total_w = len(text)*6*SC
    ox = -total_w/2.0
    glColor4f(0.0, 0.88, 0.80, 0.95)
    for c in text:
        rows = F5.get(c.upper() if c.upper() in F5 else c, F5[' '])
        for ri, bits in enumerate(rows):
            for ci, px in enumerate(bits):
                if px=='1':
                    x0=ox+ci*SC; y0=ri*SC
                    glBegin(GL_QUADS)
                    glVertex3f(x0,       -y0,        0)
                    glVertex3f(x0+SC,    -y0,        0)
                    glVertex3f(x0+SC,    -(y0+SC),   0)
                    glVertex3f(x0,       -(y0+SC),   0)
                    glEnd()
        ox += 6*SC
    glEnable(GL_LIGHTING)
    glPopMatrix()

# ═══════════════════════════════════════════════
# 3D GEOMETRY
# ═══════════════════════════════════════════════
def mat3(r, g, b, sp, sh, a=1.0):
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [r,g,b,a])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,            [sp,sp,sp,a])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS,           sh)
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION,            [0,0,0,a])

def sph(r, sl=48, st=48):
    q=gluNewQuadric(); gluQuadricNormals(q,GLU_SMOOTH)
    gluSphere(q,r,sl,st); gluDeleteQuadric(q)

def orb_ring(r, incl=0.0, n=120):
    glPushMatrix()
    glRotatef(incl, 1.0, 0.0, 0.0)
    glBegin(GL_LINE_LOOP)
    for i in range(n):
        a=2*math.pi*i/n; glVertex3f(math.cos(a)*r, 0, math.sin(a)*r)
    glEnd()
    glPopMatrix()

def sat_rings(ri, ro, n=64):
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(n+1):
        a=2*math.pi*i/n; c,s=math.cos(a),math.sin(a)
        glNormal3f(0,1,0)
        glVertex3f(c*ro,0,s*ro); glVertex3f(c*ri,0,s*ri)
    glEnd()

def sat_rings_textured(ri, ro, n=64):
    glBegin(GL_TRIANGLE_STRIP)
    for i in range(n+1):
        a = 2 * math.pi * i / n
        c, s = math.cos(a), math.sin(a)
        glNormal3f(0, 1, 0)
        glTexCoord2f(1.0, 0.5)
        glVertex3f(c * ro, 0, s * ro)
        glTexCoord2f(0.0, 0.5)
        glVertex3f(c * ri, 0, s * ri)
    glEnd()

def draw_stars(t):
    glDisable(GL_LIGHTING); glPointSize(1.8)
    glBegin(GL_POINTS)
    for i in range(N_STARS):
        b = _sb[i]
        if show_twink: b *= 0.55 + 0.45*math.sin(t*3.5+i*2.1)
        glColor4f(b*0.72, b*0.85, b, 1.0)
        glVertex3f(SX[i],SY[i],SZ[i])
    glEnd(); glPointSize(1.0); glEnable(GL_LIGHTING)

def draw_background_skybox(texture_id, cx, cy, cz):
    if texture_id is None:
        return
    glDisable(GL_LIGHTING)
    glDepthMask(GL_FALSE)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(cx, cy, cz)
    glRotatef(20.0, 1, 0, 0)
    glRotatef(_time.time() * 0.02, 0, 1, 0)
    
    q = gluNewQuadric()
    gluQuadricTexture(q, GL_TRUE)
    gluQuadricOrientation(q, GLU_INSIDE)
    gluSphere(q, 380.0, 32, 32)
    gluDeleteQuadric(q)
    
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)
    glDepthMask(GL_TRUE)
    glEnable(GL_LIGHTING)

def draw_sun():
    glDisable(GL_LIGHTING)
    glDepthMask(GL_FALSE) # Disable depth buffer writes for glow spheres!
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE) # Additive blending
    
    # Draw glowing atmosphere layers (bright yellow-orange)
    glColor4f(1.0, 0.50, 0.0, 0.15); sph(5.5)
    glColor4f(1.0, 0.70, 0.12, 0.20); sph(4.6)
    glColor4f(1.0, 0.85, 0.28, 0.25); sph(4.0)
    
    glDepthMask(GL_TRUE) # Re-enable depth writing
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # Normal blending
    glDisable(GL_BLEND)
    
    tex_id = TEXTURES.get("Sun")
    if tex_id is not None:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        q = gluNewQuadric()
        gluQuadricNormals(q, GLU_SMOOTH)
        gluQuadricTexture(q, GL_TRUE)
        gluSphere(q, 3.5, 48, 48)
        gluDeleteQuadric(q)
        glDisable(GL_TEXTURE_2D)
    else:
        glColor3f(1.0,0.94,0.46); sph(3.5)
    glEnable(GL_LIGHTING)

def draw_planet(p, t):
    nm,rad,orb,ospd,axspd,r,g,b,sp,sh,rings,incl = p
    ox, oy, oz = get_body_position(PLANETS.index(p) + 1, t)
    glPushMatrix()
    glTranslatef(ox, oy, oz)
    glRotatef((axspd*t)%360, 0, 1, 0)
    
    tex_id = TEXTURES.get(nm)
    if tex_id is not None:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [sp, sp, sp, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, sh)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        
        q = gluNewQuadric()
        gluQuadricNormals(q, GLU_SMOOTH)
        gluQuadricTexture(q, GL_TRUE)
        gluSphere(q, rad, 48, 48)
        gluDeleteQuadric(q)
        glDisable(GL_TEXTURE_2D)
    else:
        mat3(r, g, b, sp, sh)
        sph(rad)
        
    if rings:
        glRotatef(27, 1, 0, 0)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        ring_tex = TEXTURES.get("SaturnRings")
        if ring_tex is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, ring_tex)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0, 0.85])
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 5)
            glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 0.0, 0.0, 0.0])
            sat_rings_textured(rad*1.32, rad*2.20)
            glDisable(GL_TEXTURE_2D)
        else:
            mat3(0.92, 0.80, 0.58, 0.1, 5, 0.55)
            sat_rings(rad*1.32, rad*2.20)
        glDisable(GL_BLEND)
    glPopMatrix()
    return ox, oy, oz

def draw_moon(eox, eoy, eoz, t):
    ma=math.radians((MOON_SPD*t)%360)
    mx=eox+math.cos(ma)*MOON_ORB
    my=eoy
    mz=eoz+math.sin(ma)*MOON_ORB
    glPushMatrix(); glTranslatef(mx,my,mz)
    
    tex_id = TEXTURES.get("Moon")
    if tex_id is not None:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 5)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        
        q = gluNewQuadric()
        gluQuadricNormals(q, GLU_SMOOTH)
        gluQuadricTexture(q, GL_TRUE)
        gluSphere(q, MOON_R, 24, 24)
        gluDeleteQuadric(q)
        glDisable(GL_TEXTURE_2D)
    else:
        mat3(0.72,0.72,0.72,0.1,5)
        sph(MOON_R)
        
    glPopMatrix()
    if show_orbits:
        glDisable(GL_LIGHTING)
        glColor4f(0.4,0.4,0.55,0.18)
        glPushMatrix()
        glTranslatef(eox,eoy,eoz)
        p_earth = PLANETS[2]
        glRotatef(p_earth[11], 1.0, 0.0, 0.0)
        orb_ring(MOON_ORB)
        glPopMatrix()
        glEnable(GL_LIGHTING)
    return mx, my, mz

def draw_orbits():
    if not show_orbits: return
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    for p in PLANETS:
        r, g, b = p[5], p[6], p[7]
        glColor4f(r, g, b, 0.28)
        orb_ring(p[2], p[11])
    glDisable(GL_BLEND); glEnable(GL_LIGHTING)

def draw_belt(t):
    if not show_belt: return
    glDisable(GL_LIGHTING); glPointSize(1.8)
    glColor4f(0.50, 0.46, 0.42, 0.60)
    glBegin(GL_POINTS)
    for i in range(N_AST):
        a=math.radians(APH[i]+ASPD[i]*t)
        glVertex3f(math.cos(a)*AR[i], ATLT[i], math.sin(a)*AR[i])
    glEnd(); glPointSize(1.0); glEnable(GL_LIGHTING)

def draw_ship():
    glPushMatrix(); glTranslatef(ship_x,ship_y,ship_z)
    glRotatef(cam_yaw,0,1,0); glRotatef(-cam_pitch,1,0,0)
    glDisable(GL_COLOR_MATERIAL)
    mat3(0.80,0.84,0.90,0.9,72)
    glBegin(GL_TRIANGLES)
    glVertex3f(0,0,-2);    glVertex3f(-0.5,-0.2,0.3); glVertex3f(0.5,-0.2,0.3)
    glVertex3f(0,0,-2);    glVertex3f(-0.5,-0.2,0.3); glVertex3f(0,0.45,0.3)
    glVertex3f(0,0,-2);    glVertex3f(0,0.45,0.3);    glVertex3f(0.5,-0.2,0.3)
    glVertex3f(-0.5,-0.2,0.3); glVertex3f(-2.5,-0.5,1.4); glVertex3f(-0.5,-0.2,1.2)
    glVertex3f(0.5,-0.2,0.3);  glVertex3f(0.5,-0.2,1.2);  glVertex3f(2.5,-0.5,1.4)
    glVertex3f(0,0.45,0.3); glVertex3f(0,0.45,1.2); glVertex3f(0,1.6,1.2)
    glEnd()
    mat3(0.12,0.52,0.96,1.0,95)
    glBegin(GL_TRIANGLES)
    glVertex3f(0,0.22,-0.5); glVertex3f(-0.38,-0.05,0.15); glVertex3f(0.38,-0.05,0.15)
    glEnd()
    # Engine glow
    glMaterialfv(GL_FRONT_AND_BACK,GL_EMISSION,[1.0,0.45,0.0,1.0])
    glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT_AND_DIFFUSE,[1.0,0.45,0.0,1.0])
    glBegin(GL_TRIANGLE_FAN); glVertex3f(0,0,1.2)
    for i in range(10):
        a=2*math.pi*i/9; glVertex3f(math.cos(a)*0.3,math.sin(a)*0.3,2.4)
    glEnd()
    glEnable(GL_COLOR_MATERIAL); glPopMatrix()

# ═══════════════════════════════════════════════════════════════
# HUD — NASA MISSION CONTROL LAYOUT
# 
# ┌─────────────────── TOP BAR ───────────────────────────┐
# │[WSB MERITO WROCLAW]  SOLAR SYSTEM MISSION CONTROL  T+..│
# ├──────────┬──────────────────────────┬──────────────────┤
# │          │   [TRACKING: ...]        │                  │
# │  LEFT    │                          │  RIGHT           │
# │  PANEL   │   (3D viewport)          │  PANEL           │
# │  telemetry│                         │  controls        │
# │          │                          │                  │
# │  radar   │                          │                  │
# ├──────────┴──────────────────────────┴──────────────────┤
# │ SYS STATUS BAR                                         │
# └────────────────────────────────────────────────────────┘
# ═══════════════════════════════════════════════════════════════
def draw_hud(ww, wh, sim_t, real_t):
    global BTNS, blink_on, t_blink, radar_a
    global sldr_x, sldr_y, sldr_w

    if ww<=0 or wh<=0: return

    # Blink toggle
    if real_t - t_blink > 0.5:
        blink_on = not blink_on; t_blink = real_t

    radar_a = (radar_a + 0.7) % 360.0

    old_h = {b["id"]:b["hover"] for b in BTNS}
    BTNS.clear()

    # ── Enter 2D ─────────────────────────────
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(0, ww, wh, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH); glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    # ╔═══════════════════════════════════════╗
    # ║  TOP BAR                             ║
    # ╚═══════════════════════════════════════╝
    TH = 34
    box(0, 0, ww, TH, PBKG)
    hln(0, TH, ww, CYAN_B, 1.5)
    # Left tag
    put("[WSB MERITO WROCLAW]", 12, (TH-th(1.3))/2, 1.3, DIM)
    # Center title
    putc("SOLAR SYSTEM MISSION CONTROL", ww/2, (TH-th(1.5))/2, 1.5, CYAN)
    # Right: speed + clock
    clk = _clock()
    spd = "PAUSED" if time_scale==0 else ("x%.1f" % time_scale)
    sp_c = (RED if not blink_on else DIM) if time_scale==0 else GREEN
    putr(clk, ww-12-tw(spd,1.4)-10, (TH-th(1.4))/2, 1.4, AMBER)
    putr(spd, ww-12, (TH-th(1.4))/2, 1.4, sp_c)

    # ╔═══════════════════════════════════════╗
    # ║  BOTTOM STATUS BAR                   ║
    # ╚═══════════════════════════════════════╝
    BH = 26; by0 = wh - BH
    box(0, by0, ww, BH, PBKG)
    hln(0, by0, ww, CYAN_B, 1.2)
    statuses = [
        ("PROPULSION",   GREEN),("NAVIGATION",  GREEN),("TELEMETRY",  GREEN),
        ("RADAR",        GREEN),("ORBIT CALC",  AMBER),("SYS NOMINAL",GREEN),
    ]
    bx = 12
    for lbl, c in statuses:
        dc = c if blink_on else (*c[:3], 0.28)
        circ2d(bx+4, by0+BH/2, 4, dc, True)
        ex = put(lbl, bx+12, by0+(BH-th(1.2))/2, 1.2, DIM)
        bx = ex + 20
    putr("MODE: "+cam_mode.upper(), ww-12, by0+(BH-th(1.3))/2, 1.3, CYAN)

    # ╔═══════════════════════════════════════╗
    # ║  LEFT PANEL  — Telemetry             ║
    # ╚═══════════════════════════════════════╝
    PW = 245; PH = wh - TH - BH - 18
    LX = 10; LY = TH + 9

    box(LX, LY, PW, PH, PBKG)
    dot_grid(LX, LY, PW, PH, 20, (0, 0.5, 0.45, 0.05))
    bdr(LX, LY, PW, PH, CYAN_B, 1.0)
    brackets(LX, LY, PW, PH, 14, CYAN, 1.8)

    PAD = 12; IW = PW - PAD*2
    tx = LX + PAD; ty = LY + PAD

    ty = sec_hdr(tx, ty, IW, "ORBITAL TELEMETRY")

    fname = _fname()
    sci   = SCI.get(fname, {})
    dc    = sci.get("col", (1,1,1))

    # Planet name with color indicator dot
    circ2d(tx+6, ty+8, 7, (*dc,1.0), True)
    circ2d(tx+6, ty+8, 7, (*dc,0.5), False)
    put(fname.upper(), tx+18, ty, 2.0, CYAN)
    ty += int(th(2.0)) + 3
    put(sci.get("kind","UNKNOWN"), tx+18, ty, 1.2, DIM)
    ty += int(th(1.2)) + 8

    hln(tx, ty, IW, CYAN_B); ty += 8

    ty = sec_hdr(tx, ty, IW, "POSITION")
    pos = _fpos(sim_t)
    ty = row(tx, ty, IW, "X AXIS", "%+9.3f AU"%pos[0], DIM, CYAN)
    ty = row(tx, ty, IW, "Y AXIS", "%+9.3f AU"%pos[1], DIM, CYAN)
    ty = row(tx, ty, IW, "Z AXIS", "%+9.3f AU"%pos[2], DIM, CYAN)
    dist = math.sqrt(sum(v**2 for v in pos))
    ty = row(tx, ty, IW, "DIST SUN", "%.3f AU"%dist, DIM, AMBER)
    ty += 4; hln(tx,ty,IW,CYAN_B); ty += 8

    ty = sec_hdr(tx, ty, IW, "OBJECT DATA")
    ty = row(tx, ty, IW, "TEMP",    sci.get("temp","N/A"),  DIM, AMBER)
    ty = row(tx, ty, IW, "MASS",    sci.get("mass","N/A"),  DIM, CYAN)
    ty = row(tx, ty, IW, "DIST",    sci.get("dist","N/A"),  DIM, CYAN)
    ty = row(tx, ty, IW, "MOONS",   sci.get("moons","N/A"), DIM, GREEN)
    if focus_idx>0:
        p = PLANETS[focus_idx-1]
        ty = row(tx, ty, IW, "ORB ANG", "%.1f DEG"%((p[3]*sim_t)%360), DIM, CYAN)
        ty = row(tx, ty, IW, "ORB SPD", "%.2f DEG/S"%p[3], DIM, CYAN)

    ty += 4; hln(tx,ty,IW,CYAN_B); ty+=8

    # Orbit progress arc
    if focus_idx>0:
        p = PLANETS[focus_idx-1]
        frac = ((p[3]*sim_t)%360)/360.0
        acx = tx + IW//2; acy = ty + 30; ar = 26
        circ2d(acx, acy, ar, (0,0.4,0.35,0.25), True)
        circ2d(acx, acy, ar, CYAN_B, False)
        if frac>0.002:
            arc2d(acx, acy, ar, -math.pi/2, -math.pi/2+2*math.pi*frac, CYAN, 2.5)
        pct = "%d%%"%int(frac*100)
        putc(pct, acx, acy-th(1.2)/2, 1.2, AMBER)
        putc("ORBIT", acx, acy+th(1.2)/2+2, 1.0, DIM)
        ty += 66

    hln(tx,ty,IW,CYAN_B); ty+=8

    # ── Tactical Radar ─────────────────────
    rem_h = (LY + PH) - ty - 16
    RR = min(rem_h//2 - 10, IW//2 - 10)
    if RR > 30:
        ty2 = sec_hdr(tx, ty, IW, "TACTICAL RADAR")
        rcx = tx + IW//2; rcy = ty2 + RR + 4

        circ2d(rcx, rcy, RR+6, (0,0,0,0.8), True)
        circ2d(rcx, rcy, RR+6, CYAN_B, False)

        farthest = PLANETS[-1][2]
        for p in PLANETS:
            sc = p[2]/farthest*RR
            circ2d(rcx, rcy, sc, (0.12,0.38,0.32,0.28), False)

        glColor4f(0.10,0.32,0.28,0.35)
        glBegin(GL_LINES)
        glVertex2f(rcx-RR,rcy); glVertex2f(rcx+RR,rcy)
        glVertex2f(rcx,rcy-RR); glVertex2f(rcx,rcy+RR)
        glEnd()

        # Sweep
        sa = math.radians(-radar_a)
        for i in range(36):
            frac = i/36
            a0 = sa - math.radians(55*(1-frac))
            a1 = sa - math.radians(55*(1-(i+1)/36))
            glColor4f(0.12, 0.9, 0.45, frac*0.26)
            glBegin(GL_TRIANGLES)
            glVertex2f(rcx, rcy)
            glVertex2f(rcx+math.cos(a0)*RR, rcy+math.sin(a0)*RR)
            glVertex2f(rcx+math.cos(a1)*RR, rcy+math.sin(a1)*RR)
            glEnd()
        glLineWidth(1.8); glColor4f(*GREEN)
        glBegin(GL_LINES)
        glVertex2f(rcx, rcy)
        glVertex2f(rcx+math.cos(sa)*RR, rcy+math.sin(sa)*RR)
        glEnd(); glLineWidth(1.0)

        for i,p in enumerate(PLANETS):
            oa = math.radians((p[3]*sim_t)%360)
            sc = p[2]/farthest*RR
            bx2=rcx+math.cos(oa)*sc; by2=rcy+math.sin(oa)*sc
            circ2d(bx2, by2, 3.5, (*SCI[p[0]]["col"],1.0), True)
            if i==focus_idx-1 and cam_mode=="Orbit":
                glLineWidth(1.8); circ2d(bx2,by2,7,CYAN,False); glLineWidth(1.0)

        circ2d(rcx,rcy,5,(1.0,0.92,0.40,1.0),True)
        circ2d(rcx,rcy,7,(1.0,0.92,0.40,0.4),False)

    # ╔═══════════════════════════════════════╗
    # ║  CENTER TOP — tracking strip         ║
    # ╚═══════════════════════════════════════╝
    CX = LX + PW + 10; CW = ww - PW*2 - 40
    if CW > 120:
        CTH = 46
        box(CX, LY, CW, CTH, PBKG)
        bdr(CX, LY, CW, CTH, CYAN_B, 1.0)
        brackets(CX, LY, CW, CTH, 10, CYAN, 1.5)
        putc("TRACKING: "+fname.upper(), CX+CW/2, LY+7, 1.5, CYAN)
        pos2 = _fpos(sim_t)
        info = "X:%+.1f  Y:%+.1f  Z:%+.1f  AU" % pos2
        putc(info, CX+CW/2, LY+7+th(1.5)+4, 1.2, DIM)

    # ╔═══════════════════════════════════════╗
    # ║  RIGHT PANEL — Controls              ║
    # ╚═══════════════════════════════════════╝
    RX = ww - PW - 10; RY = LY

    box(RX, RY, PW, PH, PBKG)
    dot_grid(RX, RY, PW, PH, 20, (0,0.5,0.45,0.05))
    bdr(RX, RY, PW, PH, CYAN_B, 1.0)
    brackets(RX, RY, PW, PH, 14, CYAN, 1.8)

    rx = RX + PAD; ry = RY + PAD

    ry = sec_hdr(rx, ry, IW, "NAVIGATION CTRL")
    bw = (IW-8)//2
    btn("mode_orbit","ORBIT MODE", rx,      ry, bw, 26)
    btn("mode_fly",  "FREE FLY",   rx+bw+8, ry, bw, 26)
    ry += 34; hln(rx,ry,IW,CYAN_B); ry+=8

    ry = sec_hdr(rx, ry, IW, "VISUAL SYSTEMS")
    togs = [("tog_orbits","ORBIT RINGS"),("tog_belt","ASTEROID BELT"),
            ("tog_twink","STAR TWINKLE"),("tog_labels","PLANET LABELS")]
    for tid, tlbl in togs:
        ac = _active(tid)
        dc2 = (GREEN if ac and blink_on else (*GREEN[:3],0.3) if ac else (*DIM[:3],0.5))
        circ2d(rx+6, ry+11, 4, dc2, True)
        btn(tid, tlbl, rx+16, ry, IW-16, 22)
        ry += 28
    ry += 2; hln(rx,ry,IW,CYAN_B); ry+=8

    ry = sec_hdr(rx, ry, IW, "SIMULATION SPEED")
    spd_s = "ENGINES OFFLINE" if time_scale==0 else ("TIME WARP  x%.1f" % time_scale)
    sp_col = (RED if not blink_on else (*RED[:3],0.3)) if time_scale==0 else AMBER
    putc(spd_s, rx+IW//2, ry, 1.3, sp_col); ry += int(th(1.3))+6

    # Slider track
    sly = ry+4; slw = IW; slx = rx
    t_frac = max(0.0,min(1.0,time_scale/max(SPEED_MAX,1)))
    kx = slx+slw*t_frac; ky = sly+4

    box(slx,sly,slw,8,(0,0.14,0.12,0.9))
    bdr(slx,sly,slw,8,(*CYAN[:3],0.25))
    if t_frac>0.002:
        box(slx,sly,slw*t_frac,8,(*GREEN[:3],0.55))
    for v in [2,5,10,15,20]:
        nx = slx + slw*(v/SPEED_MAX)
        glColor4f(*CYAN_B); glLineWidth(1.0)
        glBegin(GL_LINES); glVertex2f(nx,sly-2); glVertex2f(nx,sly+10); glEnd()
    circ2d(kx,ky,9,PBKG,True)
    glLineWidth(2.0); circ2d(kx,ky,9,CYAN,False); glLineWidth(1.0)
    circ2d(kx,ky,4,CYAN,True)
    sldr_x=slx; sldr_y=ky; sldr_w=slw
    ry += 18
    for v,lbl in [(0,"0"),(5,"5x"),(10,"10x"),(20,"20x")]:
        nx = slx + slw*(v/SPEED_MAX)
        putc(lbl, nx, ry, 1.1, DIM)
    ry += int(th(1.1))+8

    # Play/Pause
    pp_lbl = "PAUSE SIMULATION" if time_scale>0 else "RESUME SIMULATION"
    pp_col = RED if time_scale>0 else GREEN
    pp_f   = (*pp_col[:3],0.20)
    chamfer(rx,ry,IW,28,8,fill=pp_f,border=(*pp_col[:3],0.85),lw=1.6)
    putc(pp_lbl, rx+IW//2, ry+(28-th(1.3))/2, 1.3, pp_col)
    BTNS.append({"id":"play_pause","x":rx,"y":ry,"w":IW,"h":28,
                 "hover":next((b["hover"] for b in BTNS if b["id"]=="play_pause"),False)})
    ry += 36; hln(rx,ry,IW,CYAN_B); ry+=8

    ry = sec_hdr(rx, ry, IW, "TARGET SELECTION")
    targets=["Sun","Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus","Neptune"]
    cw2=(IW-8)//2
    for i,tn in enumerate(targets):
        bx2=rx+(i%2)*(cw2+8); by2=ry+(i//2)*28
        tc = SCI.get(tn,{}).get("col",(0.5,0.5,0.5))
        circ2d(bx2+5, by2+11, 4, (*tc,1.0), True)
        btn("focus_%d"%i, tn.upper(), bx2+12, by2, cw2-12, 22)
    ry += math.ceil(len(targets)/2)*28+4
    hln(rx,ry,IW,CYAN_B); ry+=8

    ry = sec_hdr(rx, ry, IW, "KEY REFERENCE")
    if cam_mode=="FreeFly":
        kmap=[("W/S","THRUST FWD/BACK"),("A/D","STRAFE L/R"),
              ("SPC/CTRL","UP/DOWN"),("MOUSE","AIM")]
    else:
        kmap=[("DRAG","ROTATE CAMERA"),("SCROLL","ZOOM"),
              ("R","RESET VIEW"),("P","PAUSE/RESUME")]
    for k,v in kmap:
        ex2=put(k, rx, ry, 1.3, AMBER)
        put("  "+v, ex2, ry, 1.1, DIM)
        ry += int(th(1.2))+4

    # Restore hover
    for b in BTNS:
        b["hover"] = old_h.get(b["id"],False)

    glDisable(GL_LINE_SMOOTH); glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()

# ═══════════════════════════════════════════════
# INPUT
# ═══════════════════════════════════════════════
def cursor_cb(win, xp, yp):
    global cam_yaw,cam_pitch,last_mx,last_my,mouse_down,time_scale,slider_drag
    for b in BTNS:
        b["hover"]=(b["x"]<=xp<=b["x"]+b["w"] and b["y"]<=yp<=b["y"]+b["h"])
    if slider_drag and sldr_w>0:
        f=max(0.0,min(1.0,(xp-sldr_x)/sldr_w))
        time_scale=f*SPEED_MAX
        if time_scale<0.08: time_scale=0.0
    elif mouse_down:
        dx=xp-last_mx; dy=yp-last_my
        cam_yaw  += dx*0.30
        cam_pitch = max(-89,min(89,cam_pitch+dy*0.30))
    last_mx,last_my=xp,yp

def mouse_cb(win, btn2, action, mods):
    global mouse_down,slider_drag,time_scale,last_nz_speed
    if btn2!=glfw.MOUSE_BUTTON_LEFT: return
    xp,yp=glfw.get_cursor_pos(win)
    if action==glfw.PRESS:
        if sldr_w>0 and (xp-sldr_x-sldr_w*(time_scale/max(SPEED_MAX,1)))**2+(yp-sldr_y)**2<196:
            slider_drag=True; return
        hit=False
        for b in BTNS:
            if b["x"]<=xp<=b["x"]+b["w"] and b["y"]<=yp<=b["y"]+b["h"]:
                _click(b["id"]); hit=True; break
        if not hit:
            ww,wh=glfw.get_window_size(win)
            in_ui=(xp<265 or xp>ww-265 or yp<34 or yp>wh-26)
            if not in_ui: mouse_down=True
    else:
        slider_drag=False; mouse_down=False

def scroll_cb(win, xo, yo):
    global cam_dist, target_cam_dist
    cam_dist=max(5,min(250,cam_dist-yo*2.2))
    target_cam_dist = cam_dist

def key_cb(win, key, sc, action, mods):
    global cam_yaw,cam_pitch,cam_dist,time_scale,ship_x,ship_y,ship_z,last_nz_speed
    if action not in (glfw.PRESS,glfw.REPEAT): return
    if key==glfw.KEY_ESCAPE: glfw.set_window_should_close(win,True)
    elif key==glfw.KEY_R:
        cam_yaw,cam_pitch,cam_dist=30.0,-20.0,58.0
        ship_x=ship_y=0.0; ship_z=40.0
    elif key in (glfw.KEY_EQUAL,glfw.KEY_KP_ADD):
        time_scale=min((time_scale or 0.5)*1.5,SPEED_MAX)
    elif key in (glfw.KEY_MINUS,glfw.KEY_KP_SUBTRACT):
        time_scale=max(time_scale/1.5,0.1)
    elif key==glfw.KEY_P:
        if time_scale==0: time_scale=last_nz_speed
        else: last_nz_speed=time_scale; time_scale=0.0

def fly_cb(win, dt):
    global ship_x,ship_y,ship_z
    if cam_mode!="FreeFly": return
    sp=28*dt
    dx=math.cos(math.radians(cam_pitch))*math.sin(math.radians(cam_yaw))
    dy=math.sin(math.radians(cam_pitch))
    dz=math.cos(math.radians(cam_pitch))*math.cos(math.radians(cam_yaw))
    rx=math.cos(math.radians(cam_yaw)); rz=-math.sin(math.radians(cam_yaw))
    K=glfw.get_key
    if K(win,glfw.KEY_W)==glfw.PRESS: ship_x+=dx*sp; ship_y+=dy*sp; ship_z+=dz*sp
    if K(win,glfw.KEY_S)==glfw.PRESS: ship_x-=dx*sp; ship_y-=dy*sp; ship_z-=dz*sp
    if K(win,glfw.KEY_A)==glfw.PRESS: ship_x-=rx*sp; ship_z-=rz*sp
    if K(win,glfw.KEY_D)==glfw.PRESS: ship_x+=rx*sp; ship_z+=rz*sp
    if K(win,glfw.KEY_SPACE)==glfw.PRESS:        ship_y+=sp
    if K(win,glfw.KEY_LEFT_CONTROL)==glfw.PRESS: ship_y-=sp

# ═══════════════════════════════════════════════
# LIGHTING
# ═══════════════════════════════════════════════
def setup_lights():
    glEnable(GL_LIGHTING); glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE); glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0,GL_DIFFUSE,  [1.00,1.00,0.92,1.0])
    glLightfv(GL_LIGHT0,GL_SPECULAR, [1.00,1.00,0.85,1.0])
    glLightfv(GL_LIGHT0,GL_AMBIENT,  [0.04,0.04,0.06,1.0])
    glLightf (GL_LIGHT0,GL_CONSTANT_ATTENUATION,  1.0)
    glLightf (GL_LIGHT0,GL_LINEAR_ATTENUATION,    0.008)
    glLightf (GL_LIGHT0,GL_QUADRATIC_ATTENUATION, 0.0006)

# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════
def main():
    global focus_x, focus_y, focus_z, transition_alpha, cam_dist, target_cam_dist
    if not glfw.init(): raise RuntimeError("GLFW init failed")
    glfw.window_hint(glfw.SAMPLES, 4)
    win=glfw.create_window(1440, 900,
        "Solar System Mission Control  —  Huseyin Tunay Celik (97294)", None, None)
    if not win: glfw.terminate(); raise RuntimeError("Window failed")
    glfw.make_context_current(win)
    glfw.set_cursor_pos_callback   (win, cursor_cb)
    glfw.set_mouse_button_callback (win, mouse_cb)
    glfw.set_scroll_callback       (win, scroll_cb)
    glfw.set_key_callback          (win, key_cb)
    glEnable(GL_MULTISAMPLE)
    glClearColor(0.0, 0.005, 0.012, 1.0)
    setup_lights()
    
    # Download and load all photorealistic textures with real-time UI loading screen
    download_and_load_textures(win)

    last_t=glfw.get_time(); sim_t=0.0
    
    # Initialize camera focus position to prevent startup jump
    init_pos = get_body_position(focus_idx, 0.0)
    focus_x, focus_y, focus_z = init_pos

    while not glfw.window_should_close(win):
        glfw.poll_events()
        now=glfw.get_time(); dt=min(now-last_t,0.05); last_t=now
        sim_t += dt*time_scale*10.0

        fly_cb(win, dt)

        fw,fh=glfw.get_framebuffer_size(win)
        ww,wh=glfw.get_window_size(win)
        if ww<=0 or wh<=0 or fw<=0 or fh<=0:
            glfw.swap_buffers(win); continue

        glViewport(0,0,fw,fh)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(45.0, fw/max(fh,1), 0.1, 600.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()

        # Smooth camera look-at target transition
        if transition_alpha < 1.0:
            transition_alpha = min(1.0, transition_alpha + 1.8 * dt)
            
        pos_old = get_body_position(prev_focus_idx, sim_t)
        pos_new = get_body_position(focus_idx, sim_t)
        
        # Smoothly interpolate look-at point (ease-in-out curve)
        t_smooth = 3 * (transition_alpha ** 2) - 2 * (transition_alpha ** 3)
        lx = pos_old[0] + (pos_new[0] - pos_old[0]) * t_smooth
        ly = pos_old[1] + (pos_new[1] - pos_old[1]) * t_smooth
        lz = pos_old[2] + (pos_new[2] - pos_old[2]) * t_smooth
        
        focus_x, focus_y, focus_z = lx, ly, lz
        
        # Smoothly interpolate zoom distance
        cam_dist += (target_cam_dist - cam_dist) * 4.0 * dt

        if cam_mode=="Orbit":
            ex=lx+cam_dist*math.cos(math.radians(cam_pitch))*math.sin(math.radians(cam_yaw))
            ey=ly+cam_dist*math.sin(math.radians(cam_pitch))
            ez=lz+cam_dist*math.cos(math.radians(cam_pitch))*math.cos(math.radians(cam_yaw))
            gluLookAt(ex,ey,ez, lx,ly,lz, 0,1,0)
        else:
            ddx=math.cos(math.radians(cam_pitch))*math.sin(math.radians(cam_yaw))
            ddy=math.sin(math.radians(cam_pitch))
            ddz=math.cos(math.radians(cam_pitch))*math.cos(math.radians(cam_yaw))
            ex=ship_x-ddx*cam_dist*0.35
            ey=ship_y-ddy*cam_dist*0.35+0.5
            ez=ship_z-ddz*cam_dist*0.35
            lx,ly,lz=ship_x,ship_y,ship_z
            gluLookAt(ex,ey,ez,ship_x,ship_y,ship_z,0,1,0)

        glLightfv(GL_LIGHT0, GL_POSITION, [0.0,0.0,0.0,1.0])

        draw_background_skybox(TEXTURES["Background"], ex, ey, ez)
        draw_stars(now)
        draw_orbits()
        draw_sun()

        eox=eoy=eoz=0.0
        bodies=[("SUN",0.0,0.0,0.0,3.5)]
        for i,p in enumerate(PLANETS):
            ox,oy,oz=draw_planet(p,sim_t)
            bodies.append((p[0].upper(),ox,oy,oz,p[1]))
            if i==2: eox,eoy,eoz=ox,oy,oz

        mx,my,mz=draw_moon(eox,eoy,eoz,sim_t)
        bodies.append(("MOON",mx,my,mz,MOON_R))
        draw_belt(sim_t)
        if cam_mode=="FreeFly":
            draw_ship()

        if show_labels:
            for nm,bx2,by2,bz,brad in bodies:
                d=math.sqrt((bx2-ex)**2+(by2-ey)**2+(bz-ez)**2)
                if 1.0<d<120:
                    label3d(nm, bx2, by2+brad+0.9, bz)

        draw_hud(ww, wh, sim_t, now)
        glfw.swap_buffers(win)

    glfw.terminate()

if __name__=="__main__":
    main()
