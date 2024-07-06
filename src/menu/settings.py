import pygame
from src.storage import storage
from src.logger import get_logger

logger = get_logger(__name__)

class SettingsMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 36)
        self.settings = {
            "Cursor": {
                "Size": storage.get_setting("cursor", "size", default=5),
                "Max Size": storage.get_setting("cursor", "max_size", default=100)
            },
            "Window": {
                "Width": storage.get_setting("window", "width", default=800),
                "Height": storage.get_setting("window", "height", default=600)
            },
            "Palette": {
                "Icon Size": storage.get_setting("graphics", "palette", "icon_size", default=24)  # Updated default to 24
            }
        }
        self.active_setting = None
        self.buttons = []
        self.text_cursor_pos = 0
        self.text_cursor_visible = True
        self.text_cursor_blink_time = 0

    def draw(self, screen):
        screen.fill((30, 30, 30))
        y = 20
        self.buttons = []  # Reset buttons list
        for category, items in self.settings.items():
            category_text = self.title_font.render(category, True, (255, 255, 255))
            screen.blit(category_text, (20, y))
            y += 40
            for setting, value in items.items():
                setting_text = self.font.render(f"{setting}:", True, (200, 200, 200))
                screen.blit(setting_text, (40, y))
                input_rect = pygame.Rect(200, y, 100, 30)
                pygame.draw.rect(screen, (100, 100, 100), input_rect)
                value_text = self.font.render(str(value), True, (255, 255, 255))
                screen.blit(value_text, (210, y + 5))
                if self.active_setting == setting:
                    if self.text_cursor_visible:
                        cursor_x = 210 + self.font.size(str(value)[:self.text_cursor_pos])[0]
                        pygame.draw.line(screen, (255, 255, 255), (cursor_x, y + 5), (cursor_x, y + 25), 2)
                self.buttons.append((setting, input_rect))
                y += 40
            y += 20

        # Draw Save and Cancel buttons
        save_button = pygame.Rect(screen.get_width() - 220, screen.get_height() - 50, 100, 40)
        cancel_button = pygame.Rect(screen.get_width() - 110, screen.get_height() - 50, 100, 40)
        pygame.draw.rect(screen, (0, 255, 0), save_button)
        pygame.draw.rect(screen, (255, 0, 0), cancel_button)
        save_text = self.font.render("Save", True, (0, 0, 0))
        cancel_text = self.font.render("Cancel", True, (0, 0, 0))
        screen.blit(save_text, (save_button.x + 30, save_button.y + 10))
        screen.blit(cancel_text, (cancel_button.x + 20, cancel_button.y + 10))
        self.buttons.append(("Save", save_button))
        self.buttons.append(("Cancel", cancel_button))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for setting, rect in self.buttons:
                if rect.collidepoint(event.pos):
                    if setting == "Save":
                        self.save_settings()
                        return "MainMenu"
                    elif setting == "Cancel":
                        return "MainMenu"
                    else:
                        self.active_setting = setting
                        self.text_cursor_pos = len(str(self.get_active_value()))
        elif event.type == pygame.KEYDOWN:
            if self.active_setting:
                if event.key == pygame.K_RETURN:
                    self.active_setting = None
                elif event.key == pygame.K_BACKSPACE:
                    self.update_setting(self.active_setting, event.unicode)
                elif event.key == pygame.K_LEFT:
                    self.text_cursor_pos = max(0, self.text_cursor_pos - 1)
                elif event.key == pygame.K_RIGHT:
                    self.text_cursor_pos = min(len(str(self.get_active_value())), self.text_cursor_pos + 1)
                elif event.unicode.isnumeric():
                    self.update_setting(self.active_setting, event.unicode)
            elif event.key == pygame.K_RETURN:
                self.save_settings()
                return "MainMenu"
        
        # Blink the text cursor
        current_time = pygame.time.get_ticks()
        if current_time - self.text_cursor_blink_time > 500:
            self.text_cursor_visible = not self.text_cursor_visible
            self.text_cursor_blink_time = current_time

        return self

    def update_setting(self, setting, value):
        for category, items in self.settings.items():
            if setting in items:
                current = str(items[setting])
                if value == "\b":
                    new_value = current[:self.text_cursor_pos-1] + current[self.text_cursor_pos:]
                    self.text_cursor_pos = max(0, self.text_cursor_pos - 1)
                else:
                    new_value = current[:self.text_cursor_pos] + value + current[self.text_cursor_pos:]
                    self.text_cursor_pos += 1
                try:
                    items[setting] = int(new_value)
                except ValueError:
                    pass

    def get_active_value(self):
        for category, items in self.settings.items():
            if self.active_setting in items:
                return items[self.active_setting]
        return None

    def save_settings(self):
        storage.set_setting(self.settings["Cursor"]["Size"], "cursor", "size")
        storage.set_setting(self.settings["Cursor"]["Max Size"], "cursor", "max_size")
        storage.set_setting(self.settings["Window"]["Width"], "window", "width")
        storage.set_setting(self.settings["Window"]["Height"], "window", "height")
        storage.set_setting(self.settings["Palette"]["Icon Size"], "graphics", "palette", "icon_size")
        storage.save_settings()
        logger.info("Settings saved")