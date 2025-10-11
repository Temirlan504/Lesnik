import pygame
from utils.fade import Fade
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Hut:
    def __init__(self, screen):
        self.screen = screen
        self.fade = Fade(screen, mode="in", speed=3)
        self.bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg.fill((40, 25, 15))  # cozy brown background

    def update(self, keys, events):
        self.fade.update()
        return None

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.fade.draw()
