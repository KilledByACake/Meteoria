import pgzrun
import math
import pygame
from datetime import datetime
from modules.terrain import Terrain
from modules.collectibles import create_manager
from modules.assets import build_frames
from modules.highscores import load_store, add_score_with_ranks  # no best_* imports now
from modules.cycler import Cycler

WIDTH = 480
HEIGHT = 720
TITLE = "Endless Biker in Finland Tester"

FPS = 60
TIMER_SEC = 10         # game length in seconds
MESSAGE_DURATION_SEC = 3  # pickup messages

PLAYER_NAME = "PlayerOne"

# Terrain
terrain = Terrain(WIDTH, HEIGHT, FPS)

# Cyclist
runner = Cycler(
    images=["bicycler1", "bicycler2", "bicycler3"],
    build_frames=build_frames,
    image_loader = images.load
)

# Motion / game state
runner_speed = 5
frame_counter = 0
camera_x = 0

# Energy model (distance + elevation)
FLAT_ENERGY_PER_PX = 1.0
UPHILL_ENERGY_PER_PX_Y = 0.8
DOWNHILL_MULTIPLIER = 0.6
energy_total = 0.0

# Track previous world position for dx/dy
prev_world_x = camera_x + runner.x
prev_ground_y = terrain.get_ground_height(prev_world_x)

# Timer / state
timer_frames = TIMER_SEC * FPS
game_over = False
end_message = ""

# High score store
store = load_store()

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
    global energy_total, timer_frames, game_over, end_message
    global runner_angle_rad, runner_anchor_y
    global prev_world_x, prev_ground_y

    runner_speed = 5
    frame_counter = 0
    camera_x = 0
    energy_total = 0.0
    timer_frames = TIMER_SEC * FPS
    game_over = False
    end_message = ""
    runner.index = 0
    runner_angle_rad = 0.0
    runner_anchor_y = int(terrain.get_ground_height(runner.x))

    terrain.reset()
    collectibles.reset()

    prev_world_x = camera_x + runner.x
    prev_ground_y = terrain.get_ground_height(prev_world_x)

def ordinal_word(n):
    return {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth"}.get(n, f"{n}th")

def build_rank_message(ranks):
    # Exclusivity: pick exactly one bucket in priority: yearly > monthly > daily
    yr = ranks.get("yearly_rank")
    mo = ranks.get("monthly_rank")
    dy = ranks.get("daily_rank")

    if yr is not None and 1 <= yr <= 5:
        if yr == 1:
            return "Congrats! You are the highest score of the year!"
        return f"You have the {ordinal_word(yr)} highest score this year!"

    if mo is not None and 1 <= mo <= 5:
        if mo == 1:
            return "Congrats! You are the highest score of the month!"
        return f"You have the {ordinal_word(mo)} highest score this month!"

    # Daily-only messages (no overlap with above)
    if dy == 1:
        return "Congrats! You are the highest score of the day!"
    if dy == 2:
        return "You have the second highest score today!"
    if dy == 3:
        return "You have the third highest score today!"
    if dy is not None and 4 <= dy <= 10:
        return "Congrats, you are one of the best today!"
    if dy is not None and 11 <= dy <= 30:
        return "Congrats on making today's list!"
    return "Come on, you can do better!"

def draw():
    screen.clear()
    screen.fill("skyblue")
    runner.draw(screen, camera_x)

    # Ground
    for sx in range(WIDTH):
        wx = sx + camera_x
        y = int(terrain.get_ground_height(wx))
        screen.draw.line((sx, y), (sx, HEIGHT), (0, 250, 154))

    # Collectibles
    collectibles.draw(screen, camera_x)

    # # Cyclist (rotated blit)
    # surf = frames[runner.index]
    # angle_deg = -math.degrees(runner_angle_rad)
    # rot = pygame.transform.rotozoom(surf, angle_deg, 1.0)
    # center_to_anchor = pygame.Vector2(0, H/2 - MARGIN_BOTTOM)
    # rot_offset = center_to_anchor.rotate(angle_deg)
    # cx = runner.x - rot_offset.x
    # cy = runner_anchor_y - rot_offset.y
    # rect = rot.get_rect(center=(cx, cy))
    # screen.blit(rot, rect)

    # HUD (no best-today / best-alltime lines)
    seconds_left = max(0, timer_frames // FPS)
    mm = seconds_left // 60
    ss = seconds_left % 60
    screen.draw.text(f"Time: {mm:02d}:{ss:02d}", (10, 10), color="black")
    screen.draw.text(f"Energy (score): {int(energy_total)}", (10, 30), color="black")

    if game_over:
        base = f"Time's up!\nFinal score: {int(energy_total)}\nPress R to restart"
        screen.draw.textbox(base, Rect(40, 80, WIDTH-80, 100), color="black")
        if end_message:
            screen.draw.textbox(end_message, Rect(40, 190, WIDTH-80, 90), color="black")

    if collectibles.message_timer > 0 and collectibles.message_text:
        screen.draw.textbox(collectibles.message_text, Rect(10, 60, WIDTH-20, 60), color="black")

def update():
    global runner_speed, frame_counter, camera_x
    global runner_angle_rad, runner_anchor_y
    global energy_total, timer_frames, game_over, end_message
    global prev_world_x, prev_ground_y, store
    
    
    if game_over:
        return
    
    runner.update(camera_x, terrain.get_ground_height)
    runner.animate(frame_counter)
    camera_x += runner.speed

    # Animation
    frame_counter += 1
    frame_counter += 1
    runner.animate(frame_counter)
        
    # Distance/elevation since last frame
    world_x = camera_x + runner.x
    dx = max(0.0, world_x - prev_world_x)
    ground_y = terrain.get_ground_height(world_x)
    dy = ground_y - prev_ground_y

    base = dx * FLAT_ENERGY_PER_PX * (DOWNHILL_MULTIPLIER if dy < 0 else 1.0)
    climb = max(0.0, dy) * UPHILL_ENERGY_PER_PX_Y
    energy_total += base + climb

    prev_world_x = world_x
    prev_ground_y = ground_y

    # Terrain updates
    terrain.update(camera_x)

    # Collectibles
    collectibles.maybe_spawn(energy_total, camera_x, WIDTH, terrain.get_ground_height)
    collectibles.update(camera_x, runner.x, runner_anchor_y)

    # Timer end → save score and build exclusive rank message
    timer_frames -= 1
    if timer_frames <= 0:
        game_over = True
        elapsed_sec = TIMER_SEC
        entry = {
            "name": PLAYER_NAME,
            "score": float(energy_total),
            "date": datetime.now().date().isoformat(),
            "energy_kj": float(energy_total),
            "duration_sec": int(elapsed_sec),
            "avg_power_w": None,
            "avg_speed": (camera_x / elapsed_sec) if elapsed_sec > 0 else None,
        }
        store, ranks = add_score_with_ranks(store, entry)
        end_message = build_rank_message(ranks)

        """ # Sample terrain at wheel positions
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
            runner_anchor_y = (yL + yR) / 2"""

    

def on_key_down(key):
    if key == keys.R and game_over:
        reset_game()
    if not game_over:
        runner.cycle(key)

pgzrun.go()