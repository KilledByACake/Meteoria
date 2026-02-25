import pgzrun
import math
import pygame
import random

# Window
WIDTH = 480
HEIGHT = 720
TITLE = "Endless Biker in Finland Tester"

# Terrain
# Procedural terrain parameters (tune these)
SEED = 12345          # change to any integer for a different world
NOISE_SCALE = 0.004   # smaller = longer hills, larger = shorter hills
OCTAVES = 4           # number of detail layers (3–5 is good)
HILL_HEIGHT = 50      # overall hill amplitude in pixels

# Internal cache for gradients (performance)
_grad_cache = {}

def _grad(i):
    # deterministic gradient in [-1, 1] per integer coordinate i
    g = _grad_cache.get(i)
    if g is None:
        rng = random.Random(i * 1619 + SEED)  # hashed seed per index
        g = rng.uniform(-1.0, 1.0)
        _grad_cache[i] = g
    return g

def _perlin1d(x):
    # 1D Perlin-like noise with fade smoothing
    i0 = math.floor(x)
    i1 = i0 + 1
    t = x - i0
    fade = t*t*t*(t*(t*6 - 15) + 10)  # smoothstep (Perlin fade)
    n0 = _grad(i0) * t
    n1 = _grad(i1) * (t - 1)
    return (1 - fade) * n0 + fade * n1

def _fractal_noise(x, scale=NOISE_SCALE, octaves=OCTAVES):
    # sum multiple octaves for richer detail
    n = 0.0
    amp = 1.0
    freq = 1.0
    for _ in range(octaves):
        n += _perlin1d(x * scale * freq) * amp
        freq *= 2.0
        amp *= 0.5
    return n

def get_ground_height(x):
    # baseline + fractal noise scaled to pixels
    return HEIGHT // 2 + _fractal_noise(x) * HILL_HEIGHT

# Image scaling cache
_scaled_cache = {}
def scale_to_max(name, max_h):
    key = (name, max_h)
    surf = _scaled_cache.get(key)
    if surf is None:
        src = images.load(name)
        w, h = src.get_size()
        factor = min(1.0, max_h / h)  # never upscale
        surf = pygame.transform.smoothscale(src, (int(w * factor), int(h * factor)))
        _scaled_cache[key] = surf
    return surf

# Cyclist (target 80 px height)
runner = Actor("bicycler1")
runner.x = 140
runner.index = 0
runner.images = ["bicycler1", "bicycler2", "bicycler3"]
RUNNER_TARGET_HEIGHT = 80
frames = [scale_to_max(n, RUNNER_TARGET_HEIGHT) for n in runner.images]
W, H = frames[0].get_size()

# Bike geometry (tune to your image)
WHEEL_BASE = int(0.55 * W)  # distance between wheel contacts
MARGIN_BOTTOM = 0           # pixels from image bottom to wheel contact line

# Motion / camera / game state
runner_speed = 5
frame_counter = 0
camera_x = 0

# Energy model (score)
ENERGY_PER_PX = 1.0     # base energy per pixel on flat
UPHILL_BONUS = 1.2      # >0 slope increases energy: 1 + UPHILL_BONUS*slope
DOWNHILL_PENALTY = 1.0  # <0 slope decreases energy: 1 - DOWNHILL_PENALTY*|slope|
MULT_MIN = 0.3
MULT_MAX = 2.0
energy_total = 0.0

# Timer (2 minutes) and message duration
FPS = 60
TIMER_SEC = 10
MESSAGE_DURATION_SEC = 2
timer_frames = TIMER_SEC * FPS
game_over = False

# Collectibles (foreground, max 50 px)
COLLECTIBLE_MAX_HEIGHT = 50
collectibles = []
HEADSET_THRESHOLD_ENERGY = 400
PHONE_THRESHOLD_ENERGY = 1000
headset_spawned = False
phone_spawned = False

# UI message
message_text = ""
message_timer = 0

# Rotation anchor state
runner_angle_rad = 0.0
runner_anchor_y = int(get_ground_height(runner.x))

def reset_game():
    global runner_speed, frame_counter, camera_x
    global energy_total, timer_frames, game_over
    global runner_angle_rad, runner_anchor_y
    global collectibles, headset_spawned, phone_spawned, message_text, message_timer

    runner_speed = 5
    frame_counter = 0
    camera_x = 0
    energy_total = 0.0
    timer_frames = TIMER_SEC * FPS
    game_over = False
    runner.index = 0
    runner_angle_rad = 0.0
    runner_anchor_y = int(get_ground_height(runner.x))
    collectibles = []
    headset_spawned = False
    phone_spawned = False
    message_text = ""
    message_timer = 0

def spawn_collectible(name):
    surf = scale_to_max(name, COLLECTIBLE_MAX_HEIGHT)
    wx = camera_x + WIDTH + 160       # ahead of screen
    wy = get_ground_height(wx) - 2    # sit on ground
    collectibles.append({"name": name, "surf": surf, "wx": wx, "wy": wy})

def draw():
    screen.clear()
    screen.fill("skyblue")

    # Ground
    for sx in range(WIDTH):
        wx = sx + camera_x
        y = int(get_ground_height(wx))
        screen.draw.line((sx, y), (sx, HEIGHT), (0, 250, 154))

    # Collectibles (foreground)
    for c in collectibles:
        sx = int(c["wx"] - camera_x)
        sy = int(c["wy"])
        rect = c["surf"].get_rect(midbottom=(sx, sy))
        screen.blit(c["surf"], rect)

    # Cyclist (rotated blit; anchor at wheel-bottom mid)
    surf = frames[runner.index]
    angle_deg = -math.degrees(runner_angle_rad)
    rot = pygame.transform.rotozoom(surf, angle_deg, 1.0)
    center_to_anchor = pygame.Vector2(0, H/2 - MARGIN_BOTTOM)
    rot_offset = center_to_anchor.rotate(angle_deg)
    cx = runner.x - rot_offset.x
    cy = runner_anchor_y - rot_offset.y
    rect = rot.get_rect(center=(cx, cy))
    screen.blit(rot, rect)

    # HUD
    seconds_left = max(0, timer_frames // FPS)
    mm = seconds_left // 60
    ss = seconds_left % 60
    screen.draw.text(f"Time: {mm:02d}:{ss:02d}", (10, 10), color="black")
    screen.draw.text(f"Energy (score): {int(energy_total)}", (10, 30), color="black")

    if game_over:
        screen.draw.textbox(
            f"Time's up!\nFinal score: {int(energy_total)}\nPress R to restart",
            Rect(40, 80, WIDTH-80, 100),
            color="black"
        )

    if message_timer > 0 and message_text:
        screen.draw.textbox(message_text, Rect(10, 60, WIDTH-20, 60), color="black")

def update():
    global runner_speed, frame_counter, camera_x
    global runner_angle_rad, runner_anchor_y
    global energy_total, timer_frames, game_over
    global headset_spawned, phone_spawned, message_text, message_timer

    if game_over:
        return

    # Animation
    frame_counter += 1
    if frame_counter % 10 == 0:
        runner.index = (runner.index + 1) % len(frames)

    # Sample terrain at wheel positions
    d = WHEEL_BASE
    xL = camera_x + runner.x - d/2
    xR = camera_x + runner.x + d/2
    yL = get_ground_height(xL)
    yR = get_ground_height(xR)

    # Tilt angle and speed
    runner_angle_rad = math.atan2(yR - yL, d)
    slope = (yR - yL) / d  # positive = uphill to the right

    runner_speed -= slope * 0.6
    runner_speed *= 0.99
    runner_speed = max(2, min(runner_speed, 10))

    # Move world
    camera_x += runner_speed

    # Anchor at midpoint between wheel heights
    runner_anchor_y = (yL + yR) / 2

    # Energy gain (more uphill, less downhill, normal on flat)
    if slope >= 0:
        mult = 1.0 + UPHILL_BONUS * slope
    else:
        mult = 1.0 - DOWNHILL_PENALTY * (-slope)
    mult = max(MULT_MIN, min(MULT_MAX, mult))
    energy_total += runner_speed * ENERGY_PER_PX * mult

    # Spawn collectibles when thresholds reached (once each)
    if (not headset_spawned) and energy_total >= HEADSET_THRESHOLD_ENERGY \
       and not any(c["name"] == "headset" for c in collectibles):
        spawn_collectible("headset")
        headset_spawned = True

    if (not phone_spawned) and energy_total >= PHONE_THRESHOLD_ENERGY \
       and not any(c["name"] == "telefon" for c in collectibles):
        spawn_collectible("telefon")
        phone_spawned = True

    # Pickup + cleanup (no extra points; just a message)
    for c in collectibles[:]:
        sx = c["wx"] - camera_x
        sy = c["wy"]
        if abs(sx - runner.x) <= 24 and abs(sy - runner_anchor_y) <= 28:
            if c["name"] == "headset":
                message_text = "You would need to bike for 90 more minutes to charge a headset!"
            elif c["name"] == "telefon":
                message_text = "You need to bike 3 more minutes to charge a full phone."
            else:
                message_text = "Collected item."
            message_timer = int(FPS * MESSAGE_DURATION_SEC)  # show 5 seconds
            collectibles.remove(c)
        elif sx < -200:
            collectibles.remove(c)

    # Timer
    timer_frames -= 1
    if timer_frames <= 0:
        game_over = True

    # Message timer countdown
    if message_timer > 0:
        message_timer -= 1
        if message_timer == 0:
            message_text = ""

def on_key_down(key):
    if key == keys.R and game_over:
        reset_game()

pgzrun.go()