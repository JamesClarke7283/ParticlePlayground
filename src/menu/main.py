import pygame
from src.storage import storage
from src.logger import get_logger
from src.menu.settings import SettingsMenu

logger = get_logger(__name__)

class MainMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.options = ["Back to Game", "Settings", "Quit Game"]
        self.selected = 0
        self.option_rects = []
        self.settings_menu = SettingsMenu()
        logger.info("Main menu initialized")

    def draw(self, screen):
        menu_surface = pygame.Surface((300, 200))
        menu_surface.fill((50, 50, 50))
        self.option_rects = []
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(topleft=(20, 20 + i * 40))
            menu_surface.blit(text, text_rect)
            self.option_rects.append(text_rect.move(250, 200))
        screen.blit(menu_surface, (250, 200))
        logger.debug("Menu drawn")

    def next_option(self):
        self.selected = (self.selected + 1) % len(self.options)
        logger.debug(f"Menu selection changed to {self.options[self.selected]}")

    def check_click(self, pos):
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                self.selected = i
                logger.info(f"Menu option clicked: {self.options[i]}")
                return self.options[i]
        return None

    def get_selected_option(self):
        return self.options[self.selected]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_option = self.check_click(event.pos)
            if clicked_option == "Settings":
                return self.settings_menu
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.options[self.selected] == "Settings":
                    return self.settings_menu
        return self