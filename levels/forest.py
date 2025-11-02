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
        self.prompt_font = pygame.font.Font(None, 28)

        self.fade = Fade(screen, mode="in", speed=1)

        self.fog_of_war = FogOfWar(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            light_radius=200,
            fog_alpha=230,
            light_gradient=10
        )

        # --- Background music ---
        pygame.mixer.music.load("assets/music/forest_ambience.mp3")
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)  # Loop indefinitely

        # --- Door setup ---
        door_obj = self.map.get_object("Door")
        self.door_triggered = False
        self.show_door_prompt = False

        if door_obj:
            self.door_rect = pygame.Rect(
                door_obj.x * self.map.scale_x,
                door_obj.y * self.map.scale_y,
                door_obj.width * self.map.scale_x,
                door_obj.height * self.map.scale_y
            )
        else:
            self.door_rect = None
            print("⚠️ No Door object found in map.")


        # --- Player spawn setup ---
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
        self.dialogue.set_character(
            pygame.image.load("assets/sprites/player/player_portrait.png").convert_alpha(),
            position="left"
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
            self.player.move_player(dx, dy, self.map.collision_rects)

        self.dialogue.update(events)
        self.update_camera()

        if getattr(self, "_wants_return_menu", False) and not self.fade.active:
            return "menu"
        
        # Check for door interaction
        if self.door_rect and self.player.rect.colliderect(self.door_rect):
            if not self.door_triggered:
                self.dialogue.start([
                    "This looks like a nice hut.",
                    "Maybe I can rest there for the night."
                ])
                self.dialogue.set_character(
                    pygame.image.load("assets/sprites/player/player_portrait.png").convert_alpha(),
                    position="left"
                )
                self.door_triggered = True

            # show prompt only after dialogue is done
            elif not self.dialogue.active:
                self.show_door_prompt = True
                # check for "E" press to enter
                if keys[pygame.K_e] and not self.fade.active:
                    pygame.mixer.music.stop()
                    pygame.mixer.Sound("assets/sfx/door_crackle.mp3").play()
                    self.fade.start("out", speed=3)
                    self._wants_transition_hut = True
        else:
            self.show_door_prompt = False

        if getattr(self, "_wants_transition_hut", False) and not self.fade.active:
            return "hut"

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

        # --- Draw door prompt ---
        if self.show_door_prompt and self.door_rect:
            prompt_text = self.prompt_font.render("Press E to enter", True, (255, 255, 255))
            text_rect = prompt_text.get_rect(center=(
                self.door_rect.centerx,
                self.door_rect.top - 20  # place slightly above the door
            ))
            self.screen.blit(prompt_text, text_rect)
