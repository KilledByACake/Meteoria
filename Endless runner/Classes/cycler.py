import pygame
import math
import pgzero

class Cycler:
  
  MAX_SPEED = 50
  MIN_SPEED = 0
  ADD_SPEED = 10
  SUB_SPEED = 0.1
    
    
  def __init__(self, images, build_frames, image_loader, target_height=80, wheel_base_ratio=0.55):
    self.actor_images = images
    self.index = 0
    self.frames = build_frames(image_loader, images, target_height)
    W, H = self.frames[0].get_size()
    self.W = W
    self.H = H
    self.WHEEL_BASE = int(wheel_base_ratio * W)
    self.MARGIN_BOTTOM = 0
    self.x = 140
    self.anchor_y = 0
    self.angle_rad = 0.0
    self.speed = 0

  def cycle(self, key):
    self.speed = min(self.speed + self.ADD_SPEED, self.MAX_SPEED)


  def update(self, camera_x, terrain_func):
    d = self.WHEEL_BASE
    xL = camera_x + self.x - d / 2
    xR = camera_x + self.x + d / 2
    yL = terrain_func(xL)
    yR = terrain_func(xR)

    self.angle_rad = math.atan2(yR - yL, d)
    slope = (yR - yL) / d
    self.speed -= slope * 0.6
    self.speed *= 0.99
    # Abbremsen wenn keine Taste gedrückt
    self.speed -= self.SUB_SPEED
    self.speed = max(self.MIN_SPEED, min(self.speed, self.MAX_SPEED))

    self.anchor_y = (yL + yR) / 2

  def animate(self, frame_counter):
    if self.speed > 0:
        # je schneller, desto öfter wechselt das Bild
        interval = max(2, int(15 / self.speed))
        if frame_counter % interval == 0:
            self.index = (self.index + 1) % len(self.frames)

  def draw(self, screen, camera_x):
      surf = self.frames[self.index]
      angle_deg = -math.degrees(self.angle_rad)
      rot = pygame.transform.rotozoom(surf, angle_deg, 1.0)
      center_to_anchor = pygame.Vector2(0, self.H / 2 - self.MARGIN_BOTTOM)
      rot_offset = center_to_anchor.rotate(angle_deg)
      cx = self.x - rot_offset.x
      cy = self.anchor_y - rot_offset.y
      rect = rot.get_rect(center=(cx, cy))
      screen.blit(rot, rect)
      
      
      
      
      
'''
runner = Actor("bicycler1")
runner.x = 140
runner.index = 0
runner.images = ["bicycler1", "bicycler2", "bicycler3"]
RUNNER_TARGET_HEIGHT = 80
frames = build_frames(images.load, runner.images, RUNNER_TARGET_HEIGHT)
W, H = frames[0].get_size()
WHEEL_BASE = int(0.55 * W)
MARGIN_BOTTOM = 0
'''