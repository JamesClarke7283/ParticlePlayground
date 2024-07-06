import os
import sys
import time
import importlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.logger import get_logger

logger = get_logger(__name__)

class ModuleReloader(FileSystemEventHandler):
    def __init__(self, module_name):
        self.module_name = module_name
        self.last_modified = {}

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            file_path = event.src_path
            if file_path not in self.last_modified or time.time() - self.last_modified[file_path] > 1:
                self.last_modified[file_path] = time.time()
                module_path = os.path.relpath(file_path).replace(os.path.sep, '.')[:-3]
                if module_path.startswith('src.'):
                    logger.info(f"Reloading module: {module_path}")
                    importlib.reload(sys.modules[module_path])

def start_hot_reloading(module_name):
    src_path = os.path.dirname(os.path.abspath(__file__))
    event_handler = ModuleReloader(module_name)
    observer = Observer()
    observer.schedule(event_handler, src_path, recursive=True)
    observer.start()
    logger.info("Hot reloading started")
    return observer

def stop_hot_reloading(observer):
    observer.stop()
    observer.join()
    logger.info("Hot reloading stopped")