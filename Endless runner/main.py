import pgzrun
import math
import random
import pygame

# Window
WIDTH = 480
HEIGHT = 720
TITLE = "Endless Biker in Finland Tester"

# Frame rate and timers
FPS = 60
TIMER_SEC = 120
MESSAGE_DURATION_SEC = 5

# ---------------- Terrain: baseline + timed random hills ----------------

# Baseline terrain (keep simple sine; you can swap for noise later)
def baseline_ground(x):
    return HEIGHT // 2 + math.sin(x * 0.01) * 50

# Hill spawn cadence (seconds)
HILL_SPAWN_MIN_SEC = 5
HILL_SPAWN_MAX_SEC = 20

# Hill size ranges (pixels)
HILL_WIDTH_MIN = 220
HILL_WIDTH_MAX = 520
HILL_HEIGHT_MIN = 20
HILL_HEIGHT_MAX = 80

# Spawn position ahead of camera (pixels)
HILL_SPAWN_AHEAD_MIN = 120
HILL_SPAWN_AHEAD_MAX = 320

# Storage for hills
hills = []  # each: {"cx": center_x_world, "w": width_px, "h": height_px}
hill_spawn_countdown = int(random.uniform(HILL_SPAWN_MIN_SEC, HILL_SPAWN_MAX_SEC) * FPS)

def hill_profile(x, cx, width):
    """Raised-cosine bump: smooth, zero slope at edges."""
    half = width / 2.0
    s = (x - cx) / half
    if abs(s) >= 1.0:
        return 0.0
    return 0.5 * (1.0 + math.cos(math.pi * s))

def get_ground_height(x):
    """Baseline + sum of active hills."""
    y = baseline_ground(x)
    for hill in hills:
        contrib = hill_profile(x, hill["cx"], hill["w"])
        if contrib > 0.0:
            y += hill["h"] * contrib
    return y

def spawn_hill():
    w = random.randint(HILL_WIDTH_MIN, HILL_WIDTH_MAX)
    h = random.randint(HILL_HEIGHT_MIN, HILL_HEIGHT_MAX)
    ahead = random.randint(HILL_SPAWN_AHEAD_MIN, HILL_SPAWN_AHEAD_MAX)
    cx = camera_x + WIDTH + ahead  # world x center ahead of view
    hills.append({"cx": cx, "w": w, "h": h})

def cleanup_hills():
    margin = 100
    left_cut = camera_x - margin
    for hill in hills[:]:
        if (hill["cx"] + hill["w"] / 2.0) < left_cut:
            hills.remove(hill)

# ---------------- Image scaling cache ----------------

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

# ---------------- Cyclist setup ----------------

runner = Actor("bicycler1")
runner.x = 140
runner.index = 0
runner.images = ["bicycler1", "bicycler2", "bicycler3"]
RUNNER_TARGET_HEIGHT = 80
frames = [scale_to_max(n, RUNNER_TARGET_HEIGHT) for n in runner.images]
W, H = frames[0].get_size()

# Bike geometry
WHEEL_BASE = int(0.55 * W)
MARGIN_BOTTOM = 0

# ---------------- Motion / game state ----------------

runner_speed = 5
frame_counter = 0
camera_x = 0

# Energy model (score)
ENERGY_PER_PX = 1.0
UPHILL_BONUS = 1.2
DOWNHILL_PENALTY = 1.0
MULT_MIN = 0.3
MULT_MAX = 2.0
energy_total = 0.0

# Timer and game over
timer_frames = TIMER_SEC * FPS
game_over = False

# ---------------- Collectibles ----------------

COLLECTIBLE_MAX_HEIGHT = 50
collectibles = []

HEADSET_THRESHOLD_ENERGY = 400
PHONE_THRESHOLD_ENERGY = 1000
headset_spawned = False
phone_spawned = False

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
    global hills, hill_spawn_countdown

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

    hills = []
    hill_spawn_countdown = int(random.uniform(HILL_SPAWN_MIN_SEC, HILL_SPAWN_MAX_SEC) * FPS)

def spawn_collectible(name):
    surf = scale_to_max(name, COLLECTIBLE_MAX_HEIGHT)
    wx = camera_x + WIDTH + 160
    wy = get_ground_height(wx) - 2
    collectibles.append({"name": name, "surf": surf, "wx": wx, "wy": wy})

def draw():
    screen.clear()
    screen.fill("skyblue")

    # Ground
    for sx in range(WIDTH):
        wx = sx + camera_x
        y = int(get_ground_height(wx))
        screen.draw.line((sx, y), (sx, HEIGHT), (0, 250, 154))

    # Collectibles
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
    global hill_spawn_countdown

    if game_over:
        return

    # Animation
    frame_counter += 1
    if frame_counter % 10 == 0:
        runner.index = (runner.index + 1) % len(frames)

    # Sample terrain at wheel positions (world x)
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

    # Timed hill spawning
    hill_spawn_countdown -= 1
    if hill_spawn_countdown <= 0:
        spawn_hill()
        hill_spawn_countdown = int(random.uniform(HILL_SPAWN_MIN_SEC, HILL_SPAWN_MAX_SEC) * FPS)
    cleanup_hills()

    # Spawn collectibles at thresholds (once each)
    if (not headset_spawned) and energy_total >= HEADSET_THRESHOLD_ENERGY \
       and not any(c["name"] == "headset" for c in collectibles):
        spawn_collectible("headset")
        headset_spawned = True

    if (not phone_spawned) and energy_total >= PHONE_THRESHOLD_ENERGY \
       and not any(c["name"] == "telefon" for c in collectibles):
        spawn_collectible("telefon")
        phone_spawned = True

    # Pickup + cleanup (message only)
    for c in collectibles[:]:
        sx = c["wx"] - camera_x
        sy = c["wy"]
        if abs(sx - runner.x) <= 24 and abs(sy - runner_anchor_y) <= 28:
            if c["name"] == "headset":
                message_text = "You would need to bike for 90 more minutes to charge a headset!"
            elif c["name"] == "telefon":
                message_text = "Now you have biked enough to charge a full phone (≈4 minutes)."
            else:
                message_text = "Collected item."
            message_timer = int(FPS * MESSAGE_DURATION_SEC)
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