# ./src/palette.py
import pygame
from src.storage import storage
from src.logger import get_logger
from src.utils.icon import save_icon, frameify_icon, get_icon

logger = get_logger(__name__)

class PaletteItem:
    def __init__(self, id, name, icon_path, frame_path):
        self.id = id
        self.name = name
        self.icon_path = icon_path
        self.frame_path = frame_path
        self.icon = None
        self.subitems = []

    def load_icon(self):
        if self.icon is None:
            cache_relative_path = f"icons/{self.id}.png"
            self.icon = get_icon(self.icon_path, self.frame_path, cache_relative_path)

    def add_subitem(self, subitem):
        self.subitems.append(subitem)

class Palette:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.items = []
        self.selected_item = None
        self.hovered_item = None
        self.rects = []
        self.icon_size = storage.get_setting("graphics", "palette", "icon_size", default=64)
        self.selected_group = storage.get_setting("graphics", "palette", "palette_group_selected", default="powders")
        self.invisible_barriers = []

    def add_item(self, item):
        self.items.append(item)
        if item.id == self.selected_group:
            self.selected_item = item

    def draw(self, screen):
        x = screen.get_width() - self.icon_size - 20
        y = 20
        self.rects = []
        for item in self.items:
            item.load_icon()
            item_rect = pygame.Rect(x, y, self.icon_size, self.icon_size)
            self.rects.append((item_rect, item))
            icon_surface = pygame.image.fromstring(item.icon.tobytes(), item.icon.size, item.icon.mode)
            icon_surface = pygame.transform.scale(icon_surface, (self.icon_size, self.icon_size))
            screen.blit(icon_surface, item_rect.topleft)
            if item_rect.collidepoint(pygame.mouse.get_pos()):
                self.hovered_item = item
                self.draw_text(screen, item.name, item_rect.left - 10, item_rect.centery, align="right")
            y += self.icon_size + 10
        if self.selected_item:
            self.draw_subitems(screen)

    def draw_subitems(self, screen):
        if not self.selected_item:
            return
        subitem_x = screen.get_width() - (2 * self.icon_size) - 30
        subitem_y = screen.get_height() - self.icon_size - 10
        for subitem in reversed(self.selected_item.subitems):
            subitem.load_icon()
            subitem_rect = pygame.Rect(subitem_x, subitem_y, self.icon_size, self.icon_size)
            self.rects.append((subitem_rect, subitem))
            icon_surface = pygame.image.fromstring(subitem.icon.tobytes(), subitem.icon.size, subitem.icon.mode)
            icon_surface = pygame.transform.scale(icon_surface, (self.icon_size, self.icon_size))
            screen.blit(icon_surface, subitem_rect.topleft)
            if subitem_rect.collidepoint(pygame.mouse.get_pos()):
                self.draw_text(screen, subitem.name, subitem_rect.left + self.icon_size // 2, subitem_rect.top - 25, align="center")
            subitem_x -= self.icon_size + 10

    def draw_text(self, screen, text, x, y, align="left"):
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        if align == "right":
            text_rect.topright = (x, y)
        elif align == "center":
            text_rect.midtop = (x, y)
        else:
            text_rect.topleft = (x, y)
        screen.blit(text_surface, text_rect)

    def check_hover(self, pos):
        for item_rect, item in self.rects:
            if item_rect.collidepoint(pos):
                self.hovered_item = item
                return item.id
        self.hovered_item = None
        return None

    def check_click(self, pos):
        for item_rect, item in self.rects:
            if item_rect.collidepoint(pos):
                if item in self.items:
                    self.selected_item = item
                    storage.set_setting(item.id, "graphics", "palette", "palette_group_selected")
                logger.info(f"Selected particle: {item.name}")
                return item.id
        return None

    def get_selected_item(self):
        return self.selected_item

    def update_invisible_barriers(self, screen):
        self.invisible_barriers = []

        # Right palette barrier
        right_palette_x = screen.get_width() - self.icon_size - 20
        right_palette_y = 20
        for item in self.items:
            item_rect = pygame.Rect(right_palette_x, right_palette_y, self.icon_size, self.icon_size)
            self.invisible_barriers.append(item_rect)
            right_palette_y += self.icon_size + 10

        # Bottom palette barrier
        bottom_palette_x = screen.get_width() - self.icon_size - 20
        bottom_palette_y = screen.get_height() - self.icon_size - 10
        left_margin = self.icon_size + 20  # Prevent overlap with the left palette
        if self.selected_item:
            for subitem in reversed(self.selected_item.subitems):
                if bottom_palette_x < left_margin:
                    break
                subitem_rect = pygame.Rect(bottom_palette_x, bottom_palette_y, self.icon_size, self.icon_size)
                self.invisible_barriers.append(subitem_rect)
                bottom_palette_x -= self.icon_size + 10

# Example of adding items to the palette
def initialize_palette():
    palette = Palette()

    # Add main items
    powders_icon_path = 'assets/palette/toplevel/powders.png'
    powders_frame_path = 'assets/palette/toplevel/frame.png'
    powders_item = PaletteItem("powders", "Powders", powders_icon_path, powders_frame_path)

    # Add subitems
    dust_icon_path = 'assets/palette/powders/dust.png'
    dust_frame_path = 'assets/palette/toplevel/frame.png'
    dust_item = PaletteItem("dust", "Dust", dust_icon_path, dust_frame_path)
    powders_item.add_subitem(dust_item)

    palette.add_item(powders_item)

    return palette
