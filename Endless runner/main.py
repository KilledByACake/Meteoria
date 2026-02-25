import pgzrun  # imports pygame zero module
import math    # imports math module for mathematical functions
import pygame  # for image scaling

# Constant Settings for size
WIDTH = 480
HEIGHT = 720
TITLE = "Endless Biker in Finland Tester"

# Visual background rectangles (not used for physics)
sky = Rect(0, 0, WIDTH, HEIGHT // 2)
ground = Rect(0, HEIGHT // 2, WIDTH, HEIGHT // 2)

# Movement / physics variables
runner_speed = 5          # horizontal speed
frame_counter = 0         # update counter
camera_x = 0              # world offset (endless effect)

# Terrain function: returns ground height at world x
def get_ground_height(x):
    return HEIGHT // 2 + math.sin(x * 0.01) * 50
    # base: HEIGHT//2, amplitude: 50, wavelength factor: 0.01

# Actor: Bicycler (for position only)
runner = Actor("bicycler1")
runner.anchor = ('center', 'bottom')  # bottom-center anchor (for bottom positioning)
runner.x = 100
runner.index = 0
runner.images = ["bicycler1", "bicycler2", "bicycler3"]
runner.image = runner.images[0]
runner.bottom = int(get_ground_height(runner.x))  # ensure visible before first draw

# Scale animation frames to a comfortable on-screen size
RUNNER_TARGET_HEIGHT = 50  # adjust to taste (e.g., 160–260)

def make_scaled_frames(names, target_height):
    frames = []
    for name in names:
        surf = images.load(name)  # Pygame Zero image surface
        w, h = surf.get_size()
        factor = target_height / h
        new_size = (int(w * factor), int(h * factor))
        frames.append(pygame.transform.smoothscale(surf, new_size))
    return frames

runner_frames = make_scaled_frames(runner.images, RUNNER_TARGET_HEIGHT)
print("runner original size:", images.load("bicycler1").get_size(),
      "scaled size:", runner_frames[0].get_size())

# Actor: Monument (elk)
elk = Actor("elk")
elk.bottomleft = (600, HEIGHT // 2 + 20)

def draw():
    screen.clear()
    screen.fill("skyblue")

    # Draw dynamic ground using camera_x to convert screen x -> world x
    for x in range(WIDTH):
        world_x = x + camera_x
        y = int(get_ground_height(world_x))
        screen.draw.line((x, y), (x, HEIGHT), (0, 250, 154))

    # Draw runner with midbottom anchoring
    surf = runner_frames[runner.index]
    rect = surf.get_rect(midbottom=(runner.x, runner.bottom))
    screen.blit(surf, rect)

    # Draw elk relative to camera position
    elk.x = 600 - camera_x
    elk.draw()

def update():
    global runner_speed, frame_counter, camera_x

    # Animation: change frame every 10 updates
    frame_counter += 1
    if frame_counter % 10 == 0:
        runner.index = (runner.index + 1) % len(runner_frames)

    # Terrain slope calculation at runner's world x
    current_height = get_ground_height(camera_x + runner.x)
    next_height = get_ground_height(camera_x + runner.x + 1)
    slope = next_height - current_height  # >0 uphill, <0 downhill

    # Speed adjustment by slope + simple friction and clamping
    runner_speed -= slope * 0.05
    runner_speed *= 0.99
    runner_speed = max(2, min(runner_speed, 10))

    # Move the world (endless runner effect)
    camera_x += runner_speed

    # Stick runner to ground using bottom
    runner.bottom = int(get_ground_height(camera_x + runner.x))

pgzrun.go()  # executes the game loop