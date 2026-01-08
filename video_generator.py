"""
Backward-compatible re-export module.

New architecture keeps video generation in `services/video_service.py`.
"""

from services.video_service import *  # noqa: F403,F401
