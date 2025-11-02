import pygame
import os
from utils.resource_path import resource_path

class Lesnik(pygame.sprite.Sprite):
    def __init__(self, position, path_points=None, speed=2):
        super().__init__()
        self.speed = speed
        self.path_points = path_points or []
        self.current_target = 0
        self.moving = False
        self.direction = pygame.Vector2(0, 1)  # Facing down initially

        # --- Animation setup ---
        self.animations = self.load_animations(resource_path("assets/sprites/lesnik"))
        self.state = "idle_front"
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 120  # ms between frames

        # Initialize sprite
        self.image = self.animations[self.state][0]
        self.rect = self.image.get_rect(center=position)

    # -------------------------
    # 🖼️ Load animations from folders
    # -------------------------
    def load_animations(self, base_path):
        animations = {}
        directions = ["front", "back", "left", "right"]
        states = ["idle", "walk"]

        for state in states:
            for direction in directions:
                folder = os.path.join(base_path, f"{state}_{direction}")
                if not os.path.exists(folder):
                    continue
                frames = []
                for file in sorted(os.listdir(folder)):
                    if file.endswith(".png"):
                        img = pygame.image.load(os.path.join(folder, file)).convert_alpha()
                        img = pygame.transform.scale(img, (50, 90))
                        frames.append(img)
                if frames:
                    animations[f"{state}_{direction}"] = frames
        return animations

    # -------------------------
    # 🚶 Movement & animation update
    # -------------------------
    def update(self, dt=16):
        # --- Movement logic ---
        if self.moving and self.path_points:
            target = pygame.Vector2(self.path_points[self.current_target])
            diff = target - pygame.Vector2(self.rect.center)
            if diff.length() > 0:
                self.direction = diff.normalize()
                self.rect.center += self.direction * self.speed

            # Arrived at point?
            if pygame.Vector2(self.rect.center).distance_to(target) < 4:
                self.current_target += 1
                if self.current_target >= len(self.path_points):
                    self.moving = False

        # --- Determine current animation ---
        self.update_state()
        self.animate(dt)

    def update_state(self):
        old_state = self.state
        if not self.moving:
            self.state = f"idle_{self.get_facing_direction()}"
        else:
            self.state = f"walk_{self.get_facing_direction()}"
        
        # Reset frame index when state changes
        if old_state != self.state:
            self.frame_index = 0

    def get_facing_direction(self):
        # Determine direction based on vector
        if abs(self.direction.x) > abs(self.direction.y):
            return "right" if self.direction.x > 0 else "left"
        else:
            return "front" if self.direction.y > 0 else "back"

    # -------------------------
    # 🌀 Animate frames
    # -------------------------
    def animate(self, dt):
        frames = self.animations.get(self.state, [])
        if not frames:
            return
        
        # Safety check: reset frame_index if it's out of range
        if self.frame_index >= len(frames):
            self.frame_index = 0
        
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(frames)
        self.image = frames[self.frame_index]

    # -------------------------
    # 🚀 Path follow control
    # -------------------------
    def start_path(self, points):
        self.path_points = points
        self.current_target = 0
        self.moving = True
