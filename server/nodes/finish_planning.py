"""finish_planning。"""

from server.states import ComicDramaState


def finish_planning(state: ComicDramaState) -> dict[str, object]:
    """扇入后确认两路结果完整，才允许策划阶段结束。"""
    characters = state.get("characters") or []
    scenes = state.get("scenes") or []

    if not characters or not scenes:
        raise ValueError("角色或场景设定为空，策划不能完成")

    character_ids = [item.character_id for item in characters]
    scene_ids = [item.scene_id for item in scenes]

    if len(character_ids) != len(set(character_ids)):
        raise ValueError("角色 character_id 重复")

    if len(scene_ids) != len(set(scene_ids)):
        raise ValueError("场景 scene_id 重复")

    return {"current_stage": "planning_ready", "events": ["策划资料已汇合并通过检查"]}
