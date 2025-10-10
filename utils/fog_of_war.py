import pygame

class FogOfWar:
    def __init__(self, screen_size, light_radius=150, fog_alpha=220, light_gradient=80):
        self.width, self.height = screen_size
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.fog_color = (0, 0, 0, fog_alpha)
        self.light_radius = light_radius
        self.light_gradient = light_gradient

    def draw(self, screen, player_pos, camera_offset):
        """Draw fog overlay centered around the player's position."""
        # Fill with solid fog color
        self.surface.fill(self.fog_color)

        # Player position relative to camera
        player_screen_x = int(player_pos[0] - camera_offset.x)
        player_screen_y = int(player_pos[1] - camera_offset.y)

        # Draw a transparent circle (light area)
        # We'll use a gradient to soften the edges
        for r in range(self.light_radius, 0, -2):
            # Alpha gradually increases outward (more fog near edge)
            alpha = int((r / self.light_radius) * self.fog_color[3])
            color = (0, 0, 0, alpha)
            pygame.draw.circle(self.surface, color, (player_screen_x, player_screen_y), r)

        # Finally, darken the screen with the fog overlay
        screen.blit(self.surface, (0, 0))
