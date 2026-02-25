import pygame

# Default collectibles configuration
ITEMS_CONFIG = {
    "headset": {
        "energy": 400,
        "message": "You would need to bike for 90 more minutes to charge a headset!",
    },
    "telefon": {
        "energy": 600,
        "message": "You need to bike 4 minutes to charge a full phone!",
    },
}

class CollectiblesManager:
    """Manage collectibles based on energy thresholds."""
    def __init__(self, items_config, image_loader, max_height=50, fps=60,
                 pickup_x_tol=24, pickup_y_tol=28, message_duration_sec=5):
        self.items_config = items_config
        self.image_loader = image_loader
        self.max_height = max_height
        self.pickup_x_tol = pickup_x_tol
        self.pickup_y_tol = pickup_y_tol
        self.fps = fps
        self.message_duration_sec = message_duration_sec

        self._scaled_cache = {}
        self.active = []     # {"name", "surf", "wx", "wy"}
        self.spawned = set()
        self.message_text = ""
        self.message_timer = 0

    def _scale_to_max(self, name):
        key = (name, self.max_height)
        surf = self._scaled_cache.get(key)
        if surf is None:
            src = self.image_loader(name)
            w, h = src.get_size()
            factor = min(1.0, self.max_height / h)  # never upscale
            surf = pygame.transform.smoothscale(src, (int(w * factor), int(h * factor)))
            self._scaled_cache[key] = surf
        return surf

    def reset(self):
        self.active.clear()
        self.spawned.clear()
        self.message_text = ""
        self.message_timer = 0

    def spawn_collectible(self, name, camera_x, screen_width, get_ground_height):
        surf = self._scale_to_max(name)
        wx = camera_x + screen_width + 160
        wy = get_ground_height(wx) - 2
        self.active.append({"name": name, "surf": surf, "wx": wx, "wy": wy})

    def maybe_spawn(self, energy_total, camera_x, screen_width, get_ground_height):
        for name, cfg in self.items_config.items():
            if name in self.spawned:
                continue
            if energy_total >= cfg["energy"] and not any(c["name"] == name for c in self.active):
                self.spawn_collectible(name, camera_x, screen_width, get_ground_height)
                self.spawned.add(name)

    def update(self, camera_x, runner_x, runner_y):
        for c in self.active[:]:
            sx = c["wx"] - camera_x
            sy = c["wy"]
            if abs(sx - runner_x) <= self.pickup_x_tol and abs(sy - runner_y) <= self.pickup_y_tol:
                msg = self.items_config.get(c["name"], {}).get("message", "Collected item.")
                self.message_text = msg
                self.message_timer = int(self.fps * self.message_duration_sec)
                self.active.remove(c)
            elif sx < -200:
                self.active.remove(c)

        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message_text = ""

    def draw(self, screen, camera_x):
        for c in self.active:
            sx = int(c["wx"] - camera_x)
            sy = int(c["wy"])
            rect = c["surf"].get_rect(midbottom=(sx, sy))
            screen.blit(c["surf"], rect)

def create_manager(image_loader, fps=60, message_duration_sec=5,
                   max_height=50, pickup_x_tol=24, pickup_y_tol=28):
    """Factory to create a manager with default ITEMS_CONFIG."""
    return CollectiblesManager(
        items_config=ITEMS_CONFIG,
        image_loader=image_loader,
        max_height=max_height,
        fps=fps,
        pickup_x_tol=pickup_x_tol,
        pickup_y_tol=pickup_y_tol,
        message_duration_sec=message_duration_sec
    )