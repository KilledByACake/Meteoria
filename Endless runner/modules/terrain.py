import math
import random

class Terrain:
    """Baseline ground plus timed random hills; query ground height at world x."""

    def __init__(self, screen_width, screen_height, fps):
        self.W = screen_width
        self.H = screen_height
        self.FPS = fps

        # Hill timing and size
        self.spawn_min_sec = 5
        self.spawn_max_sec = 20
        self.width_min = 220
        self.width_max = 520
        self.height_min = 20
        self.height_max = 80
        self.spawn_ahead_min = 120
        self.spawn_ahead_max = 320

        self.hills = []  # {"cx", "w", "h"}
        self.spawn_countdown = int(random.uniform(self.spawn_min_sec, self.spawn_max_sec) * self.FPS)

    def baseline_ground(self, x):
        return self.H // 2 + math.sin(x * 0.01) * 50

    @staticmethod
    def hill_profile(x, cx, width):
        half = width / 2.0
        s = (x - cx) / half
        if abs(s) >= 1.0:
            return 0.0
        return 0.5 * (1.0 + math.cos(math.pi * s))  # smooth bump

    def get_ground_height(self, x):
        y = self.baseline_ground(x)
        for hill in self.hills:
            contrib = self.hill_profile(x, hill["cx"], hill["w"])
            if contrib > 0.0:
                y += hill["h"] * contrib
        return y

    def spawn_hill(self, camera_x):
        w = random.randint(self.width_min, self.width_max)
        h = random.randint(self.height_min, self.height_max)
        ahead = random.randint(self.spawn_ahead_min, self.spawn_ahead_max)
        cx = camera_x + self.W + ahead
        self.hills.append({"cx": cx, "w": w, "h": h})

    def cleanup(self, camera_x):
        margin = 100
        left_cut = camera_x - margin
        for hill in self.hills[:]:
            if (hill["cx"] + hill["w"] / 2.0) < left_cut:
                self.hills.remove(hill)

    def update(self, camera_x):
        self.spawn_countdown -= 1
        if self.spawn_countdown <= 0:
            self.spawn_hill(camera_x)
            self.spawn_countdown = int(random.uniform(self.spawn_min_sec, self.spawn_max_sec) * self.FPS)
        self.cleanup(camera_x)

    def reset(self):
        self.hills.clear()
        self.spawn_countdown = int(random.uniform(self.spawn_min_sec, self.spawn_max_sec) * self.FPS)