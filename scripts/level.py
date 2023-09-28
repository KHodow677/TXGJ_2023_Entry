import pygame
from scripts.support import import_csv_layout, import_cut_graphics, import_folder
from data.settings import tile_size, screen_height, screen_width
from data.game_data import levels
from scripts.tiles import Tile, StaticTile, AnimatedTile, Crate, Coin
from scripts.enemy import Enemy
from scripts.decorations import Sky, Water, Clouds
from scripts.player import Player
from scripts.particles import ParticleEffect

class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health) -> None:
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None

        # Audio
        self.coin_sound = pygame.mixer.Sound('audio/sfx/coin/coin.wav')
        self.stomp_sound = pygame.mixer.Sound('audio/sfx/land/land.wav')
        self.hurt_sound = pygame.mixer.Sound('audio/sfx/hurt/hurt.wav')
        self.treasure_sound = pygame.mixer.Sound('audio/sfx/treasure/treasure.wav')
        self.coin_sound.set_volume(0.25)
        self.stomp_sound.set_volume(0.25)
        self.hurt_sound.set_volume(0.25)
        self.treasure_sound.set_volume(0.25)

        # Overworld Connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

        # Player Setup
        self.player_animations = self.import_character_assets('graphics/characters/player/', ['idle', 'run', 'jump', 'fall'])
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)
        self.jump_frames = import_folder('graphics/particles/player/jump', 0.125)
        self.land_frames = import_folder('graphics/particles/player/land', 0.125)

        # User Interface
        self.change_coins = change_coins

        # Dust Setup
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # Terrain Setup
        self.terrain_layout = import_csv_layout(level_data['terrain'])

        # Crate Setup
        self.crate_layout = import_csv_layout(level_data['crates'])

        # Coin Setup
        self.coin_frames = import_folder('graphics/items/coin/', 0.25)
        self.coin_layout = import_csv_layout(level_data['coins'])

        # Enemy Setup
        self.enemy_animations = self.import_character_assets('graphics/characters/enemy/', ['attack', 'idle', 'run'])
        self.enemy_layout = import_csv_layout(level_data['enemies'])

        # Constraints Setup
        self.constraint_layout = import_csv_layout(level_data['constraints'])

        # Trap Setup
        self.blade_frames = import_folder('graphics/items/traps/blade/', 0.1)
        self.spike_frame = pygame.image.load('graphics/items/traps/spike.png').convert_alpha()
        scale_factor = 0.125
        self.spike_frame = pygame.transform.smoothscale(self.spike_frame, (int(self.spike_frame.get_width() * scale_factor), int(self.spike_frame.get_height() * scale_factor)))
        self.trap_layout = import_csv_layout(level_data['traps'])

        # Background Setup
        self.sky = Sky()
        level_width = len(self.terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 60, level_width)
        self.clouds = Clouds(400, level_width, 20)

    def import_character_assets(self, character_path, animation_types) -> None:
        animations = {}
        for animation in animation_types:
            animation_list = []
            full_path = character_path + animation
            animation_frames = import_folder(full_path, 0.125)
            for frame in animation_frames:
                animation_list.append(frame)
            animations[animation] = animation_list
        return animations

    def create_tile_group(self, layout, type) -> pygame.sprite.Group:
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'crates':
                        crate_tile_list = import_cut_graphics('graphics/terrain/crates.png')
                        tile_surface = crate_tile_list[int(val)]
                        scale = 0.7
                        tile_surface = pygame.transform.smoothscale(tile_surface, (int(tile_surface.get_width() * scale), int(tile_surface.get_height() * scale)))
                        sprite = Crate(tile_size, x, y+5, tile_surface)

                    if type == 'coins':
                        sprite = Coin(tile_size, x, y, self.coin_frames)

                    if type == 'enemies':
                        sprite = Enemy(tile_size, x, y-10, self.enemy_animations)

                    if type == 'constraints':
                        sprite = Tile(tile_size, x, y)

                    if type == 'traps' and val == '0':
                        sprite = AnimatedTile(tile_size, x, y, self.blade_frames)

                    if type == 'traps' and val == '1':
                        sprite = StaticTile(tile_size, x, y+32, self.spike_frame)
                    
                    sprite_group.add(sprite)
        
        return sprite_group

    def player_setup(self, layout, change_health) -> None:
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x, y+15), self.display_surface, self.player_animations, self.create_jump_particles, change_health)
                    self.player.add(sprite)
                if val == '1':
                    treasure_surface = pygame.image.load('graphics/items/treasure/01.png').convert_alpha()
                    scale_factor = 0.7
                    treasure_surface = pygame.transform.smoothscale(treasure_surface, (int(treasure_surface.get_width() * scale_factor), int(treasure_surface.get_height() * scale_factor)))
                    sprite = StaticTile(tile_size, x, y-15, treasure_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self) -> None:
        for enemy in self.enemy_sprites:
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False) and enemy.status == 'run':
                enemy.reverse()

    def check_player_on_ground(self) -> None:
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_jump_particles(self, pos) -> None:
        if self.player.sprite.face_right:
            pos -= pygame.math.Vector2(0, 0)
        else:
            pos -= pygame.math.Vector2(0, 0)
        jump_particle_sprite = ParticleEffect(pos, self.jump_frames)
        self.dust_sprite.add(jump_particle_sprite)

    def create_land_particles(self) -> None:
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.face_right:
                offset = pygame.math.Vector2(0, 0)
            else:
                offset = pygame.math.Vector2(0, 0)
            land_particle_sprite = ParticleEffect(self.player.sprite.rect.midbottom - offset, self.land_frames)
            self.dust_sprite.add(land_particle_sprite)
            self.stomp_sound.play()

    def horizontal_movement_collision(self) -> None:
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprites.sprites() + self.crate_sprites.sprites():
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                    player.on_left_wall = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.on_right_wall = True
                    self.current_x = player.rect.right  

    def vertical_movement_collision(self) -> None:
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.terrain_sprites.sprites() + self.crate_sprites.sprites():
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def scroll_x(self) -> None:
        player = self.player.sprite

        player_x = player.collision_rect.centerx
        center_x = screen_width // 2
        shift_x = (center_x - player_x) // 20

        self.world_shift = shift_x
        player.collision_rect.x += shift_x

    def check_death(self) -> None:
        if self.player.sprite.rect.top > screen_height:
            self.hurt_sound.play()
            self.create_overworld(0, 0)

    def check_win(self) -> None:
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.treasure_sound.play()
            self.create_overworld(self.current_level, self.new_max_level)

    def check_coin_collision(self) -> None:
        coin_collected = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if coin_collected:
            self.coin_sound.play()
            for coin in coin_collected:
                self.change_coins(1)

    def check_enemy_collisions(self) -> None:
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)
        if enemy_collisions:
            for enemy in enemy_collisions:
                if enemy.is_reverse and self.player.sprite.rect.centerx < enemy.rect.centerx:
                    enemy.status = 'attack'
                    enemy.attack_time = pygame.time.get_ticks()
                    self.player.sprite.get_damage(10)
                    self.player.sprite.jump()
                    self.hurt_sound.play()
                elif not enemy.is_reverse and self.player.sprite.rect.centerx > enemy.rect.centerx:
                    enemy.status = 'attack'
                    enemy.attack_time = pygame.time.get_ticks()
                    self.player.sprite.get_damage(10)
                    self.player.sprite.jump()
                    self.hurt_sound.play()
        trap_collisions = pygame.sprite.spritecollide(self.player.sprite, self.trap_sprites, False)
        if trap_collisions:
            if not self.player.sprite.on_ground:
                self.player.sprite.get_damage(10)
                self.player.sprite.jump()
                self.hurt_sound.play()

    def run (self) -> None:

        # Sky
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        # Dust
        self.dust_sprite.update(0)
        self.dust_sprite.draw(self.display_surface)

        # Traps
        self.trap_sprites.update(self.world_shift)
        self.trap_sprites.draw(self.display_surface)

        # Terrain
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)
        
        # Crates
        self.crate_sprites.update(self.world_shift)
        self.crate_sprites.draw(self.display_surface)

        # Enemy
        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)

        # Coins
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)

        # Player Sprites
        self.player.update()
        self.horizontal_movement_collision()
        self.check_player_on_ground()
        self.vertical_movement_collision()
        self.create_land_particles()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        
        self.check_death()
        self.check_win()

        self.check_coin_collision()
        self.check_enemy_collisions()

        # Water
        self.water.draw(self.display_surface, self.world_shift)

        self.scroll_x()

    def reset(self, current_level, surface, create_overworld, change_coins, change_health) -> None:
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None

        # Overworld Connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']

        # Player Setup
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)

        # User Interface
        self.change_coins = change_coins

        # Dust Setup
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # Terrain Setup
        self.terrain_sprites = self.create_tile_group(self.terrain_layout, 'terrain')

        # Crate Setup
        self.crate_sprites = self.create_tile_group(self.crate_layout, 'crates')

        # Coin Setup
        self.coin_sprites = self.create_tile_group(self.coin_layout, 'coins')

        # Enemy Setup
        self.enemy_sprites = self.create_tile_group(self.enemy_layout, 'enemies')

        # Constraints Setup
        self.constraint_sprites = self.create_tile_group(self.constraint_layout, 'constraints')

        # Trap Setup
        self.trap_sprites = self.create_tile_group(self.trap_layout, 'traps')

        # Background Setup
        self.sky = Sky()
        level_width = len(self.terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 60, level_width)
        self.clouds = Clouds(400, level_width, 20)