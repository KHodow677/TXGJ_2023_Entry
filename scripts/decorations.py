import pygame
import random
from data.settings import screen_width
from scripts.tiles import StaticTile, CloudTile
from scripts.support import import_folder

class Sky:
    def __init__(self) -> None:
        self.image = pygame.image.load('graphics/decorations/blue_background.png').convert_alpha()

    def draw(self, surface) -> None:
        surface.blit(self.image, (0,0))

class Water:
    def __init__(self, top, level_width) -> None:
        water_start = -screen_width
        water_tile_width = 192
        tile_x_amount = int((level_width + screen_width * 2)/ water_tile_width)
        self.water_sprites = pygame.sprite.Group()

        for tile in range(tile_x_amount):
            x = water_start + (tile * water_tile_width)
            y = top
            water_surf = pygame.image.load('graphics/decorations/water.png').convert_alpha()
            sprite = StaticTile(192, x, y, water_surf)
            self.water_sprites.add(sprite)

    def draw(self, surface, shift) -> None:
        self.water_sprites.update(shift)
        self.water_sprites.draw(surface)

class Clouds:
    def __init__(self, horizon, level_width, cloud_number):
        cloud_surf_list = import_folder('graphics/decorations/clouds', scale=0.75)
        min_x = -screen_width
        max_x = level_width + screen_width
        min_y = 0
        max_y = horizon
        self.cloud_sprites = pygame.sprite.Group()

        for cloud in range(cloud_number):
            cloud = random.choice(cloud_surf_list)
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            shift_rate = random.uniform(0.4, 0.7)
            sprite = CloudTile(0, x, y, cloud, shift_rate)
            self.cloud_sprites.add(sprite)

    def draw(self, surface, shift) -> None:
        self.cloud_sprites.update(shift)
        self.cloud_sprites.draw(surface)
