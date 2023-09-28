import pygame, math, random
from scripts.support import import_folder, import_folder_audio

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, animations, create_jump_particles, change_health) -> None:
        super().__init__()

        # Sound Effects
        self.jump_sounds = import_folder_audio('audio/sfx/jump/')
        for sound in self.jump_sounds:
            sound.set_volume(0.15)

        # Animation Attributes
        self.animations = animations
        self.frame_index = 0
        self.animation_speed = 1
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # Particles
        self.dust_frame_index = 0
        self.dust_animation_speed = 0.6
        self.display_surface = surface
        self.create_jump_particles = create_jump_particles

        # Player Movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 8
        self.gravity = 0.8
        self.jump_speed = -16
        self.collision_rect = pygame.Rect((self.rect.midbottom[0]-15,self.rect.midbottom[1]-15), (30, 60))

        # Player Status
        self.status = 'idle'
        self.face_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left_wall = False
        self.on_right_wall = False

        # Health
        self.change_health = change_health
        self.invincible = False
        self.invincibility_duration = 500
        self.hurt_time = 0

    def animate(self) -> None:
        animation = self.animations[self.status]

        # Loop over frame index
        self.frame_index += self.animation_speed
        
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Flip the image
        image = animation[int(self.frame_index)]
        if self.face_right:
            self.image = image
            self.rect.midbottom = self.collision_rect.midbottom
        else:
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image
            self.rect.midbottom = self.collision_rect.midbottom

        if self.invincible:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
          
    def get_input(self) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:
            self.direction.x = 1
            self.face_right = True
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.face_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_w] and self.on_ground:
            self.jump()
            self.create_jump_particles(self.rect.midbottom)

    def get_status(self):
        self.last_frame_direction = self.direction
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 0 and not self.on_ground:
            self.status = 'jump'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    def apply_gravity(self) -> None:
        self.direction.y += self.gravity
        self.collision_rect.y += self.direction.y
        
    def jump(self) -> None:
        self.direction.y = self.jump_speed
        random.choice(self.jump_sounds).play()

    def get_damage(self, amount) -> None:
        if not self.invincible:
            self.invincible = True
            self.change_health(-amount)
            self.hurt_time = pygame.time.get_ticks()

    def invincibility_timer(self) -> None:
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.invincible = False

    def wave_value(self):
        value = math.sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0

    def update(self) -> None:
        self.get_input()
        self.get_status()
        self.animate()
        self.invincibility_timer()