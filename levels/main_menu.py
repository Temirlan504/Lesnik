import pygame
from utils.fade import Fade

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 40)
        self.options = ["Start Game", "Quit"]
        self.selected = 0
        self.fade = Fade(screen, mode="in", speed=12)  # fade in menu
        self._starting_game = False

    def update(self, keys, events):
        # update fade (so it fades in if needed)
        self.fade.update()

        for event in events:
            if event.type == pygame.KEYDOWN and not self._starting_game:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.options[self.selected] == "Start Game":
                        # start fade-out and mark intent to switch
                        self.fade.start("out", speed=12)
                        self._starting_game = True
                    elif self.options[self.selected] == "Quit":
                        return "_quit"  # special flag handled in main.py

        # If fade finished and we wanted to start game, return transition
        if self._starting_game and not self.fade.active:
            return "forest"

        return None

    def draw(self):
        self.screen.fill((0, 0, 0))
        title = self.font.render("Lesnik", True, (200, 0, 0))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))

        for i, option in enumerate(self.options):
            color = (200, 0, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            self.screen.blit(text, (
                self.screen.get_width()//2 - text.get_width()//2,
                250 + i*60
            ))

        # draw fade overlay on top (will be transparent if fade completed)
        self.fade.draw()
