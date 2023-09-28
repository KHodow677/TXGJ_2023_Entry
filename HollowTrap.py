import pygame, sys
from data.game_data import *
from data.settings import *
from scripts.level import Level
from scripts.overworld import Overworld
from scripts.ui import UI
from scripts.support import AnimatedSprite, import_folder

class Game:
    def __init__(self) -> None:
        self.max_level = 0
        self.max_health = 100
        self.current_health = 100
        self.coins = 0

        # Game Elements Setup
        self.overworld = Overworld(0, self.max_level, screen, self.create_level, self.go_to_main_menu)
        self.status = 'overworld'
        self.levels = self.load_all_levels()

        # Player Sprites
        self.animated_player = pygame.sprite.Group()
        self.player_idle_frames = import_folder('graphics/characters/enemy/idle', 0.50)
        player_sprite = AnimatedSprite(self.player_idle_frames, 800, 200, 1, flip=True)  # Adjust frame_duration as needed
        self.animated_player.add(player_sprite)

        # UI
        self.ui = UI(screen)

        # Main Menu Setup
        self.main_menu = True
        self.title_font = pygame.font.Font('graphics/ui/BCS.ttf', 180)
        self.menu_font = pygame.font.Font('graphics/ui/BCS.ttf', 48)
        self.menu_text = self.menu_font.render("Press SPACE to Start", True, (255, 255, 255))
        self.title = self.title_font.render("Hollow Trap", True, (255, 255, 255))

        # Music
        self.game_music = pygame.mixer.Sound('audio/music/spooky_song.wav')
        self.game_music.set_volume(0.25)
        self.game_music.play(loops=-1)

    def create_level(self, current_level) -> None:
        self.level = self.levels[current_level]
        self.level.reset(current_level, screen, self.create_overworld, self.change_coins, self.change_health)
        self.status = 'level'

    def create_overworld(self, current_level, new_max_level) -> None:
        if current_level == 0 and new_max_level == 0:
            self.check_game_over(force = True)
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level, self.go_to_main_menu)
        self.status = 'overworld'
        
    def load_all_levels(self) -> list[Level]:
        all_levels = []
        for i in range(len(levels)):
            all_levels.append(Level(i, screen, self.create_overworld, self.change_coins, self.change_health))
        return all_levels
    
    def change_coins(self, amount) -> None:
        self.coins += amount

    def change_health(self, amount) -> None:
        self.current_health += amount

    def check_game_over(self, force = False) -> None:
        if self.current_health <= 0 or force:
            self.current_health = 100
            self.coins = 0
            self.max_level = 0
            self.overworld = Overworld(0, self.max_level, screen, self.create_level, self.go_to_main_menu)
            self.status = 'overworld'

    def go_to_main_menu(self) -> None:
        self.main_menu = True

    def show_main_menu(self) -> None:
        screen.blit(bg_image, (0,0))
        screen.blit(self.title, (40, 40))
        screen.blit(self.menu_text, (screen_width // 2 + 150, screen_height // 2 + 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.main_menu = False
        self.animated_player.update()
        self.animated_player.draw(screen)

    def run(self) -> None:
        if self.main_menu:
            self.show_main_menu()
        elif self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.ui.show_health(self.current_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()

# Pygame Setup
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height), pygame.SRCALPHA)
programIcon = pygame.image.load('graphics/overworld/icon.png')
pygame.display.set_caption("Hollow Trap")
pygame.display.set_icon(programIcon)
clock = pygame.time.Clock()

loading_image = pygame.image.load('graphics/ui/loading.png').convert_alpha()
screen.blit(loading_image, (0,0))
pygame.display.update()
game = Game()

bg_image = pygame.image.load('graphics/decorations/blue_background.png').convert_alpha()

font = pygame.font.Font(None, 36)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game.main_menu:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game.overworld.start_time = pygame.time.get_ticks()
                game.overworld.allow_input = False
                game.main_menu = False

    fps = clock.get_fps()
    game.run()

    # fps_text = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
    # screen.blit(fps_text, (10, 10))

    pygame.display.update()
    clock.tick(60)
