# wallpaper-switcher

![](https://i.imgur.com/XxFeOvd.png)

A python script to better transition wallpapers for desktop background slideshows

The native Windows wallpaper slideshow does not deal well with mixing and matching wallpapers of different sizes to adequately tile your multi-monitor display, so I created a simple script to attempt to improve the process

## Features
- Script randomly picks a combination of provided wallpapers of varying monitor spans (currently single-, dual-, and triple-monitor wallpapers supported) that fit your current display, crops and stiches them together, and displays it as the desktop background.
- A "To-Sort" folder exists - add new wallpapers into it and they will be automatically sorted to their respective size folders
- The current generated wallpaper, along with a .txt listing the paths of the wallpapers used to generate it are saved to the script's directory

## Requirements
- Windows OS (Tested on Windows 10 v21H1)
- Python (Tested on Python 3.9.1)
- Packages as listed in `requirements.txt`

## Usage
- Install requirements in requirements.txt if not already: `pip install -r requirements.txt`
- Run the `setup.py` script in the folder that you wish to store the folder directories for the wallpapers on. The script can then be deleted.
- Add enough wallpapers to the respective folders (or into the "To-Sort" folder) such that the script will have enough wallpapers to tile your displays. **Not having this will likely make the script hang**.
- Move the `main.py` script into the folder with the created folders and use a job scheduler (e.g. Windows Task Scheduler) to have the script run and change wallpapers at your desired interval.

## Limitations

- As mentioned before, this currently only works on Windows (Tested on Windows 10 v21H1)
- All monitors need to be the same resolution currently