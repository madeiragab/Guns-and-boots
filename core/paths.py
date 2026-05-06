import os
import sys


def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_runtime_root():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return get_project_root()


def get_assets_root():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "assets")
    return os.path.join(get_project_root(), "assets")


def get_asset_path(*parts):
    return os.path.join(get_assets_root(), *parts)
