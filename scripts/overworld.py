import pygame
from data.game_data import *
from data.settings import screen_width
from scripts.decorations import Sky, Clouds

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed, path) -> None:
        super().__init__()
        self.base_image = pygame.image.load(path).convert_alpha()
        self.image = self.base_image
        self.rect = self.image.get_rect(center=pos)
        if status == 'available':
            self.status = 'available'
        else:
            self.status = 'locked'

        self.original_rect = self.rect.copy()

        self.detection_zone = pygame.Rect(
            self.rect.centerx - (icon_speed / 2),
            self.rect.centery - (icon_speed / 2),
            icon_speed,
            icon_speed)

    def set_highlighted(self, is_highlighted) -> None:
        if is_highlighted:
            scale_factor = 1.1 
            new_width = int(self.original_rect.width * scale_factor)
            new_height = int(self.original_rect.height * scale_factor)
            self.image = pygame.transform.smoothscale(self.base_image, (new_width, new_height))

            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.image = self.base_image
            self.rect = self.original_rect.copy()

    def update(self) -> None:
        if self.status != 'available':
            # Create a copy of the original image
            tinted_surf = self.base_image.copy()
            tinted_image = self.base_image.copy()

            tint_color = (0, 0, 0, 200)  
            tinted_surf.fill(tint_color, None, pygame.BLEND_RGBA_MULT)
            
            tinted_image.blit(tinted_surf, (0, 0))
            self.image = tinted_image

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos) -> None:
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load('graphics/overworld/icon.png').convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (100,100))
        self.rect = self.image.get_rect(center=pos)

    def update(self) -> None:
        self.rect.center = self.pos

class Overworld:
    def __init__(self, start_level, max_level, surface, create_level, go_to_main_menu) -> None:
        # Setup
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.go_to_main_menu = go_to_main_menu

        # Movement
        self.move_direction = pygame.math.Vector2(0,0)
        self.speed = 8
        self.moving = False

        # Sprites
        self.setup_nodes()
        self.setup_icon()
        self.nodes.sprites()[self.current_level].set_highlighted(True)
        self.sky = Sky()
        self.clouds = self.clouds = Clouds(400, screen_width, 10)

        # Levels
        self.create_level = create_level

        # Time
        self.start_time = pygame.time.get_ticks()
        self.allow_input = False
        self.timer_length = 300

    def setup_nodes(self) -> None:
        self.nodes = pygame.sprite.Group()

        for index, node_data in enumerate(levels.values()):
            if index <= self.max_level:
                node_sprite = Node(node_data['node_pos'], 'available', self.speed, node_data['node_graphics'])
                self.nodes.add(node_sprite)
            else:
                node_sprite = Node(node_data['node_pos'], 'locked', self.speed, node_data['node_graphics'])
                self.nodes.add(node_sprite)

    def setup_icon(self) -> None:
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Icon(self.nodes.sprites()[self.current_level].rect.center)
        self.icon.add(icon_sprite)

    def draw_paths(self) -> None:
        if self.max_level > 0:
            points = [node['node_pos'] for index, node in enumerate(levels.values()) if index <= self.max_level]
            pygame.draw.lines(self.display_surface, '#20140f', False, points, 6)

    def input(self) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.go_to_main_menu()
        if not self.moving and self.allow_input:
            if keys[pygame.K_d] and self.current_level < self.max_level:
                self.move_direction = self.get_movement_data('next')
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_a] and self.current_level > 0:
                self.move_direction = self.get_movement_data('previous')
                self.current_level -= 1
                self.moving = True
            elif keys[pygame.K_SPACE]:
                self.create_level(self.current_level)

    def input_timer(self) -> None:
        if not self.allow_input:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.timer_length:
                self.allow_input = True

    def get_movement_data(self, target) -> pygame.math.Vector2:
        start = pygame.math.Vector2(self.nodes.sprites()[self.current_level].rect.center)

        if target == 'next':
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level + 1].rect.center)
        else:
            end = pygame.math.Vector2(self.nodes.sprites()[self.current_level - 1].rect.center)

        return (end - start).normalize()

    def update_icon_pos(self) -> None:
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0,0)

                # Set the current node as highlighted when the icon is on it
                target_node.set_highlighted(True)
            else:
                # Reset the size of all other nodes
                for node in self.nodes:
                    if node != target_node:
                        node.set_highlighted(False)

    def run(self) -> None:
        self.input_timer()
        self.input()
        self.update_icon_pos()
        self.icon.update()
        self.nodes.update()

        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, 0)
        self.draw_paths()
        self.nodes.draw(self.display_surface)
        self.icon.draw(self.display_surface)