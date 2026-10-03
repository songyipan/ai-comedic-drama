"""确认用户原始需求已收到，标记可以进入策划。"""

from server.states import ComicDramaState


def mark_planning_ready(state: ComicDramaState):
    """确认原始需求已收到。"""
    raw_requirement = state.get("raw_requirement", "")

    if not raw_requirement:
        raise ValueError("raw_requirement不能为空")

    return {
        "current_stage": "planning_ready",
        "events": ["已确认收到用户原始需求"],
    }
