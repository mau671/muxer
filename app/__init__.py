"""
MKV Muxer Application

A tool for processing MKV files with automatic track naming and language configuration.
"""

__version__ = "0.1.0"
__author__ = "Mauricio González Prendas"

from .main import main
from .metadata_handler import get_mkv_metadata
from .muxer import mux_files
from .track_processor import process_tracks

__all__ = ["main", "get_mkv_metadata", "process_tracks", "mux_files"]
