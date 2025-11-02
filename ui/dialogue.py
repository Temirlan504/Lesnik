import pygame
import textwrap

class DialogueBox:
    def __init__(self, screen, font, lines=None):
        self.screen = screen
        self.font = font
        self.active = True
        self.lines = lines or []
        self.current_line = 0
        self.visible_text = ""
        self.char_index = 0
        self.typing_speed = 2
        self.last_update_time = 0
        self.finished_typing = False

        # Dialogue box rectangle
        self.box_rect = pygame.Rect(
            40,
            self.screen.get_height() - 160,
            self.screen.get_width() - 80,
            140
        )

        # Character portrait
        self.character_image = None
        self.character_alpha = 0
        self.character_position = "right"

        # Arrow animation
        self.arrow_alpha = 255
        self.arrow_fade_direction = -5

    def set_character(self, image, position="right"):
        """Sets the character portrait (optional)."""
        self.character_image = image
        self.character_alpha = 0
        self.character_position = position

    def update(self, events):
        if not self.active:
            return

        # Typing effect
        current_time = pygame.time.get_ticks()
        if not self.finished_typing and current_time - self.last_update_time > 20:
            self.last_update_time = current_time
            self.char_index += self.typing_speed
            full_text = self.lines[self.current_line]
            if self.char_index >= len(full_text):
                self.char_index = len(full_text)
                self.finished_typing = True
            self.visible_text = full_text[:self.char_index]

        # Character fade-in
        if self.character_image and self.character_alpha < 255:
            self.character_alpha = min(255, self.character_alpha + 8)

        # Input handling
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.advance()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.box_rect.collidepoint(event.pos):
                    self.advance()

        # Arrow animation
        self.arrow_alpha += self.arrow_fade_direction
        if self.arrow_alpha <= 50 or self.arrow_alpha >= 255:
            self.arrow_fade_direction *= -1

    def advance(self):
        if not self.finished_typing:
            self.visible_text = self.lines[self.current_line]
            self.finished_typing = True
            self.char_index = len(self.visible_text)
            return

        self.current_line += 1
        if self.current_line >= len(self.lines):
            self.active = False
        else:
            self.char_index = 0
            self.visible_text = ""
            self.finished_typing = False

    def draw(self):
        if not self.active:
            return

        # Draw dialogue box (semi-transparent)
        s = pygame.Surface((self.box_rect.width, self.box_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (self.box_rect.x, self.box_rect.y))
        pygame.draw.rect(self.screen, (255, 255, 255), self.box_rect, 2, border_radius=10)

        text_offset_x = self.box_rect.x + 20

        # Draw large cinematic portrait
        if self.character_image:
            img = self.character_image.copy()
            img.set_alpha(self.character_alpha)
            img_rect = img.get_rect()

            # Scale portrait to fit height
            target_height = int(self.screen.get_height() / 5.5)
            scale = target_height / img_rect.height
            img = pygame.transform.scale(
                img,
                (int(img_rect.width * scale), int(img_rect.height * scale))
            )
            img_rect = img.get_rect()

            # Slight overlap with dialogue box
            if self.character_position == "right":
                img_rect.bottomright = (self.screen.get_width() - 40, self.box_rect.top + 30)
                text_offset_x = self.box_rect.x + 40
            else:
                img_rect.bottomleft = (40, self.box_rect.top + 30)
                text_offset_x = self.box_rect.x + img_rect.width + 50

            self.screen.blit(img, img_rect)

        # Draw text
        if self.current_line < len(self.lines):
            max_text_width = self.box_rect.width - 60
            if self.character_image and self.character_position == "left":
                max_text_width -= img_rect.width // 2

            chars_per_line = max_text_width // 12
            wrapped = textwrap.wrap(self.visible_text, width=chars_per_line)
            for i, line in enumerate(wrapped):
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(
                    text_surface,
                    (text_offset_x, self.box_rect.y + 20 + i * 28)
                )

        # Draw arrow prompt
        if self.finished_typing:
            arrow_surface = self.font.render(">", True, (255, 255, 255))
            arrow_surface.set_alpha(self.arrow_alpha)
            arrow_x = self.box_rect.right - 30
            arrow_y = self.box_rect.bottom - 30
            self.screen.blit(arrow_surface, (arrow_x, arrow_y))

    def start(self, text_or_lines):
        """Start a new dialogue sequence."""
        if isinstance(text_or_lines, str):
            self.lines = [text_or_lines]
        else:
            self.lines = list(text_or_lines)
        self.current_line = 0
        self.visible_text = ""
        self.char_index = 0
        self.finished_typing = False
        self.active = True
