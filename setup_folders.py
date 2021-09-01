import os
from pathlib import Path

from main import size_folders, TO_SORT_FOLDER, OTHER_FOLDER

# Create folder structure if not already exists

for key, value in size_folders.items():
	if not Path(value).is_dir():
		os.makedirs(value)

if not Path(TO_SORT_FOLDER).is_dir():
	os.makedirs(TO_SORT_FOLDER)
	
if not Path(OTHER_FOLDER).is_dir():
	os.makedirs(OTHER_FOLDER)