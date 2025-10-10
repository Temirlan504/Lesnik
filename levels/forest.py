import pygame
from utils.fade import Fade
from utils.fog_of_war import FogOfWar
from entities.player import Player
from ui.dialogue import DialogueBox
from ui.pause_menu import PauseMenu
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from map_loader import Map

class Forest:
    def __init__(self, screen):
        self.screen = screen
        self.map = Map("assets/maps/forest.tmx")
        self.font = pygame.font.SysFont("Arial", 24)
        self.bg_color = ("black")

        self.fade = Fade(screen, mode="in", speed=1)

        self.fog_of_war = FogOfWar(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            light_radius=200,
            fog_alpha=250,
            light_gradient=100
        )

        # --- Player setup ---
        player_obj = self.map.get_object("Player")
        if player_obj:
            self.player = Player((0, 0))
            self.player.rect.centerx = int(player_obj.x * self.map.scale_x)
            self.player.rect.centery = int(player_obj.y * self.map.scale_y)
        else:
            print("⚠️ Warning: No player object found in map! Defaulting to center.")
            self.player = Player((self.map.width // 2, self.map.height // 2))

        self.player_group = pygame.sprite.GroupSingle(self.player)

        # Camera setup
        self.camera_offset = pygame.Vector2(0, 0)

        # Dialogue setup
        self.dialogue = DialogueBox(
            screen,
            self.font,
            lines=[
                "I'm so tired...",
                "I need to find somewhere to stay for the night."
            ]
        )

        self.pause_menu = PauseMenu(screen, self.font)

    def update(self, keys, events):
        self.fade.update()

        # Toggle pause menu on ESC
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.pause_menu.toggle()

        if self.pause_menu.active:
            action = self.pause_menu.update(events)
            if action == "Continue":
                self.pause_menu.toggle()
            elif action == "Main menu":
                self.fade.start("out", speed=12)
                self._wants_return_menu = True
                self.pause_menu.toggle()
            elif action == "Exit":
                return "_quit"

        # --- Player movement with collisions ---
        if not self.dialogue.active:
            dx, dy = self.player.get_movement(keys)
            self.move_player(dx, dy)  # ✅ use our new collision-aware movement

        self.dialogue.update(events)
        self.update_camera()

        if getattr(self, "_wants_return_menu", False) and not self.fade.active:
            return "menu"

        return None

    # Handle movement & collisions
    def move_player(self, dx, dy):
        player = self.player
        collision_rects = self.map.collision_rects  # Comes from your Tiled map

        # Horizontal movement
        player.rect.x += dx
        for rect in collision_rects:
            if player.rect.colliderect(rect):
                if dx > 0:  # moving right
                    player.rect.right = rect.left
                elif dx < 0:  # moving left
                    player.rect.left = rect.right

        # Vertical movement
        player.rect.y += dy
        for rect in collision_rects:
            if player.rect.colliderect(rect):
                if dy > 0:  # moving down
                    player.rect.bottom = rect.top
                elif dy < 0:  # moving up
                    player.rect.top = rect.bottom

    def update_camera(self):
        # Center camera on player
        self.camera_offset.x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_offset.y = self.player.rect.centery - SCREEN_HEIGHT // 2

        # Clamp camera to map boundaries
        self.camera_offset.x = max(0, min(self.camera_offset.x, self.map.width - SCREEN_WIDTH))
        self.camera_offset.y = max(0, min(self.camera_offset.y, self.map.height - SCREEN_HEIGHT))

    def draw(self):
        self.screen.fill(self.bg_color)
        self.map.draw(self.screen, camera_offset=self.camera_offset)

        # --- Depth-sorted entities ---
        drawables = []

        # Add player
        offset_player_rect = self.player.rect.copy()
        offset_player_rect.topleft -= self.camera_offset
        drawables.append((self.player.image, offset_player_rect.bottom, offset_player_rect))

        # Add map objects that can overlap (trees, buildings, etc.)
        for obj in self.map.tmx_data.objects:
            if hasattr(obj, "image") and obj.image:
                image = pygame.transform.scale(
                    obj.image,
                    (int(obj.width * self.map.scale_x), int(obj.height * self.map.scale_y))
                )
                obj_rect = pygame.Rect(
                    obj.x * self.map.scale_x - self.camera_offset.x,
                    obj.y * self.map.scale_y - self.camera_offset.y,
                    obj.width * self.map.scale_x,
                    obj.height * self.map.scale_y
                )
                drawables.append((image, obj_rect.bottom, obj_rect))

        # Sort and draw
        drawables.sort(key=lambda d: d[1])
        for image, _, rect in drawables:
            self.screen.blit(image, rect)

        # Dialogue, UI, fade
        self.fog_of_war.draw(self.screen, self.player.rect.center, self.camera_offset)
        self.dialogue.draw()
        self.pause_menu.draw()
        self.fade.draw()
