import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller build."""
    if hasattr(sys, "_MEIPASS"):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running from source
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
