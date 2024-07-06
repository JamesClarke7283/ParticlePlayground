import pygame
from src.storage import storage
from src.logger import get_logger

logger = get_logger(__name__)

class InputHandler:
    def __init__(self):
        self.cursor_size = storage.get_setting("cursor", "size", default=5)
        self.max_cursor_size = storage.get_setting("cursor", "max_size", default=50)
        self.cursor_color = pygame.Color('white')
        self.cursor_pos = pygame.mouse.get_pos()
        self.show_menu = False
        logger.info(f"InputHandler initialized. Cursor size: {self.cursor_size}, Max size: {self.max_cursor_size}")

    def handle_events(self, events, menu):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.cursor_pos = event.pos
                logger.trace(f"Mouse moved to {self.cursor_pos}")
            elif event.type == pygame.MOUSEWHEEL:
                self.adjust_cursor_size(event.y)
                logger.trace(f"Mouse wheel scrolled: {event.y}")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.show_menu = not self.show_menu
                    logger.debug(f"Menu toggled: {'shown' if self.show_menu else 'hidden'}")
                elif event.key == pygame.K_TAB and self.show_menu:
                    menu.next_option()
                    logger.trace("Menu option changed")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.show_menu:  # Left mouse button
                    menu.check_click(event.pos)
                    logger.trace(f"Menu clicked at {event.pos}")
            elif event.type == pygame.VIDEORESIZE:
                logger.info(f"Window resized to {event.w}x{event.h}")
                storage.set_setting(event.w, "window", "width")
                storage.set_setting(event.h, "window", "height")

    def adjust_cursor_size(self, scroll_amount):
        new_size = max(1, min(self.max_cursor_size, self.cursor_size + scroll_amount))
        if new_size != self.cursor_size:
            self.cursor_size = new_size
            storage.set_setting(self.cursor_size, "cursor", "size")
            logger.debug(f"Cursor size adjusted to {self.cursor_size}")

    def draw_cursor(self, screen):
        pygame.draw.circle(screen, self.cursor_color, self.cursor_pos, self.cursor_size, 1)

    def get_cursor_size(self):
        return self.cursor_size

    def get_cursor_pos(self):
        return self.cursor_pos

    def is_menu_open(self):
        return self.show_menu
