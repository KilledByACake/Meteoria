import pygame

# Shared cache for scaled surfaces
_cache = {}

def scale_to_max(image_loader, name, max_h):
    """Load and shrink to max_h (no upscaling). Cached per (name, max_h)."""
    key = (name, max_h)
    surf = _cache.get(key)
    if surf is None:
        src = image_loader(name)
        w, h = src.get_size()
        factor = min(1.0, max_h / h)
        surf = pygame.transform.smoothscale(src, (int(w * factor), int(h * factor)))
        _cache[key] = surf
    return surf

def build_frames(image_loader, names, target_h):
    """Return scaled surfaces for animation frames."""
    return [scale_to_max(image_loader, n, target_h) for n in names]