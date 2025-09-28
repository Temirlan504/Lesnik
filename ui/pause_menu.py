import pygame

class PauseMenu:
    def __init__(self, screen, font, options=None):
        self.screen = screen
        self.font = font
        self.options = options or ["Continue", "Main menu", "Exit"]
        self.selected = 0
        self.active = False

    def toggle(self):
        self.active = not self.active
        self.selected = 0  # reset selection when toggled

    def update(self, events):
        if not self.active:
            return None

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.options[self.selected]  # returns string
        return None

    def draw(self):
        if not self.active:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Draw menu options
        for i, option in enumerate(self.options):
            color = (200, 0, 0) if i == self.selected else (255, 255, 255)
            text_surface = self.font.render(option, True, color)
            x = self.screen.get_width() // 2 - text_surface.get_width() // 2
            y = self.screen.get_height() // 2 - 50 + i * 60
            self.screen.blit(text_surface, (x, y))
