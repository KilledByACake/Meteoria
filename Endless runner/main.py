import pgzrun
import math
import pygame
import json
from terrain import Terrain
from collectibles import create_manager
from assets import build_frames  # image scaling helper

HS_FILE = "highscore.json"  # saved next to main.py

WIDTH = 480
HEIGHT = 720
TITLE = "Endless Biker in Finland Tester"

FPS = 60
TIMER_SEC = 10            # set 120 for 2 minutes
MESSAGE_DURATION_SEC = 3  # pickup messages show for 3 seconds

# High score I/O
def load_highscore():
    try:
        with open(HS_FILE, "r") as f:
            data = json.load(f)
            return int(data.get("high_score", 0))
    except Exception:
        return 0

def save_highscore(value):
    try:
        with open(HS_FILE, "w") as f:
            json.dump({"high_score": int(value)}, f)
    except Exception:
        pass

# Terrain
terrain = Terrain(WIDTH, HEIGHT, FPS)

# Cyclist
runner = Actor("bicycler1")
runner.x = 140
runner.index = 0
runner.images = ["bicycler1", "bicycler2", "bicycler3"]
RUNNER_TARGET_HEIGHT = 80
frames = build_frames(images.load, runner.images, RUNNER_TARGET_HEIGHT)
W, H = frames[0].get_size()
WHEEL_BASE = int(0.55 * W)
MARGIN_BOTTOM = 0

# Motion / game state
runner_speed = 5
frame_counter = 0
camera_x = 0

# Energy (score)
ENERGY_PER_PX = 1.0
UPHILL_BONUS = 1.2
DOWNHILL_PENALTY = 1.0
MULT_MIN = 0.3
MULT_MAX = 2.0
energy_total = 0.0

timer_frames = TIMER_SEC * FPS
game_over = False
high_score = load_highscore()

# Collectibles
collectibles = create_manager(
    image_loader=images.load,
    fps=FPS,
    message_duration_sec=MESSAGE_DURATION_SEC,
    max_height=50,
    pickup_x_tol=24,
    pickup_y_tol=28
)

runner_angle_rad = 0.0
runner_anchor_y = int(terrain.get_ground_height(runner.x))

def reset_game():
    global runner_speed, frame_counter, camera_x
    global energy_total, timer_frames, game_over
    global runner_angle_rad, runner_anchor_y

    runner_speed = 5
    frame_counter = 0
    camera_x = 0
    energy_total = 0.0
    timer_frames = TIMER_SEC * FPS
    game_over = False
    runner.index = 0
    runner_angle_rad = 0.0
    runner_anchor_y = int(terrain.get_ground_height(runner.x))

    terrain.reset()
    collectibles.reset()

def draw():
    screen.clear()
    screen.fill("skyblue")

    # Ground
    for sx in range(WIDTH):
        wx = sx + camera_x
        y = int(terrain.get_ground_height(wx))
        screen.draw.line((sx, y), (sx, HEIGHT), (0, 250, 154))

    # Collectibles
    collectibles.draw(screen, camera_x)

    # Cyclist (rotated blit)
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
    screen.draw.text(f"High score: {int(high_score)}", (10, 50), color="black")

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
    global energy_total, timer_frames, game_over, high_score

    if game_over:
        return

    # Animation
    frame_counter += 1
    if frame_counter % 10 == 0:
        runner.index = (runner.index + 1) % len(frames)

    # Sample terrain at wheel positions
    d = WHEEL_BASE
    xL = camera_x + runner.x - d / 2
    xR = camera_x + runner.x + d / 2
    yL = terrain.get_ground_height(xL)
    yR = terrain.get_ground_height(xR)

    # Tilt and speed
    runner_angle_rad = math.atan2(yR - yL, d)
    slope = (yR - yL) / d
    runner_speed -= slope * 0.6
    runner_speed *= 0.99
    runner_speed = max(2, min(runner_speed, 10))

    # Move world and anchor
    camera_x += runner_speed
    runner_anchor_y = (yL + yR) / 2

    # Energy
    if slope >= 0:
        mult = 1.0 + UPHILL_BONUS * slope
    else:
        mult = 1.0 - DOWNHILL_PENALTY * (-slope)
    mult = max(MULT_MIN, min(MULT_MAX, mult))
    energy_total += runner_speed * ENERGY_PER_PX * mult

    # Terrain updates (spawn/cleanup hills)
    terrain.update(camera_x)

    # Collectibles
    collectibles.maybe_spawn(energy_total, camera_x, WIDTH, terrain.get_ground_height)
    collectibles.update(camera_x, runner.x, runner_anchor_y)

    # Timer and high score update
    timer_frames -= 1
    if timer_frames <= 0:
        game_over = True
        if int(energy_total) > int(high_score):
            high_score = int(energy_total)
            save_highscore(high_score)

def on_key_down(key):
    if key == keys.R and game_over:
        reset_game()

pgzrun.go()