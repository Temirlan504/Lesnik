import pygame

class Fade:
    """
    Non-blocking fade overlay.
    mode: 'in' (fade from black -> transparent) or 'out' (transparent -> black)
    speed: how many alpha points to change per frame (tune for faster/slower)
    """
    def __init__(self, screen, mode="in", speed=8):
        self.screen = screen
        self.mode = mode
        self.speed = speed
        self.active = True
        self.alpha = 255 if mode == "in" else 0
        # Use convert_alpha for proper per-pixel alpha support
        self.surf = pygame.Surface(self.screen.get_size()).convert_alpha()

    def start(self, mode, speed=None):
        self.mode = mode
        if speed is not None:
            self.speed = speed
        self.alpha = 255 if mode == "in" else 0
        self.active = True

    def update(self):
        """Call once per frame in scene.update(). Returns True while active."""
        if not self.active:
            return False

        if self.mode == "in":
            self.alpha -= self.speed
            if self.alpha <= 0:
                self.alpha = 0
                self.active = False
        else:  # 'out'
            self.alpha += self.speed
            if self.alpha >= 255:
                self.alpha = 255
                self.active = False

        return self.active

    def draw(self):
        """Call after drawing scene content to overlay fade effect."""
        if not self.active and self.alpha == 0 and self.mode == "in":
            return
        # Fill surface with black and current alpha value
        self.surf.fill((0, 0, 0, int(self.alpha)))
        self.screen.blit(self.surf, (0, 0))
