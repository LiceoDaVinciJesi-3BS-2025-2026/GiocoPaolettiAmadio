# resources - presenta le funzioni per caricare materiali (immagini e suoni nel gioco).

# License: See LICENSE file in the project root for details.

# Authors: 
# Leonardo Paoletti <leopaoletti09@gmail.com>
# Sebastiano Amadio <sebastianoamadio09@gmail.com>

from importlib.resources import files
from pathlib import Path

#funzioni per indicare il path da seguire per caricare materiali nel gioco
def get_sound(filename: str) -> Path:
    return files(__package__) / "sounds" / filename

def get_image(filename: str) -> Path:
    return files(__package__) / "images" / filename