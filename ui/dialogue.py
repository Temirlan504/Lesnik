import pygame

class DialogueBox:
    def __init__(self, screen, font, lines=None):
        self.screen = screen
        self.font = font
        self.active = True
        self.lines = lines or []
        self.current_line = 0
        # Define dialogue box rectangle
        self.box_rect = pygame.Rect(0, self.screen.get_height() - 100,
                                    self.screen.get_width(), 100)

    def update(self, events):
        if not self.active:
            return

        for event in events:
            # Press Enter to advance
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.advance()
            # Left click inside dialogue box to advance
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.box_rect.collidepoint(event.pos):
                    self.advance()

    def advance(self):
        self.current_line += 1
        if self.current_line >= len(self.lines):
            self.active = False

    def draw(self):
        if not self.active:
            return
        # Draw dialogue box
        pygame.draw.rect(self.screen, (0, 0, 0), self.box_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), self.box_rect, 2)

        # Draw text
        if self.current_line < len(self.lines):
            text_surface = self.font.render(self.lines[self.current_line], True, (255, 255, 255))
            self.screen.blit(text_surface, (20, self.screen.get_height() - 70))

        # Draw arrow prompt
        arrow_surface = self.font.render(">", True, (255, 255, 255))
        arrow_x = self.screen.get_width() - 40
        arrow_y = self.screen.get_height() - 50
        self.screen.blit(arrow_surface, (arrow_x, arrow_y))
