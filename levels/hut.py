import pygame
from utils.fade import Fade
from entities.player import Player
from entities.lesnik import Lesnik
from ui.dialogue import DialogueBox
from ui.pause_menu import PauseMenu
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from map_loader import Map

class Hut:
    def __init__(self, screen):
        self.screen = screen
        self.map = Map("assets/maps/hut.tmx")
        self.font = pygame.font.SysFont("Arial", 24)
        self.bg_color = ("black")
        self.prompt_font = pygame.font.Font(None, 28)

        self.fade = Fade(screen, mode="in", speed=1)

        self.scene_state = "intro_dialogue"
        self.kitchen_target = (250 * self.map.scale_x, 140 * self.map.scale_y)  # adjust to match your Tiled coordinates
        self.lesnik_waiting = False
        self.can_interact_with_chair = False

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
                "Hello Batya. May I come in? It's cold outside.",
                "Be at home, traveler. I will not deny you anything — not a thing!",
                "Take a seat on the chair, I am preparing dinner."
            ]
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
        # Only allow movement when not in dialogue, sitting, or story scenes
        if (
            not self.dialogue.active
            and self.scene_state not in ["player_sitting", "talking_with_lesnik", "story_choice", "telling_story", "wolf_event"]
        ):
            dx, dy = self.player.get_movement(keys)
            self.player.move_player(dx, dy, self.map.collision_rects)
        else:
            # Freeze player (ensure sitting sprite is shown if applicable)
            if not self.player.set_sitting:
                self.player.set_sitting(True)


        self.dialogue.update(events)
        
        # --- Scene progression ---
        if self.scene_state == "intro_dialogue" and not self.dialogue.active:
            # Dialogue just finished, Lesnik should walk to kitchen
            self.lesnik.start_path([self.kitchen_target])
            self.scene_state = "lesnik_walking_to_kitchen"
            print("Lesnik is walking to the kitchen.")

        elif self.scene_state == "lesnik_walking_to_kitchen":
            if not self.lesnik.moving:
                # Lesnik reached the kitchen
                self.scene_state = "lesnik_waiting"
                self.lesnik_waiting = True
                print("Lesnik is now waiting in the kitchen.")

        self.update_camera()
        
        # Check for player interaction with chair
        self.can_interact_with_chair = self.lesnik_waiting and self.player_near_chair()
        
        if self.can_interact_with_chair:
            # Check for interaction key press
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self.scene_state = "player_sitting"
                    self.lesnik_waiting = False
                    
                    # Get chair position to move player to it
                    for obj in self.map.tmx_data.objects:
                        if obj.type.lower() == "chair_interact":
                            # Position player at the chair
                            self.player.rect.centerx = int(380 * self.map.scale_x)
                            self.player.rect.centery = int(132 * self.map.scale_y)
                            # when player sits
                            self.player.set_sitting(True)
                            break
                    
                    # Move Lesnik to table (adjust coordinates to match your table position)
                    table_target = (410 * self.map.scale_x, 120 * self.map.scale_y)
                    self.lesnik.start_path([table_target])
                    print("Player is sitting down. Lesnik is walking to the table.")
        
        # Check if Lesnik reached the table after player sits
        if self.scene_state == "player_sitting" and not self.lesnik.moving:
            # Make Lesnik face front (down)
            self.lesnik.direction = pygame.Vector2(0, 1)
            self.lesnik.state = "idle_front"
            self.lesnik.frame_index = 0
            self.dialogue.start([
                "Many stories I can tell, should you wish to listen. Many stories..."
            ])
            self.scene_state = "talking_with_lesnik"
            print("Lesnik reached the table. Starting dialogue.")
        
        # --- Story selection logic ---
        elif self.scene_state == "talking_with_lesnik" and not self.dialogue.active:
            # Dialogue just finished, show story choices
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
                                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus iaculis pretium sapien,",
                                "nec blandit metus eleifend at. Nulla viverra ex sed risus commodo, eget tincidunt felis dictum.",
                                "Aliquam erat volutpat. Curabitur ultricies varius justo, a bibendum nunc pretium et."
                            ])
                        elif choice == "Story 2":
                            self.dialogue.start([
                                "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium,",
                                "totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.",
                                "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit."
                            ])
                        elif choice == "Story 3":
                            self.dialogue.start([
                                "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum",
                                "deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident,",
                                "similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga."
                            ])
                        self.scene_state = "telling_story"
                        print(f"Started {choice}")

        elif self.scene_state == "telling_story" and not self.dialogue.active:
            if len(self.stories_heard) < 3:
                # Go back to choice menu
                self.scene_state = "story_choice"
            else:
                # All stories heard → wolf event
                pygame.mixer.music.load("assets/sfx/wolf_howl.mp3")
                pygame.mixer.music.play()

                self.dialogue.start(["Forgive me, my friend..."])
                self.scene_state = "wolf_event"
                print("All stories told. Wolf event triggered.")

        elif self.scene_state == "wolf_event" and not self.dialogue.active:
            # Lesnik leaves and returns with rifle
            rifle_target = (self.lesnik.rect.centerx - 100, self.lesnik.rect.centery)
            self.lesnik.start_path([rifle_target])
            self.scene_state = "lesnik_fetching_rifle"
            print("Lesnik left to fetch rifle.")


        if getattr(self, "_wants_return_menu", False) and not self.fade.active:
            return "menu"

    def update_camera(self):
        # Center camera on player
        self.camera_offset.x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_offset.y = self.player.rect.centery - SCREEN_HEIGHT // 2

        # Clamp camera to map boundaries
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

        # --- Depth-sorted entities ---
        drawables = []
        carpet_drawables = []  # Separate list for carpet (draw first)

        # Add player
        offset_player_rect = self.player.rect.copy()
        offset_player_rect.topleft -= self.camera_offset
        drawables.append((self.player.image, offset_player_rect.bottom, offset_player_rect))

        # Add Lesnik
        if self.lesnik:
            offset_lesnik_rect = self.lesnik.rect.copy()
            offset_lesnik_rect.topleft -= self.camera_offset
            drawables.append((self.lesnik.image, offset_lesnik_rect.bottom, offset_lesnik_rect))

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
                
                # Check if object is a carpet (always draw below everything)
                if obj.name and obj.name.lower() == "carpet":
                    carpet_drawables.append((image, obj_rect.bottom, obj_rect))
                else:
                    drawables.append((image, obj_rect.bottom, obj_rect))

        # Draw carpet first (no sorting needed, always on bottom)
        for image, _, rect in carpet_drawables:
            self.screen.blit(image, rect)

        # Sort and draw everything else
        drawables.sort(key=lambda d: d[1])
        for image, _, rect in drawables:
            self.screen.blit(image, rect)

        # Show interaction prompt
        if self.can_interact_with_chair:
            prompt_text = self.prompt_font.render("Press E to sit", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
            # Draw background for better visibility
            bg_rect = prompt_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            self.screen.blit(prompt_text, prompt_rect)

        # --- Story choice menu ---
        if self.scene_state == "story_choice":
            menu_x = SCREEN_WIDTH // 2
            menu_y = SCREEN_HEIGHT // 2 - 40
            line_spacing = 40

            for i, option in enumerate(self.story_options):
                prefix = "> " if i == self.selected_option else "  "
                text = self.font.render(prefix + option, True, (255, 255, 255))
                rect = text.get_rect(center=(menu_x, menu_y + i * line_spacing))
                self.screen.blit(text, rect)

        
        # Dialogue, UI, fade
        self.dialogue.draw()
        self.pause_menu.draw()
        self.fade.draw()
