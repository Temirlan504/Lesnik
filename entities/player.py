import pygame
import math

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((100, 200, 100))  # green square placeholder
        self.rect = self.image.get_rect(center=pos)
        self.speed = 2

    def update(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1

        # Normalize diagonal movement
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)  # magnitude of vector
            dx = dx / length * self.speed
            dy = dy / length * self.speed

        self.rect.x += dx
        self.rect.y += dy
