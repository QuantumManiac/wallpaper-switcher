# Imports
from pathlib import Path
from shutil import move
from PIL import Image
from random import randint, choice
from win32com.shell import shell, shellcon
from uuid import uuid4
import os
import ctypes
import win32api
import pythoncom
import pywintypes
import win32gui


# Constants
VALID_FILETYPES = ['.gif', '.jpeg', '.jpg', '.png']

# Monitor height and width - assuming all monitors have the same one
MONITOR_HEIGHT = 1080
MONITOR_WIDTH = 1920

# Aspect ratio for single monitor
SINGLE_ASPECT_RATIO = 16 / 9

# Thresholds for Windows using wallpaper of given aspect ratio as one wallpaper type vs another
LOWER_THRESH = 1
SINGLE_TO_DUAL_THRESH = 2.2
DUAL_TO_TRIPLE_THRESH = 4.45
UPPER_THRESH = 7

# Dictionary to map wallpaper sizes to wallpaper folders
size_folders = {
    1: '1_Single-Monitor',
    2: '2_Dual-Monitor',
    3: '3_Triple-Monitor'
}

# Misc folder names
TO_SORT_FOLDER = '0_To-Sort'
OTHER_FOLDER = '4_Other'


# Helper function to resize wallpaper to desired size
def crop_wallpaper(img, new_height, new_width):
    width, height = img.size   # Get dimensions

    left = round((width - new_width) / 2)
    top = round((height - new_height) / 2)
    x_right = round(width - new_width) - left
    x_bottom = round(height - new_height) - top
    right = width - x_right
    bottom = height - x_bottom

    # Crop the center of the image
    return img.crop((left, top, right, bottom))


def _make_filter(class_name, title):
    """https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enumwindows"""

    def enum_windows(handle, h_list):
        if not (class_name or title):
            h_list.append(handle)
        if class_name and class_name not in win32gui.GetClassName(handle):
            return True  # continue enumeration
        if title and title not in win32gui.GetWindowText(handle):
            return True  # continue enumeration
        h_list.append(handle)

    return enum_windows


def find_window_handles(parent=None, window_class=None, title=None):
    cb = _make_filter(window_class, title)
    try:
        handle_list = []
        if parent:
            win32gui.EnumChildWindows(parent, cb, handle_list)
        else:
            win32gui.EnumWindows(cb, handle_list)
        return handle_list
    except pywintypes.error:
        return []


if __name__ == "__main__":
    # SORT UNSORTED WALLPAPERS
    # Check if to-sort folder has wallpapers to sort
    if len(os.listdir(f'./{TO_SORT_FOLDER}')) != 0:
        # If to-sort folder has wallpapers, sort them
        for path in Path(f'./{TO_SORT_FOLDER}').iterdir():
            # Check if file in folder is a valid image filetype
            if path.suffix in VALID_FILETYPES:
                img = Image.open(path)
                sort_width, sort_height = img.size
                aspect_ratio = sort_width / sort_height
                img.close()

                # Pick destination folder based on aspect ratio of wallpaper
                if aspect_ratio >= LOWER_THRESH and aspect_ratio <= SINGLE_TO_DUAL_THRESH:
                    dest_folder = size_folders[1]
                elif aspect_ratio > SINGLE_TO_DUAL_THRESH and aspect_ratio <= DUAL_TO_TRIPLE_THRESH:
                    dest_folder = size_folders[2]
                elif aspect_ratio > DUAL_TO_TRIPLE_THRESH and aspect_ratio <= UPPER_THRESH:
                    dest_folder = size_folders[3]
                else:
                    # Anything that doesn't fit the other folders (wierd aspect ratios)
                    dest_folder = OTHER_FOLDER

                # Create unique filename
                filename = str(uuid4()) + path.suffix
                # Create destination path
                dest = Path(f'./{dest_folder}/{filename}')
                # Move image to destination folder
                move(path, dest)

            else:
                # If not valid filetype, move to "Other" folder
                dest = Path(f'./{OTHER_FOLDER}/{path.name}')
                move(path, dest)

    # SWITCH WALLPAPERS

    # Get desktop width and height
    user32 = ctypes.windll.user32
    desk_width, desk_height = user32.GetSystemMetrics(
        78), user32.GetSystemMetrics(79)

    # Get number of monitors (assuming all monitors are 1080p - TODO make this compatible with other monitor sizes)
    num_monitors = int(round(desk_width / MONITOR_WIDTH))

    # Generate weightings for each wallpaper size
    wallpaper_weights = []
    for size in size_folders:
        wallpaper_weights += [size] * len(os.listdir(size_folders[size]))
    print(wallpaper_weights)

    # Randomly choose wallpaper sizes
    wallpaper_sizes = []
    while(sum(wallpaper_sizes) < num_monitors):
        wallpaper_size = choice(wallpaper_weights)
        # Check if wallpaper fits into monitors and wallpaper of given size exists
        if ((sum(wallpaper_sizes) + wallpaper_size <= num_monitors) and len(os.listdir(f'./{size_folders[wallpaper_size]}')) != 0):
            wallpaper_sizes.append(wallpaper_size)

    # Randomly choose wallpaper paths from given wallpaper sizes
    wallpaper_paths = []
    for size in wallpaper_sizes:
        wallpaper_paths.append(
            f'./{size_folders[size]}/{choice(os.listdir(f"./{size_folders[size]}"))}')

    # Open each image
    wallpaper_images = []
    for path in wallpaper_paths:
        wallpaper_images.append(Image.open(path))

    # Crop and resize wallpapers to proper dimensions
    for i, img in enumerate(wallpaper_images):
        # Check if image is already the desired dimensions
        width, height = img.size
        wallpaper_size = wallpaper_sizes[i]
        # Get desired width from wallpaper's size
        desired_width = wallpaper_size * MONITOR_WIDTH
        if (width == desired_width) and (height == MONITOR_HEIGHT):
            continue
        else:
            # Crop image if irregular size

            # Crop based on which dimension of the wallpaper can be the "datum" of the aspect ratio
            if width / (SINGLE_ASPECT_RATIO * wallpaper_size) <= height:
                # Use width as datum
                img = crop_wallpaper(img, round(
                    width / (SINGLE_ASPECT_RATIO * wallpaper_size)), width)
            else:
                # If height too small to use width as datum, use height instead
                img = crop_wallpaper(img, height, height *
                                     (SINGLE_ASPECT_RATIO * wallpaper_size))

            img = img.resize((wallpaper_size * MONITOR_WIDTH, MONITOR_HEIGHT))

            wallpaper_images[i] = img

    # Concat wallpapers together
    # Variable to store final wallpaper
    final_wallpaper = None

    if len(wallpaper_images) != 1:
        # Check if there's not only one wallpaper (no need to concat)

        # Create new image for final wallpaper
        final_wallpaper = Image.new(
            'RGB', (num_monitors * MONITOR_WIDTH, MONITOR_HEIGHT))

        # Variable to store the desired starting x position of next wallpaper
        next_width = 0

        for i, img in enumerate(wallpaper_images):
            final_wallpaper.paste(img, (next_width * MONITOR_WIDTH, 0))
            next_width += wallpaper_sizes[i]

    final_wallpaper.save('current_wallpaper.png')

    # Enable ActiveDesktop
    try:
        progman = find_window_handles(window_class='Progman')[0]
        cryptic_params = (0x52c, 0, 0, 0, 500, None)
        user32.SendMessageTimeoutW(progman, *cryptic_params)
    except IndexError as e:
        raise WindowsError('Cannot enable Active Desktop') from e

    # Change Wallpaper
    pythoncom.CoInitialize()
    iad = pythoncom.CoCreateInstance(shell.CLSID_ActiveDesktop,
                                     None,
                                     pythoncom.CLSCTX_INPROC_SERVER,
                                     shell.IID_IActiveDesktop)
    iad.SetWallpaper(os.path.abspath('current_wallpaper.png'), 0)
    iad.ApplyChanges(shellcon.AD_APPLY_ALL)

    # Force Refresh
    user32.UpdatePerUserSystemParameters(1)

    # Print txt of current wallpapers
    f = open('current_wallpapers.txt', 'w', encoding="utf-8")
    for path in wallpaper_paths:
        f.write(f'{path}\n')
    f.close()

    # ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath('current_wallpaper.png') , 0)
    # Change wallpapers
    # https://stackoverflow.com/a/56974396
