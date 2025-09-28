import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from levels.main_menu import MainMenu
from levels.forest import Forest

class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.scene_classes = {
            "menu": MainMenu,
            "forest": Forest,
            # "hut": Hut,  # later
        }
        self.current_scene = self.scene_classes["menu"](screen)
        self._should_quit = False

    def update(self, keys, events):
        next_scene = self.current_scene.update(keys, events)

        if next_scene == "_quit":
            self._should_quit = True
        elif next_scene and next_scene in self.scene_classes:
            # Create a fresh instance of the new scene
            self.current_scene = self.scene_classes[next_scene](self.screen)

    def draw(self):
        self.current_scene.draw()

    def should_quit(self):
        return self._should_quit


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Lesnik")
        self.clock = pygame.time.Clock()
        self.running = True
        self.manager = SceneManager(self.screen)

    def run(self):
        while self.running:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

            # Update & draw
            self.manager.update(keys, events)

            if self.manager.should_quit():
                self.running = False
                pygame.quit()
                sys.exit()

            self.manager.draw()

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()
