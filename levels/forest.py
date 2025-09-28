import pygame
from utils import Fade
from entities.player import Player
from ui.dialogue import DialogueBox
from ui.pause_menu import PauseMenu
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Forest:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 24)
        self.bg_color = ("black")

        self.fade = Fade(screen, mode="in", speed=1)

        # Player setup
        self.player = Player((SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.player_group = pygame.sprite.GroupSingle(self.player)

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
                self.pause_menu.toggle()  # close menu immediately
            elif action == "Exit":
                return "_quit"

        # Freeze player during dialogue
        if not self.dialogue.active:
            self.player.update(keys)

        # Update dialogue first
        self.dialogue.update(events)

        if getattr(self, "_wants_return_menu", False) and not self.fade.active:
            return "menu"

        return None

    def draw(self):
        # Background
        self.screen.fill(self.bg_color)

        # Draw player
        self.player_group.draw(self.screen)

        # Dialogue
        self.dialogue.draw()

        # Draw pause menu
        self.pause_menu.draw()

        # Fade overlay
        self.fade.draw()
