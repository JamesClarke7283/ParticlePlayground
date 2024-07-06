import os
import tomllib
import tomli_w
from appdirs import user_config_dir
from src.logger import get_logger

logger = get_logger(__name__)

class Storage:
    def __init__(self):
        self.app_name = "ParticlePlayground"
        self.config_dir = user_config_dir(self.app_name)
        self.config_file = os.path.join(self.config_dir, "settings.toml")
        self.default_settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".default_settings.toml")
        logger.info(f"Config file: {self.config_file}")
        logger.info(f"Default settings file: {self.default_settings_file}")
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.config_file) and os.path.getsize(self.config_file) > 0:
            try:
                with open(self.config_file, "rb") as f:
                    logger.info(f"Loading settings from {self.config_file}")
                    return tomllib.load(f)
            except tomllib.TOMLDecodeError:
                logger.error(f"Error reading {self.config_file}. Using default settings.")
        
        # Load default settings
        try:
            with open(self.default_settings_file, "rb") as f:
                logger.info(f"Loading default settings from {self.default_settings_file}")
                default_settings = tomllib.load(f)
            
            # Write default settings to config file
            self.save_settings(default_settings)
            return default_settings
        except (FileNotFoundError, tomllib.TOMLDecodeError):
            logger.error(f"Error reading {self.default_settings_file}. Using hardcoded default settings.")
            default_settings = {
                "cursor": {"size": 5, "max_size": 50},
                "window": {"width": 800, "height": 600}
            }
            self.save_settings(default_settings)
            return default_settings

    def save_settings(self, settings=None):
        if settings is None:
            settings = self.settings
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, "wb") as f:
            logger.info(f"Saving settings to {self.config_file}")
            tomli_w.dump(settings, f)

    def get_setting(self, *keys, default=None):
        value = self.settings
        for key in keys:
            if key in value and isinstance(value, dict):
                value = value[key]
            else:
                logger.warning(f"Setting not found: {keys}. Using default: {default}")
                return default
        logger.debug(f"Retrieved setting: {keys} = {value}")
        return value

    def set_setting(self, value, *keys):
        settings = self.settings
        for key in keys[:-1]:
            settings = settings.setdefault(key, {})
        settings[keys[-1]] = value
        logger.debug(f"Setting updated: {keys} = {value}")
        self.save_settings()

storage = Storage()