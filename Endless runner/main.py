import pgzrun
import math
import random
import pygame
from collectibles import CollectiblesManager

WIDTH = 480
HEIGHT = 720
TITLE = "Endless Biker in Finland Tester"

FPS = 60
TIMER_SEC = 120
MESSAGE_DURATION_SEC = 5

# Terrain: baseline + timed hills
def baseline_ground(x):
    return HEIGHT // 2 + math.sin(x * 0.01) * 50

HILL_SPAWN_MIN_SEC = 5
HILL_SPAWN_MAX_SEC = 20
HILL_WIDTH_MIN = 220
HILL_WIDTH_MAX = 520
HILL_HEIGHT_MIN = 20
HILL_HEIGHT_MAX = 80
HILL_SPAWN_AHEAD_MIN = 120
HILL_SPAWN_AHEAD_MAX = 320

hills = []  # {"cx", "w", "h"}
hill_spawn_countdown = int(random.uniform(HILL_SPAWN_MIN_SEC, HILL_SPAWN_MAX_SEC) * FPS)

def hill_profile(x, cx, width):
    half = width / 2.0
    s = (x - cx) / half
    if abs(s) >= 1.0:
        return 0.0
    return 0.5 * (1.0 + math.cos(math.pi * s))

def get_ground_height(x):
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
    cx = camera_x + WIDTH + ahead
    hills.append({"cx": cx, "w": w, "h": h})

def cleanup_hills():
    margin = 100
    left_cut = camera_x - margin
    for hill in hills[:]:
        if (hill["cx"] + hill["w"] / 2.0) < left_cut:
            hills.remove(hill)

# Image scaling cache
_scaled_cache = {}
def scale_to_max(name, max_h):
    key = (name, max_h)
    surf = _scaled_cache.get(key)
    if surf is None:
        src = images.load(name)
        w, h = src.get_size()
        factor = min(1.0, max_h / h)
        surf = pygame.transform.smoothscale(src, (int(w * factor), int(h * factor)))
        _scaled_cache[key] = surf
    return surf

# Cyclist
runner = Actor("bicycler1")
runner.x = 140
runner.index = 0
runner.images = ["bicycler1", "bicycler2", "bicycler3"]
RUNNER_TARGET_HEIGHT = 80
frames = [scale_to_max(n, RUNNER_TARGET_HEIGHT) for n in runner.images]
W, H = frames[0].get_size()

WHEEL_BASE = int(0.55 * W)
MARGIN_BOTTOM = 0

# Motion and game state
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

timer_frames = TIMER_SEC * FPS
game_over = False

import pgzrun
import math
import random
import pygame
from collectibles import create_manager

WIDTH = 480
HEIGHT = 720
TITLE = "Endless Biker in Finland Tester"

FPS = 60
TIMER_SEC = 120
MESSAGE_DURATION_SEC = 5

# Terrain: baseline + timed hills
def baseline_ground(x):
    return HEIGHT // 2 + math.sin(x * 0.01) * 50

HILL_SPAWN_MIN_SEC = 5
HILL_SPAWN_MAX_SEC = 20
HILL_WIDTH_MIN = 220
HILL_WIDTH_MAX = 520
HILL_HEIGHT_MIN = 20
HILL_HEIGHT_MAX = 80
HILL_SPAWN_AHEAD_MIN = 120
HILL_SPAWN_AHEAD_MAX = 320

hills = []  # {"cx", "w", "h"}
hill_spawn_countdown = int(random.uniform(HILL_SPAWN_MIN_SEC, HILL_SPAWN_MAX_SEC) * FPS)

def hill_profile(x, cx, width):
    half = width / 2.0
    s = (x - cx) / half
    if abs(s) >= 1.0:
        return 0.0
    return 0.5 * (1.0 + math.cos(math.pi * s))

def get_ground_height(x):
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
    cx = camera_x + WIDTH + ahead
    hills.append({"cx": cx, "w": w, "h": h})

def cleanup_hills():
    margin = 100
    left_cut = camera_x - margin
    for hill in hills[:]:
        if (hill["cx"] + hill["w"] / 2.0) < left_cut:
            hills.remove(hill)

# Image scaling cache
_scaled_cache = {}
def scale_to_max(name, max_h):
    key = (name, max_h)
    surf = _scaled_cache.get(key)
    if surf is None:
        src = images.load(name)
        w, h = src.get_size()
        factor = min(1.0, max_h / h)
        surf = pygame.transform.smoothscale(src, (int(w * factor), int(h * factor)))
        _scaled_cache[key] = surf
    return surf

# Cyclist
runner = Actor("bicycler1")
runner.x = 140
runner.index = 0
runner.images = ["bicycler1", "bicycler2", "bicycler3"]
RUNNER_TARGET_HEIGHT = 80
frames = [scale_to_max(n, RUNNER_TARGET_HEIGHT) for n in runner.images]
W, H = frames[0].get_size()

WHEEL_BASE = int(0.55 * W)
MARGIN_BOTTOM = 0

# Motion and game state
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

timer_frames = TIMER_SEC * FPS
game_over = False

# Collectibles manager from module
collectibles = create_manager(
    image_loader=images.load,
    fps=FPS,
    message_duration_sec=MESSAGE_DURATION_SEC,
    max_height=50,
    pickup_x_tol=24,
    pickup_y_tol=28
)

runner_angle_rad = 0.0
runner_anchor_y = int(get_ground_height(runner.x))

def reset_game():
    global runner_speed, frame_counter, camera_x
    global energy_total, timer_frames, game_over
    global runner_angle_rad, runner_anchor_y
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

    hills = []
    hill_spawn_countdown = int(random.uniform(HILL_SPAWN_MIN_SEC, HILL_SPAWN_MAX_SEC) * FPS)

    collectibles.reset()

def draw():
    screen.clear()
    screen.fill("skyblue")

    for sx in range(WIDTH):
        wx = sx + camera_x
        y = int(get_ground_height(wx))
        screen.draw.line((sx, y), (sx, HEIGHT), (0, 250, 154))

    collectibles.draw(screen, camera_x)

    surf = frames[runner.index]
    angle_deg = -math.degrees(runner_angle_rad)
    rot = pygame.transform.rotozoom(surf, angle_deg, 1.0)
    center_to_anchor = pygame.Vector2(0, H/2 - MARGIN_BOTTOM)
    rot_offset = center_to_anchor.rotate(angle_deg)
    cx = runner.x - rot_offset.x
    cy = runner_anchor_y - rot_offset.y
    rect = rot.get_rect(center=(cx, cy))
    screen.blit(rot, rect)

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

    if collectibles.message_timer > 0 and collectibles.message_text:
        screen.draw.textbox(collectibles.message_text, Rect(10, 60, WIDTH-20, 60), color="black")

def update():
    global runner_speed, frame_counter, camera_x
    global runner_angle_rad, runner_anchor_y
    global energy_total, timer_frames, game_over
    global hill_spawn_countdown

    if game_over:
        return

    frame_counter += 1
    if frame_counter % 10 == 0:
        runner.index = (runner.index + 1) % len(frames)

    d = WHEEL_BASE
    xL = camera_x + runner.x - d/2
    xR = camera_x + runner.x + d/2
    yL = get_ground_height(xL)
    yR = get_ground_height(xR)

    runner_angle_rad = math.atan2(yR - yL, d)
    slope = (yR - yL) / d

    runner_speed -= slope * 0.6
    runner_speed *= 0.99
    runner_speed = max(2, min(runner_speed, 10))

    camera_x += runner_speed
    runner_anchor_y = (yL + yR) / 2

    if slope >= 0:
        mult = 1.0 + UPHILL_BONUS * slope
    else:
        mult = 1.0 - DOWNHILL_PENALTY * (-slope)
    mult = max(MULT_MIN, min(MULT_MAX, mult))
    energy_total += runner_speed * ENERGY_PER_PX * mult

    hill_spawn_countdown -= 1
    if hill_spawn_countdown <= 0:
        spawn_hill()
        hill_spawn_countdown = int(random.uniform(HILL_SPAWN_MIN_SEC, HILL_SPAWN_MAX_SEC) * FPS)
    cleanup_hills()

    collectibles.maybe_spawn(energy_total, camera_x, WIDTH, get_ground_height)
    collectibles.update(camera_x, runner.x, runner_anchor_y)

    timer_frames -= 1
    if timer_frames <= 0:
        game_over = True

def on_key_down(key):
    if key == keys.R and game_over:
        reset_game()

pgzrun.go()

runner_angle_rad = 0.0
runner_anchor_y = int(get_ground_height(runner.x))

def reset_game():
    global runner_speed, frame_counter, camera_x
    global energy_total, timer_frames, game_over
    global runner_angle_rad, runner_anchor_y
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

    hills = []
    hill_spawn_countdown = int(random.uniform(HILL_SPAWN_MIN_SEC, HILL_SPAWN_MAX_SEC) * FPS)

    collectibles.reset()

def draw():
    screen.clear()
    screen.fill("skyblue")

    for sx in range(WIDTH):
        wx = sx + camera_x
        y = int(get_ground_height(wx))
        screen.draw.line((sx, y), (sx, HEIGHT), (0, 250, 154))

    collectibles.draw(screen, camera_x)

    surf = frames[runner.index]
    angle_deg = -math.degrees(runner_angle_rad)
    rot = pygame.transform.rotozoom(surf, angle_deg, 1.0)
    center_to_anchor = pygame.Vector2(0, H/2 - MARGIN_BOTTOM)
    rot_offset = center_to_anchor.rotate(angle_deg)
    cx = runner.x - rot_offset.x
    cy = runner_anchor_y - rot_offset.y
    rect = rot.get_rect(center=(cx, cy))
    screen.blit(rot, rect)

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

    if collectibles.message_timer > 0 and collectibles.message_text:
        screen.draw.textbox(collectibles.message_text, Rect(10, 60, WIDTH-20, 60), color="black")

def update():
    global runner_speed, frame_counter, camera_x
    global runner_angle_rad, runner_anchor_y
    global energy_total, timer_frames, game_over
    global hill_spawn_countdown

    if game_over:
        return

    frame_counter += 1
    if frame_counter % 10 == 0:
        runner.index = (runner.index + 1) % len(frames)

    d = WHEEL_BASE
    xL = camera_x + runner.x - d/2
    xR = camera_x + runner.x + d/2
    yL = get_ground_height(xL)
    yR = get_ground_height(xR)

    runner_angle_rad = math.atan2(yR - yL, d)
    slope = (yR - yL) / d

    runner_speed -= slope * 0.6
    runner_speed *= 0.99
    runner_speed = max(2, min(runner_speed, 10))

    camera_x += runner_speed
    runner_anchor_y = (yL + yR) / 2

    if slope >= 0:
        mult = 1.0 + UPHILL_BONUS * slope
    else:
        mult = 1.0 - DOWNHILL_PENALTY * (-slope)
    mult = max(MULT_MIN, min(MULT_MAX, mult))
    energy_total += runner_speed * ENERGY_PER_PX * mult

    hill_spawn_countdown -= 1
    if hill_spawn_countdown <= 0:
        spawn_hill()
        hill_spawn_countdown = int(random.uniform(HILL_SPAWN_MIN_SEC, HILL_SPAWN_MAX_SEC) * FPS)
    cleanup_hills()

    collectibles.maybe_spawn(energy_total, camera_x, WIDTH, get_ground_height)
    collectibles.update(camera_x, runner.x, runner_anchor_y)

    timer_frames -= 1
    if timer_frames <= 0:
        game_over = True

def on_key_down(key):
    if key == keys.R and game_over:
        reset_game()

pgzrun.go()