"""storyboard_ready。"""

from server.states import ComicDramaState


def storyboard_ready(state: ComicDramaState) -> dict[str, object]:
    """校验通过分支的路由终点，只推进阶段。"""
    return {
        "current_stage": "quality_passed",
        "events": ["分镜已就绪，等待审核"],
    }
