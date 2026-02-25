import pgzrun
import math
import pygame

# Window
WIDTH = 480
HEIGHT = 720
TITLE = "Endless Biker in Finland Tester"

# Motion / camera
runner_speed = 5
frame_counter = 0
camera_x = 0

# Terrain
def get_ground_height(x):
    return HEIGHT // 2 + math.sin(x * 0.01) * 50

# Actor (position only)
runner = Actor("bicycler1")
runner.x = 140
runner.index = 0
runner.images = ["bicycler1", "bicycler2", "bicycler3"]

# Scale frames
RUNNER_TARGET_HEIGHT = 80  # make smaller/larger here
def make_scaled_frames(names, target_h):
    frames = []
    for name in names:
        surf = images.load(name)
        w, h = surf.get_size()
        factor = target_h / h
        frames.append(pygame.transform.smoothscale(surf, (int(w*factor), int(h*factor))))
    return frames

frames = make_scaled_frames(runner.images, RUNNER_TARGET_HEIGHT)
W, H = frames[0].get_size()

# Bike geometry (tune to your image)
WHEEL_BASE = int(0.55 * W)  # horizontal distance between wheel contact points
MARGIN_BOTTOM = 0           # pixels from image bottom to wheel contact line (crop-tight -> 0)

# State
runner_angle_rad = 0.0
runner_anchor_y = int(get_ground_height(runner.x))  # midpoint between wheels

def draw():
    screen.clear()
    screen.fill("skyblue")

    # Ground
    for sx in range(WIDTH):
        wx = sx + camera_x
        y = int(get_ground_height(wx))
        screen.draw.line((sx, y), (sx, HEIGHT), (0, 250, 154))

    # Current frame and rotation
    surf = frames[runner.index]
    angle_deg = -math.degrees(runner_angle_rad)
    rot = pygame.transform.rotozoom(surf, angle_deg, 1.0)

    # Offset from image center to the midpoint of the wheel-bottom line (unrotated coords)
    center_to_anchor = pygame.Vector2(0, H/2 - MARGIN_BOTTOM)
    # Rotate that offset with the same angle used by rotozoom (screen coords)
    rot_offset = center_to_anchor.rotate(angle_deg)

    # Final blit position so wheels sit on ground (subtract the rotated offset)
    cx = runner.x - rot_offset.x
    cy = runner_anchor_y - rot_offset.y
    rect = rot.get_rect(center=(cx, cy))
    screen.blit(rot, rect)

    # Debug: wheel contact points (should sit on ground)
    d = WHEEL_BASE
    offL = pygame.Vector2(-d/2, 0).rotate(angle_deg)
    offR = pygame.Vector2(+d/2, 0).rotate(angle_deg)
    wheelL = (runner.x + offL.x, runner_anchor_y + offL.y)
    wheelR = (runner.x + offR.x, runner_anchor_y + offR.y)

def update():
    global runner_speed, frame_counter, camera_x, runner_angle_rad, runner_anchor_y

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
    slope = (yR - yL) / d
    runner_speed -= slope * 0.6   # adjust to taste
    runner_speed *= 0.99
    runner_speed = max(2, min(runner_speed, 10))
    camera_x += runner_speed

    # Anchor at the midpoint between the two heights
    runner_anchor_y = (yL + yR) / 2

pgzrun.go()