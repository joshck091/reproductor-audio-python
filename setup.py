import os
import shutil
from setuptools import setup

APP = ['repmp3.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame', 'mutagen', 'tkinterdnd2'],
    'includes': ['tkinter'],
}

# Elimina las carpetas anteriores automáticamente
for folder in ('build', 'dist'):
    if os.path.exists(folder):
        print(f"Eliminando carpeta {folder}...")
        shutil.rmtree(folder)

setup(
    app=APP,
    name='Reproductor MP3 RO5K4',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
