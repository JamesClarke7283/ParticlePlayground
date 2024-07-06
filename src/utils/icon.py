# ./src/utils/icon.py
from PIL import Image
import os
from appdirs import AppDirs
from src.storage import storage

dirs = AppDirs("ParticlePlayground")
icon_size = storage.get_setting("graphics", "palette", "icon_size", default=64)

def get_effective_bounding_box(image):
    alpha = image.split()[3]  # Get the alpha channel
    bbox = alpha.getbbox()
    return bbox

def get_effective_size(image):
    bbox = get_effective_bounding_box(image)
    effective_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
    return effective_size

def resize_image(image, width, height):
    return image.resize((width, height), Image.LANCZOS)

def save_icon(image, relative_path):
    save_path = os.path.join(dirs.user_cache_dir, relative_path)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    image.save(save_path)
    return save_path

def frameify_icon(icon_path, frame_path, padding=10):
    frame = Image.open(frame_path).convert("RGBA")
    icon = Image.open(icon_path).convert("RGBA")

    icon_bbox = get_effective_bounding_box(icon)
    icon_effective = icon.crop(icon_bbox)

    frame_bbox = get_effective_bounding_box(frame)
    frame_effective = frame.crop(frame_bbox)

    icon_effective_size = get_effective_size(icon)
    frame_effective_size = get_effective_size(frame)

    max_icon_width = frame_effective_size[0] - padding * 2
    max_icon_height = frame_effective_size[1] - padding * 2

    icon_ratio = icon_effective_size[0] / icon_effective_size[1]
    if max_icon_width / icon_ratio <= max_icon_height:
        new_icon_width = max_icon_width
        new_icon_height = max_icon_width / icon_ratio
    else:
        new_icon_height = max_icon_height
        new_icon_width = max_icon_height * icon_ratio

    new_icon_size = (int(new_icon_width), int(new_icon_height))
    
    resized_icon = resize_image(icon, new_icon_size[0], new_icon_size[1])

    framed_icon = Image.new("RGBA", frame.size, (0, 0, 0, 0))

    paste_position = (
        (frame.size[0] - resized_icon.size[0]) // 2,
        (frame.size[1] - resized_icon.size[1]) // 2
    )
    
    framed_icon.paste(resized_icon, paste_position, resized_icon)
    framed_icon = Image.alpha_composite(framed_icon, frame)

    return resize_image(framed_icon, icon_size, icon_size)

def process_and_cache_icon(icon_path, frame_path, cache_relative_path):
    cache_path = os.path.join(dirs.user_cache_dir, cache_relative_path)
    if not os.path.exists(cache_path):
        framed_icon = frameify_icon(icon_path, frame_path)
        save_icon(framed_icon, cache_relative_path)
    return cache_path
