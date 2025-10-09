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
        
        # ✅ Build collision rects once during initialization
        self.collision_rects = self.get_collision_rects()

    def get_collision_rects(self):
        """Extract all collision rectangles from the map"""
        collision_rects = []
        
        for obj in self.tmx_data.objects:
            # Check if this object is a collision object
            if obj.name == "Collision" or obj.type == "Collision":
                rect = pygame.Rect(
                    obj.x * self.scale_x,
                    obj.y * self.scale_y,
                    obj.width * self.scale_x,
                    obj.height * self.scale_y
                )
                collision_rects.append(rect)
        
        return collision_rects

    def draw(self, surface, camera_offset=(0, 0)):
        """Draw all visible layers (tiles + objects) with camera offset"""
        offset_x, offset_y = camera_offset

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    if image:
                        image = pygame.transform.scale(
                            image,
                            (int(self.tile_width * self.scale_x), int(self.tile_height * self.scale_y))
                        )
                        surface.blit(image, (x * TILE_SIZE - offset_x, y * TILE_SIZE - offset_y))

            elif isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    # ✅ Skip collision objects - don't draw them
                    if obj.name == "Collision" or obj.type == "Collision":
                        continue
                    
                    if hasattr(obj, "image") and obj.image:
                        image = pygame.transform.scale(
                            obj.image,
                            (int(obj.width * self.scale_x), int(obj.height * self.scale_y))
                        )
                        surface.blit(image, (obj.x * self.scale_x - offset_x, obj.y * self.scale_y - offset_y))
                    else:
                        rect = pygame.Rect(
                            obj.x * self.scale_x - offset_x,
                            obj.y * self.scale_y - offset_y,
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
    