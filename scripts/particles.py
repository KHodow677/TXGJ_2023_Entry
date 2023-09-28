from typing import Any
import pygame
from scripts.support import import_folder

class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, pos, frames) -> None:
        super().__init__()
        self.frame_index = 0
        self.animation_speed = 0.5
        self.frames = frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def animate(self) -> None:
        self.frame_index += self.animation_speed

        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self, shift) -> None:
        self.animate()
        self.rect.x += shift
        self.rect.y += shift