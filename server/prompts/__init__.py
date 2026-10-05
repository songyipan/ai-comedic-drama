"""prompts。"""

from .sys_prompt import SYSTEM_PROMPT
from .story_prompt import STORY_PROMPT
from .character_prompt import CHARACTER_PROMPT
from .scene_prompt import SCENE_PROMPT
from .storyboard_prompt import STORYBOARD_PROMPT

__all__ = [
    "SYSTEM_PROMPT",
    "STORY_PROMPT",
    "STORYBOARD_PROMPT",
    "CHARACTER_PROMPT",
    "SCENE_PROMPT",
]
