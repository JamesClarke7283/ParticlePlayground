import pygame
import sys
import os
from src.input_handler import InputHandler
from src.menu.main import MainMenu
from src.storage import storage
from src.logger import get_logger
from src.palette import initialize_palette

logger = get_logger(__name__)

def main():
    logger.info("Game starting")

    # Check if we're running in a PyInstaller bundle
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        is_development = False
    else:
        is_development = True
        from src.hot_reload import start_hot_reloading, stop_hot_reloading
        observer = start_hot_reloading(__name__)

    # Initialize Pygame
    pygame.init()
    logger.debug("Pygame initialized")

    # Set up the display
    width = storage.get_setting("window", "width", default=800)
    height = storage.get_setting("window", "height", default=600)
    
    # Ensure width and height are integers
    try:
        width = int(width)
        height = int(height)
    except ValueError:
        logger.error("Invalid window dimensions in settings. Using defaults.")
        width, height = 800, 600

    logger.info(f"Setting up display: {width}x{height}")
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption("Particle Playground")

    # Create input handler, menu, and palette
    input_handler = InputHandler()
    main_menu = MainMenu()
    current_menu = main_menu
    palette = initialize_palette()

    # Set up the clock for a consistent frame rate
    clock = pygame.time.Clock()

    # Main game loop
    running = True
    try:
        logger.info("Entering main game loop")
        while running:
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    logger.info("Quit event received")
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    width, height = event.size
                    storage.set_setting(width, "window", "width")
                    storage.set_setting(height, "window", "height")
                    logger.info(f"Window resized to {width}x{height}")
                if input_handler.is_menu_open():
                    result = current_menu.handle_event(event)
                    if isinstance(result, str):
                        if result == "MainMenu":
                            current_menu = main_menu
                        elif result == "Back to Game":
                            input_handler.show_menu = False
                        elif result == "Quit Game":
                            running = False
                    elif result != current_menu:
                        current_menu = result
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        palette.check_click(event.pos)

            # Handle input
            input_handler.handle_events(events, main_menu)

            # Fill the screen with black
            screen.fill((0, 0, 0))

            # Draw the cursor
            input_handler.draw_cursor(screen)

            # Draw the menu if it's open
            if input_handler.is_menu_open():
                current_menu.draw(screen)
            else:
                palette.check_hover(pygame.mouse.get_pos())  # Check hover status
                palette.draw(screen)

            # Update the invisible barriers
            palette.update_invisible_barriers(screen)

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(60)
            logger.trace(f"FPS: {clock.get_fps():.2f}")

    except KeyboardInterrupt:
        logger.info("Game interrupted by keyboard")
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
    finally:
        logger.info("Game loop ended, cleaning up")
        # Save all current settings before quitting
        current_size = screen.get_size()
        storage.set_setting(current_size[0], "window", "width")
        storage.set_setting(current_size[1], "window", "height")
        storage.set_setting(input_handler.get_cursor_size(), "cursor", "size")
        storage.set_setting(input_handler.max_cursor_size, "cursor", "max_size")
        storage.save_settings()
        # Quit Pygame
        pygame.quit()
        if is_development:
            stop_hot_reloading(observer)
        logger.info("Game exited")
        sys.exit()

if __name__ == "__main__":
    main()