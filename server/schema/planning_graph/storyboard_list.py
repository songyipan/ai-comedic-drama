"""真实模型结构化输出需要顶层对象，State 只保存内部 shots。"""

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from server.schema.storyboard import Storyboard


class StoryBoardList(BaseModel):

    model_config = ConfigDict(extra="forbid")
    storyboard_list: list[Storyboard] = Field(min_length=1)
