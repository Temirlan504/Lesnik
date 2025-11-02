import pygame
import math
import os
from utils.resource_path import resource_path

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        
        # Animation properties
        self.animations = {
            'idle_up': [],
            'idle_down': [],
            'idle_left': [],
            'idle_right': [],
            'walk_up': [],
            'walk_down': [],
            'walk_left': [],
            'walk_right': [],
        }
        
        # Load animations
        self.load_animations()
        
        # Current animation state
        self.direction = 'up'  # up, down, left, right
        self.state = 'idle'  # idle or walk
        self.is_sitting = False
        self.current_frame = 0
        self.animation_speed = 0.15  # Lower = slower animation
        self.frame_counter = 0
        
        # Set initial image
        self.image = self.animations['idle_up'][0]
        self.rect = self.image.get_rect(center=pos)
        self.speed = 2
        
    def load_animations(self):
        """Load all animation frames"""
        base_path = "assets/sprites/player/"

        for key in self.animations.keys():
            state, direction = key.split('_')

            if state == 'idle':
                # Load single idle frame
                path = resource_path(f"{base_path}player_idle_{direction}.png")
                if os.path.exists(path):
                    frame = pygame.image.load(path).convert_alpha()
                    frame = pygame.transform.scale(frame, (50, 90))
                    self.animations[key].append(frame)
            else:
                # Load walk animation frames (try up to 8 frames)
                frame_num = 1
                while frame_num <= 8:
                    path = resource_path(f"{base_path}player_walk_{direction}_{frame_num}.png")
                    if os.path.exists(path):
                        frame = pygame.image.load(path).convert_alpha()
                        frame = pygame.transform.scale(frame, (50, 90))
                        self.animations[key].append(frame)
                        frame_num += 1
                    else:
                        break
        
        # Fallback: if no animations loaded, create a simple colored rectangle
        for key in self.animations.keys():
            if not self.animations[key]:
                fallback = pygame.Surface((50, 90), pygame.SRCALPHA)
                fallback.fill((100, 150, 255, 255))
                self.animations[key].append(fallback)

    def get_movement(self, keys):
        dx, dy = 0, 0
        new_direction = self.direction
        new_state = self.state
        
        if keys[pygame.K_w]: 
            dy = -1
            new_direction = 'up'
        if keys[pygame.K_s]: 
            dy = 1
            new_direction = 'down'
        if keys[pygame.K_a]: 
            dx = -1
            new_direction = 'left'
        if keys[pygame.K_d]: 
            dx = 1
            new_direction = 'right'

        # Update state
        if dx != 0 or dy != 0:
            new_state = 'walk'
            length = math.hypot(dx, dy)
            dx = dx / length * self.speed
            dy = dy / length * self.speed
        else:
            new_state = 'idle'
        
        # Reset frame if animation changed
        if new_direction != self.direction or new_state != self.state:
            self.current_frame = 0
            self.frame_counter = 0
        
        self.direction = new_direction
        self.state = new_state

        return dx, dy

    def update_animation(self):
        """Update the current animation frame"""
        animation_key = f"{self.state}_{self.direction}"
        frames = self.animations[animation_key]
        
        if not frames:
            return

        # Update frame counter
        self.frame_counter += self.animation_speed
        
        if self.frame_counter >= 1:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(frames)
        
        # Update image
        old_center = self.rect.center
        self.image = frames[int(self.current_frame)]
        self.rect = self.image.get_rect(center=old_center)

    def move_player(self, dx, dy, collision_rects):
        """Move player with collision detection"""
        # Horizontal movement
        self.rect.x += dx
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if dx > 0:
                    self.rect.right = rect.left
                elif dx < 0:
                    self.rect.left = rect.right

        # Vertical movement
        self.rect.y += dy
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if dy > 0:
                    self.rect.bottom = rect.top
                elif dy < 0:
                    self.rect.top = rect.bottom
        
        # Update animation
        self.update_animation()

    def set_sitting(self, sitting: bool):
        self.is_sitting = sitting
        if sitting:
            self.image = pygame.image.load(resource_path("assets/sprites/player/sitting.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (48, 80))
        else:
            # Return to idle front or whichever makes sense
            self.state = "idle_front"
            self.image = self.animations["idle_front"][0]
