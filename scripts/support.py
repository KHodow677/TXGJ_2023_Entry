import pygame
from csv import reader
from data.settings import tile_size
from os import walk

def import_csv_layout(path):
    terrain_map = []
    with open(path, newline='') as map:
        level = reader(map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))

    return terrain_map

def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_size()[0] / tile_size)
    tile_num_y = int(surface.get_size()[1] / tile_size)

    cut_tiles = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * tile_size
            y = row * tile_size
            new_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            new_surf.blit(surface, (0,0), pygame.Rect(x,y,tile_size,tile_size))
            cut_tiles.append(new_surf)

    return cut_tiles

def import_folder(path, scale=1):
    surface_list = []
    for _, __, image_files in walk(path):
        for image in image_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            if scale != 1:
                image_surf = pygame.transform.smoothscale(image_surf, (int(image_surf.get_width() * scale), int(image_surf.get_height() * scale)))
            surface_list.append(image_surf)

    return surface_list

def import_folder_audio(path):
    sound_list = []
    for _, __, sound_files in walk(path):
        for image in sound_files:
            full_path = path + '/' + image
            sound = pygame.mixer.Sound(full_path)
            sound_list.append(sound)

    return sound_list

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, frames, x, y, frame_duration, flip=False):
        super().__init__()
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.frame_duration = frame_duration
        self.frame_timer = 0
        self.flip = flip  # True to flip the sprite horizontally

    def update(self):
        self.frame_timer += 1
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            if self.flip:
                self.image = pygame.transform.flip(self.image, True, False)

