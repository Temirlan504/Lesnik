import pygame
import math

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((100, 200, 100))  # green square placeholder
        self.rect = self.image.get_rect(center=pos)
        self.speed = 2

    def get_movement(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -1
        if keys[pygame.K_s]: dy = 1
        if keys[pygame.K_a]: dx = -1
        if keys[pygame.K_d]: dx = 1

        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx = dx / length * self.speed
            dy = dy / length * self.speed

        return dx, dy
