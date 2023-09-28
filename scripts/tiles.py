from scripts.support import import_folder
import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y) -> None:
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, shift) -> None:
        self.rect.x += shift

class StaticTile(Tile):
    def __init__(self, size, x, y, surface) -> None:
        super().__init__(size, x, y)
        self.image = surface

    def update(self, shift) -> None:
        self.rect.x += shift

class CloudTile(Tile):
    def __init__(self, size, x, y, surface, shift_rate = 1) -> None:
        super().__init__(size, x, y)
        self.image = surface
        self.shift_rate = shift_rate

    def update(self, shift) -> None:
        self.rect.x += shift * self.shift_rate

class Crate(Tile):
    def __init__(self, size, x, y, surface) -> None:
        super().__init__(size, x, y)
        self.image = surface
        offset_y = y + size
        self.rect = self.image.get_rect(bottomleft=(x, offset_y))

class AnimatedTile(Tile):
    def __init__(self, size, x, y, frames):
        super().__init__(size, x, y)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.anim_speed = 0.30

    def animate(self) -> None:
        self.frame_index += self.anim_speed
        if (self.frame_index >= len(self.frames)):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, shift) -> None:
        self.animate()
        self.rect.x += shift

class Coin(AnimatedTile):
    def __init__(self, size, x, y, frames):
        super().__init__(size, x, y, frames)
        center_x = x + int(size / 2)
        center_y = y + int(size / 2)
        self.rect = self.image.get_rect(center=(center_x, center_y))