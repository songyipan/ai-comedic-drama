"""storyboard_invalid。"""

from server.states import ComicDramaState


def storyboard_invalid(state: ComicDramaState) -> dict[str, object]:
    """校验未通过分支的路由终点，只推进阶段。"""
    return {
        "current_stage": "storyboard_invalid",
        "events": ["分镜校验未通过，等待修订"],
    }
