import pygame
import pytmx
from settings import TILE_SIZE

class Map:
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight

        # Calculate scale factor automatically
        self.scale_x = TILE_SIZE / self.tile_width
        self.scale_y = TILE_SIZE / self.tile_height

        # Optional: map dimensions (for camera, bounds, etc.)
        self.width = self.tmx_data.width * TILE_SIZE
        self.height = self.tmx_data.height * TILE_SIZE

    def draw(self, surface):
        """Draw all visible layers (tiles + objects)"""
        for layer in self.tmx_data.visible_layers:
            # Tile layers
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    if image:
                        image = pygame.transform.scale(
                            image, (int(self.tile_width * self.scale_x), int(self.tile_height * self.scale_y))
                        )
                        surface.blit(image, (x * TILE_SIZE, y * TILE_SIZE))

            # Object layers
            elif isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    if hasattr(obj, "image") and obj.image:
                        image = pygame.transform.scale(
                            obj.image, (int(obj.width * self.scale_x), int(obj.height * self.scale_y))
                        )
                        surface.blit(image, (obj.x * self.scale_x, obj.y * self.scale_y))
                    else:
                        # placeholder rectangle
                        rect = pygame.Rect(
                            obj.x * self.scale_x,
                            obj.y * self.scale_y,
                            obj.width * self.scale_x,
                            obj.height * self.scale_y
                        )
                        pygame.draw.rect(surface, (255, 0, 0), rect, 1)


    def get_object(self, name):
        """Helper to get object by name"""
        for obj in self.tmx_data.objects:
            if obj.name == name:
                return obj
        return None
