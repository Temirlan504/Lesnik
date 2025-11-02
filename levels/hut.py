import pygame
from utils.fade import Fade
from entities.player import Player
from entities.lesnik import Lesnik
from ui.dialogue import DialogueBox
from ui.pause_menu import PauseMenu
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from map_loader import Map
from settings import FPS

class Hut:
    def __init__(self, screen):
        self.screen = screen
        self.map = Map("assets/maps/hut.tmx")
        self.font = pygame.font.SysFont("Arial", 24)
        self.bg_color = ("black")
        self.prompt_font = pygame.font.Font(None, 28)
        self.fade = Fade(screen, mode="in", speed=1)

        self.rifle_sprite = pygame.image.load("assets/sprites/lesnik/rifle.png").convert_alpha()
        self.rifle_sprite = pygame.transform.scale(self.rifle_sprite, (10, 48))
        self.rifle_attached = False
        self.rifle_timer = 0

        self.credits_music_playing = False
        self.credits_start_time = 0  # Initialize here
        self.credits_lines = []  # Initialize here
        self.credits_font = None  # Initialize here

        self.scene_state = "intro_dialogue"
        self.kitchen_target = (250 * self.map.scale_x, 140 * self.map.scale_y)
        self.lesnik_waiting = False
        self.can_interact_with_chair = False

        # --- Hoodie sprite ---
        self.hoodie_sprite = pygame.image.load("assets/sprites/objects/hoodie.png").convert_alpha()
        self.hoodie_sprite = pygame.transform.scale(self.hoodie_sprite, (25*2.5, 23*2.5))
        self.hoodie_position = (350 * self.map.scale_x, 170 * self.map.scale_y)
        self.hoodie_visible = False

        # --- Plate with meat sprite ---
        self.plate_sprite = pygame.image.load("assets/sprites/objects/plate.png").convert_alpha()
        self.plate_sprite = pygame.transform.scale(self.plate_sprite, (32, 32))
        self.plate_position = (405 * self.map.scale_x, 123 * self.map.scale_y)
        self.plate_visible = False

        # Player spawn setup
        player_obj = self.map.get_object("Player")
        if player_obj:
            self.player = Player((0, 0))
            self.player.rect.centerx = int(player_obj.x * self.map.scale_x)
            self.player.rect.centery = int(player_obj.y * self.map.scale_y)
        else:
            print("⚠️ Warning: No player object found in hut map! Defaulting to center.")
            self.player = Player((self.map.width // 2, self.map.height // 2))

        self.player_group = pygame.sprite.GroupSingle(self.player)

        # Lesnik setup
        lesnik_obj = self.map.get_object("Lesnik")
        if lesnik_obj:
            self.lesnik = Lesnik((lesnik_obj.x * self.map.scale_x, lesnik_obj.y * self.map.scale_y))
        else:
            print("⚠️ Warning: No Lesnik spawner found in hut map!")
            self.lesnik = Lesnik((self.map.width // 2, self.map.height // 2 + 50))

        self.lesnik_group = pygame.sprite.GroupSingle(self.lesnik)

        # Camera setup
        self.camera_offset = pygame.Vector2(0, 0)

        # Dialogue setup
        self.dialogue = DialogueBox(
            screen,
            self.font,
            lines=[
                "Hello there, traveler.",
                "Be at home. I will not deny you anything — not a thing!",
                "Take a seat on the chair, I am preparing dinner."
            ]
        )
        self.dialogue.set_character(
            pygame.image.load("assets/sprites/lesnik/lesnik_portrait.png").convert_alpha(),
            position="left"
        )

        self.pause_menu = PauseMenu(screen, self.font)

    def update(self, keys, events):
        self.fade.update()
        self.lesnik_group.update()

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

        # Block player movement during dialogue or when sitting
        if (
            not self.dialogue.active
            and self.scene_state not in ["player_sitting", "talking_with_lesnik", "story_choice", "telling_story", "wolf_event"]
        ):
            dx, dy = self.player.get_movement(keys)
            self.player.move_player(dx, dy, self.map.collision_rects)

        self.dialogue.update(events)
        
        # --- Scene progression ---
        if self.scene_state == "intro_dialogue" and not self.dialogue.active:
            self.lesnik.start_path([self.kitchen_target])
            self.scene_state = "lesnik_walking_to_kitchen"
            print("Lesnik is walking to the kitchen.")

        elif self.scene_state == "lesnik_walking_to_kitchen":
            if not self.lesnik.moving:
                self.scene_state = "lesnik_waiting"
                self.lesnik_waiting = True
                print("Lesnik is now waiting in the kitchen.")

        self.update_camera()
        
        # Check for player interaction with chair
        self.can_interact_with_chair = self.lesnik_waiting and self.player_near_chair()
        
        if self.can_interact_with_chair:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self.scene_state = "player_sitting"
                    self.lesnik_waiting = False
                    
                    # Get chair position to move player to it
                    for obj in self.map.tmx_data.objects:
                        if obj.type.lower() == "chair_interact":
                            self.player.rect.centerx = int(380 * self.map.scale_x)
                            self.player.rect.centery = int(132 * self.map.scale_y)
                            self.player.set_sitting(True)
                            break
                    
                    table_target = (410 * self.map.scale_x, 120 * self.map.scale_y)
                    self.lesnik.start_path([table_target])
                    print("Player is sitting down. Lesnik is walking to the table.")
        
        # Check if Lesnik reached the table after player sits
        if self.scene_state == "player_sitting" and not self.lesnik.moving:
            self.lesnik.direction = pygame.Vector2(0, 1)
            self.lesnik.state = "idle_front"
            self.lesnik.frame_index = 0
            self.dialogue.start([
                "Many stories I can tell, should you wish to listen. Many stories..."
            ])
            self.dialogue.set_character(
                pygame.image.load("assets/sprites/lesnik/lesnik_portrait.png").convert_alpha(),
                position="left"
            )
            self.scene_state = "talking_with_lesnik"
            print("Lesnik reached the table. Starting dialogue.")
        
        # --- Story selection logic ---
        elif self.scene_state == "talking_with_lesnik" and not self.dialogue.active:
            self.scene_state = "story_choice"
            self.story_options = ["Story 1", "Story 2", "Story 3"]
            self.selected_option = 0
            self.stories_heard = set()
            print("Story selection started.")

        elif self.scene_state == "story_choice":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.story_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.story_options)
                    elif event.key == pygame.K_RETURN:
                        choice = self.story_options[self.selected_option]
                        self.stories_heard.add(choice)
                        
                        if choice == "Story 1":
                            self.dialogue.start([
                                "Ah, the beasts of this forest... they've long since ceased to fear me.",
                                "In my younger days, I would keep my rifle close, just in case.",
                                "But as the years went by, I learned their ways, and they learned mine.",
                                "Now, when the snow is deep and the nights are long, I leave meat at the edge of the woods.",
                                "The wolves come in silence, take what they need, and leave me in peace. We understand one another."
                            ])
                            self.dialogue.set_character(
                                pygame.image.load("assets/sprites/lesnik/lesnik_portrait.png").convert_alpha(),
                                position="left"
                            )
                        elif choice == "Story 2":
                            self.dialogue.start([
                                "On certain nights, the wind carries strange sounds through the pines.",
                                "It is then that travelers sometimes stumble upon my door — cold, weary, and half-mad from hunger.",
                                "I welcome them, as any man should. There is always soup on the stove, and a chair by the fire.",
                                "Yet by dawn, they are gone. The forest calls them back, one way or another.",
                                "No one truly leaves these woods unchanged."
                            ])
                            self.dialogue.set_character(
                                pygame.image.load("assets/sprites/lesnik/lesnik_portrait.png").convert_alpha(),
                                position="left"
                            )
                        elif choice == "Story 3":
                            self.dialogue.start([
                                "Once, there was a hunter who fancied himself the master of this place.",
                                "He boasted that no beast could match his aim, nor any man his courage.",
                                "I warned him, gently, that pride has a way of echoing in the trees.",
                                "When spring came, I found his hat hanging on a branch — not a mark of blood upon it.",
                                "Since then, the forest has been quiet, as if content once more."
                            ])
                            self.dialogue.set_character(
                                pygame.image.load("assets/sprites/lesnik/lesnik_portrait.png").convert_alpha(),
                                position="left"
                            )

                        self.scene_state = "telling_story"
                        print(f"Started {choice}")

        elif self.scene_state == "telling_story" and not self.dialogue.active:
            if len(self.stories_heard) < 3:
                self.scene_state = "story_choice"
            else:
                pygame.mixer.music.load("assets/sfx/wolf_howl.mp3")
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(1)
                self.dialogue.start([
                    "Suddenly, outside the hut, a chilling howl pierces the air..."
                ])
                self.dialogue.start([
                    "Forgive me, friend...",
                ])
                self.dialogue.set_character(
                    pygame.image.load("assets/sprites/lesnik/lesnik_portrait.png").convert_alpha(),
                    position="left"
                )
                self.scene_state = "wolf_event"
                print("All stories told. Wolf event triggered.")

        elif self.scene_state == "wolf_event" and not self.dialogue.active:
            door_obj = self.map.get_object("Door")
            if door_obj:
                door_target = (door_obj.x * self.map.scale_x, door_obj.y * self.map.scale_y)
            else:
                door_target = (self.lesnik.rect.centerx, self.lesnik.rect.centery + 400)

            path_points = [
                (self.lesnik.rect.centerx - 120, self.lesnik.rect.centery),
                door_target
            ]
            self.lesnik.start_path(path_points)
            self.lesnik_leave_time = pygame.time.get_ticks()
            self.scene_state = "lesnik_fetching_rifle"
            print("Lesnik leaves to fetch rifle.")
        
        elif self.scene_state == "lesnik_fetching_rifle":
            # Wait for Lesnik to finish moving to the door first
            if not self.lesnik.moving:
                # Lesnik has reached the door, now start the timer
                if not hasattr(self, 'lesnik_at_door_time'):
                    self.lesnik_at_door_time = pygame.time.get_ticks()
                    print("Lesnik reached the door. Waiting 7 seconds...")
                
                # Check if 7 seconds have passed since reaching the door
                elapsed_at_door = pygame.time.get_ticks() - self.lesnik_at_door_time
                if elapsed_at_door >= 7000:
                    # Now spawn him with rifle at door position minus 70 in y
                    door_obj = self.map.get_object("Door")
                    if door_obj:
                        return_pos = (door_obj.x * self.map.scale_x, (door_obj.y - 70) * self.map.scale_y)
                    else:
                        return_pos = (self.lesnik.rect.centerx, self.lesnik.rect.centery - 70)

                    self.lesnik.rect.center = return_pos
                    self.lesnik.image = pygame.image.load("assets/sprites/lesnik/idle_back/0.png").convert_alpha()
                    self.rifle_attached = True
                    
                    # Make him face forward/down
                    self.lesnik.direction = pygame.Vector2(0, 1)
                    self.lesnik.state = "idle_front"
                    self.lesnik.frame_index = 0

                    self.scene_state = "lesnik_returned_with_rifle"
                    print(f"7 seconds passed. Lesnik returned with rifle and is standing near the door.")
                    del self.lesnik_at_door_time  # Clean up the timer variable
            
        elif self.scene_state == "lesnik_returned_with_rifle":
            self.lesnik.image = pygame.image.load("assets/sprites/lesnik/idle_back/0.png").convert_alpha()
            self.lesnik.direction = pygame.Vector2(0, -1)
            self.lesnik.state = "idle_back"
            self.lesnik.frame_index = 0
            self.rifle_attached = True

            self.dialogue.start([
                "Friends want to eat... let's go outside, pal."
            ])
            self.dialogue.set_character(
                pygame.image.load("assets/sprites/lesnik/lesnik_portrait.png").convert_alpha(),
                position="left"
            )
            self.scene_state = "final_fade_to_black"
            print("Lesnik with rifle, starting final dialogue.")

        elif self.scene_state == "final_fade_to_black" and not self.dialogue.active:
            self.fade.start("out", speed=2)
            self.scene_state = "fade_dark"

        elif self.scene_state == "fade_dark" and not self.fade.active:
            # Play the gunshot while screen is fully black
            pygame.mixer.Sound("assets/sfx/shotgun_fire.mp3").play()
            pygame.time.wait(1500)

            print("Shot fired — transitioning directly to credits.")

            # Hide player completely and add hoodie sprite
            self.hoodie_visible = True
            self.plate_visible = True
            self.player.rect.center = (-9999, -9999)
            self.player.image = pygame.Surface((1, 1), pygame.SRCALPHA)

            # Move Lesnik back to table and change to eating sprite
            table_position = (410 * self.map.scale_x, 120 * self.map.scale_y)
            self.lesnik.rect.center = table_position
            self.lesnik.image = pygame.image.load("assets/sprites/lesnik/idle_front/0.png").convert_alpha()
            self.lesnik.state = "eating"
            self.lesnik.frame_index = 0

            # Initialize credits data
            self.credits_lines = [
                "A Tale of the Woods",
                "Inspired by the 'King and Jester' - song 'Lesnik'",
                "",
                "Developed by Obelus STEM (YouTube)",
                "",
                "If you liked the game, consider supporting me on YouTube!",
            ]
            self.credits_font = pygame.font.Font(None, 36)
            self.credits_start_time = pygame.time.get_ticks()

            pygame.mixer.music.load("assets/music/outro_theme.mp3")
            pygame.mixer.music.play()
            self.credits_music_playing = True

            # Go straight to credits
            self.scene_state = "credits_scene"
            self.fade.start("in", speed=2)
            print("Credits scene initialized immediately after fade to black.")

        elif self.scene_state == "credits_scene":
            if self.credits_music_playing and not pygame.mixer.music.get_busy():
                print("Outro finished. Returning to menu.")
                self.scene_state = "return_to_menu"

        elif self.scene_state == "return_to_menu" and not self.fade.active:
            return "menu"

        if getattr(self, "_wants_return_menu", False) and not self.fade.active:
            return "menu"

    def update_camera(self):
        self.camera_offset.x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_offset.y = self.player.rect.centery - SCREEN_HEIGHT // 2

        self.camera_offset.x = max(0, min(self.camera_offset.x, self.map.width - SCREEN_WIDTH))
        self.camera_offset.y = max(0, min(self.camera_offset.y, self.map.height - SCREEN_HEIGHT))

    def player_near_chair(self):
        for obj in self.map.tmx_data.objects:
            if obj.type.lower() == "chair_interact":
                chair_rect = pygame.Rect(
                    obj.x * self.map.scale_x,
                    obj.y * self.map.scale_y,
                    obj.width * self.map.scale_x,
                    obj.height * self.map.scale_y
                )
                if self.player.rect.colliderect(chair_rect):
                    return True
        return False

    def draw(self):
        self.screen.fill(self.bg_color)
        self.map.draw(self.screen, camera_offset=self.camera_offset)

        drawables = []
        carpet_drawables = []

        # Add player
        offset_player_rect = self.player.rect.copy()
        offset_player_rect.topleft -= self.camera_offset
        drawables.append((self.player.image, offset_player_rect.bottom, offset_player_rect))

        # Add Lesnik
        if self.lesnik:
            offset_lesnik_rect = self.lesnik.rect.copy()
            offset_lesnik_rect.topleft -= self.camera_offset
            drawables.append((self.lesnik.image, offset_lesnik_rect.bottom, offset_lesnik_rect))

            # --- Rifle attachment ---
            if getattr(self, "rifle_attached", False):
                rifle_offset = (
                    offset_lesnik_rect.centerx + 25,  # tweak horizontal offset as needed
                    offset_lesnik_rect.centery - 20   # tweak vertical offset
                )
                self.screen.blit(self.rifle_sprite, rifle_offset)

        # Add map objects
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
                
                if obj.name and obj.name.lower() == "carpet":
                    carpet_drawables.append((image, obj_rect.bottom, obj_rect))
                else:
                    drawables.append((image, obj_rect.bottom, obj_rect))

        for image, _, rect in carpet_drawables:
            self.screen.blit(image, rect)

        drawables.sort(key=lambda d: d[1])
        for image, _, rect in drawables:
            self.screen.blit(image, rect)

        # Show interaction prompt
        if self.can_interact_with_chair:
            prompt_text = self.prompt_font.render("Press E to sit", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            bg_rect = prompt_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            self.screen.blit(prompt_text, prompt_rect)

        # Story choice menu
        if self.scene_state == "story_choice":
            menu_x = SCREEN_WIDTH // 2
            menu_y = SCREEN_HEIGHT // 2 - 40
            line_spacing = 40

            for i, option in enumerate(self.story_options):
                prefix = "> " if i == self.selected_option else "  "
                text = self.font.render(prefix + option, True, (255, 255, 255))
                rect = text.get_rect(center=(menu_x, menu_y + i * line_spacing))
                self.screen.blit(text, rect)
        
        # --- Credits cinematic ---
        if self.scene_state == "credits_scene":
            # Move camera to right-upper corner
            cinematic_offset = pygame.Vector2(self.map.width - SCREEN_WIDTH, 0)

            # Draw map first
            self.map.draw(self.screen, camera_offset=cinematic_offset)

            # Draw Lesnik below table via depth sort
            self.rifle_attached = False  # Hide rifle during credits
            self.lesnik.image = pygame.image.load("assets/sprites/lesnik/idle_front/0.png").convert_alpha()
            self.lesnik.image = pygame.transform.scale(self.lesnik.image, (49, 87))

            drawables = []

            # Collect all map objects again (for depth order)
            for obj in self.map.tmx_data.objects:
                if hasattr(obj, "image") and obj.image:
                    image = pygame.transform.scale(
                        obj.image,
                        (int(obj.width * self.map.scale_x), int(obj.height * self.map.scale_y))
                    )
                    obj_rect = pygame.Rect(
                        obj.x * self.map.scale_x - cinematic_offset.x,
                        obj.y * self.map.scale_y - cinematic_offset.y,
                        obj.width * self.map.scale_x,
                        obj.height * self.map.scale_y
                    )
                    drawables.append((image, obj_rect.bottom, obj_rect))

            # Add Lesnik with his depth
            offset_lesnik_rect = self.lesnik.rect.copy()
            offset_lesnik_rect.topleft -= cinematic_offset
            drawables.append((self.lesnik.image, offset_lesnik_rect.bottom, offset_lesnik_rect))

            # Sort and draw
            drawables.sort(key=lambda d: d[1])
            for image, _, rect in drawables:
                self.screen.blit(image, rect)

            # Draw hoodie sprite if visible
            if self.hoodie_visible:
                hoodie_rect = self.hoodie_sprite.get_rect()
                hoodie_rect.topleft = (
                    self.hoodie_position[0] - cinematic_offset.x,
                    self.hoodie_position[1] - cinematic_offset.y
                )
                self.screen.blit(self.hoodie_sprite, hoodie_rect)

            # Draw plate sprite if visible
            if self.plate_visible:
                plate_rect = self.plate_sprite.get_rect()
                plate_rect.topleft = (
                    self.plate_position[0] - cinematic_offset.x,
                    self.plate_position[1] - cinematic_offset.y
                )
                self.screen.blit(self.plate_sprite, plate_rect)

            # Draw credits text
            for i, line in enumerate(self.credits_lines):
                text = self.credits_font.render(line, True, (255, 255, 255))
                rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 40 - 60))
                self.screen.blit(text, rect)

            # Cinematic letterboxing
            bar_height = 80
            pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, bar_height))
            pygame.draw.rect(self.screen, (0, 0, 0), (0, SCREEN_HEIGHT - bar_height, SCREEN_WIDTH, bar_height))
        
        self.dialogue.draw()
        self.pause_menu.draw()
        self.fade.draw()
