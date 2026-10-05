"""硬规则结果；失败时保留可定位的错误给后续修订节点。"""

from pydantic import (
    BaseModel,
    ConfigDict,
)


class StoryboardValidation(BaseModel):

    model_config = ConfigDict(extra="forbid")
    is_valid: bool
    errors: list[str]
