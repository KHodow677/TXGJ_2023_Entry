import pygame

class UI:
    def __init__(self, surface) -> None:
        
        # Setup
        self.display_surface = surface

        # Health
        self.health_bar = pygame.image.load('graphics/ui/health_bar.png').convert_alpha()
        scale_factor = 0.75
        self.health_bar = pygame.transform.smoothscale(self.health_bar, (int(self.health_bar.get_width() * scale_factor), int(self.health_bar.get_height() * scale_factor)))
        self.health_bar_topleft = (87,37)
        self.bar_max_width = 148
        self.bar_height = 20

        # Coins
        self.coin = pygame.image.load('graphics/items/coin/01.png').convert_alpha()
        scale_factor = 0.35
        self.coin = pygame.transform.smoothscale(self.coin, (int(self.coin.get_width() * scale_factor), int(self.coin.get_height() * scale_factor)))
        self.coin_rect = self.coin.get_rect(topleft = (80,70))
        self.font = pygame.font.Font('graphics/ui/BCS.ttf', 36)

    def show_health(self, current_health, max_health) -> None:
        self.display_surface.blit(self.health_bar, (20, 10))
        current_health_ratio = current_health / max_health
        current_bar_width = int(self.bar_max_width * current_health_ratio)
        health_bar_rect = pygame.Rect(self.health_bar_topleft, (current_bar_width, self.bar_height))
        pygame.draw.rect(self.display_surface, '#a12c2c', health_bar_rect)

    def show_coins(self, amount) -> None:
        self.display_surface.blit(self.coin, self.coin_rect)
        coint_amount_surf = self.font.render(str(amount), True, 'black')
        coint_amount_rect = coint_amount_surf.get_rect(midleft = (self.coin_rect.right + 10, self.coin_rect.centery + 2))
        self.display_surface.blit(coint_amount_surf, coint_amount_rect)