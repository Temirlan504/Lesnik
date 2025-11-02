import pygame
import sys, os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from levels.main_menu import MainMenu
from levels.forest import Forest
from levels.hut import Hut
from utils.resource_path import resource_path

class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.scene_classes = {
            "menu": MainMenu,
            "forest": Forest,
            "hut": Hut
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
        pygame.display.set_icon(pygame.image.load(resource_path("assets/sprites/lesnik/lesnik_portrait.png")))
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
    try:
        game = Game()
        game.run()
    except Exception as e:
        import traceback
        print("An error occurred.")
        # You can log it to a file:
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        # Or show an in-game popup using pygame
        pygame.quit()
        sys.exit()
