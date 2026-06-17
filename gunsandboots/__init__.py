"""Guns and Boots - A tactical combat game"""
__version__ = "1.0.0"

# Import main function
import sys
import os

# Add parent directory to path to import main modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main

__all__ = ["main"]
