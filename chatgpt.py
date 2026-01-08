"""
Backward-compatible re-export module.

Old code imports from `chatgpt.py`; new architecture keeps real code in `services/openai_service.py`
and history helpers in `data/history.py`.
"""

from data.history import format_history, get_conversation_context, load_history  # noqa: F401
from services.openai_service import (  # noqa: F401
    chatgpt_text,
    describe_image,
    image_to_anime,
    speech_to_text,
    text_to_image,
    transform_image_with_instruction,
)