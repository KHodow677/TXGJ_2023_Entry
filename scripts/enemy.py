import pygame
from scripts.tiles import AnimatedTile
from random import randint
from scripts.support import import_folder

class Enemy(pygame.sprite.Sprite):
    def __init__(self, size, x, y, animations):
        super().__init__()
        self.animations = animations
        self.frame_index = 0
        self.animation_speed = 1
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Animation Attributes
        self.anim_speed = 1
        self.rect.y += size - self.image.get_size()[1] + 10
        self.speed = randint(2, 4)

        self.status = 'idle'
        self.is_reverse = False
        self.idle_timer = 0
        self.idle_duration = randint(60, 300)
        self.run_duration = randint(60, 300)
        self.attack_duration = 60
        self.attack_time = 0

    def animate(self) -> None:
        animation = self.animations[self.status]

        # Loop over frame index
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if not self.is_reverse:
            self.image = image
        else:
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image

    def move(self) -> None:
        if self.status == 'run':
            self.rect.x += self.speed

    def attack_timer(self) -> None:
        if self.status == 'attack':
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_duration:
                self.status = 'run'
                self.set_speed_from_reverse_state(2, 4)
                self.idle_timer = 0
                self.idle_duration = randint(60, 300)
                self.run_timer = 0

    def reverse(self) -> None:
        self.speed *= -1
        self.is_reverse = not self.is_reverse

    def set_speed_from_reverse_state(self, low, high) -> None:
        if self.is_reverse:
            self.speed = -randint(low, high)
        else:
            self.speed = randint(low, high)

    def update(self, shift):
        self.rect.x += shift

        self.animate()
        self.move()
        self.attack_timer()

        if self.status == 'idle':
            self.idle_timer += 1
            if self.idle_timer >= self.idle_duration:
                self.status = 'run'  # Change status to 'run' when transitioning from idle to moving
                self.set_speed_from_reverse_state(2, 4)
                self.idle_timer = 0
                self.idle_duration = randint(60, 300)
                self.run_timer = 0
        elif self.status == 'run':
            self.run_timer += 1
            if self.run_timer >= self.run_duration:
                self.status = 'idle'  # Change status to 'idle' when transitioning from running to idle
                self.speed = 0
                self.run_timer = 0
                self.run_duration = randint(60, 300)

