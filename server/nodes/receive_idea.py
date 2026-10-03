"""接收并完成最小输入检查的节点"""

from server.states import ComicDramaState


def receive_idea(state: ComicDramaState):
    """接收并完成最小输入检查"""
    raw_requirement = state.get("raw_requirement", "")

    if not raw_requirement:
        raise ValueError("raw_requirement不能为空")

    return {
        "raw_requirement": raw_requirement,
        "current_stage": "idea_received",
        "events": ["已接收用户创意"],
    }
