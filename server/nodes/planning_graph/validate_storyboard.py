"""校验分镜的硬规则，失败时保留可定位的错误给修订环节。"""

from server.schema import (
    CharacterProfile,
    CreativeRequirement,
    SceneProfile,
    Storyboard,
    StoryboardValidation,
)
from server.states import ComicDramaState


def validate_storyboard(state: ComicDramaState) -> dict[str, object]:
    """只产出校验结果与事件，阶段流转交给 storyboard_ready / storyboard_invalid。"""
    storyboard = state.get("storyboard")
    requirement = state.get("requirement")
    characters = state.get("characters")
    scenes = state.get("scenes")
    if storyboard is None or requirement is None or characters is None or scenes is None:
        raise ValueError("缺少分镜、需求、角色或场景，不能校验分镜")

    errors = check_storyboard_rules(
        shots=storyboard,
        requirement=requirement,
        characters=characters,
        scenes=scenes,
    )
    validation = StoryboardValidation(is_valid=not errors, errors=errors)

    if errors:
        return {
            "storyboard_validation": validation,
            "events": [f"分镜未通过质量校验：{len(errors)} 处错误"],
        }
    return {
        "storyboard_validation": validation,
        "events": ["分镜通过质量校验"],
    }


def check_storyboard_rules(
    *,
    shots: list[Storyboard],
    requirement: CreativeRequirement,
    characters: list[CharacterProfile],
    scenes: list[SceneProfile],
) -> list[str]:
    """返回全部硬规则错误；空列表表示分镜合格。"""
    errors = []

    # 镜头数与总时长必须与需求严格一致
    if len(shots) != requirement.shot_count:
        errors.append(
            f"分镜共 {len(shots)} 镜，与目标镜头数 {requirement.shot_count} 不一致"
        )
    total_seconds = sum(shot.duration_seconds for shot in shots)
    if total_seconds != requirement.duration_seconds:
        errors.append(
            f"分镜总时长 {total_seconds} 秒，与目标总时长 {requirement.duration_seconds} 秒不一致"
        )

    # shot_id 不允许重复，order 必须从 1 连续到镜头数
    orders_by_id: dict[str, list[int]] = {}
    for shot in shots:
        orders_by_id.setdefault(shot.shot_id, []).append(shot.order)
    for shot_id, orders in orders_by_id.items():
        if len(orders) > 1:
            errors.append(
                f"shot_id 重复：{shot_id}（序号 {'、'.join(str(order) for order in orders)}）"
            )
    actual_orders = sorted(shot.order for shot in shots)
    if actual_orders != list(range(1, len(shots) + 1)):
        errors.append(
            f"镜头序号必须从 1 连续到 {len(shots)}，实际为 {actual_orders}"
        )

    # 只能引用已登记的角色与场景
    character_ids = {item.character_id for item in characters}
    scene_ids = {item.scene_id for item in scenes}
    for shot in shots:
        if shot.scene_id not in scene_ids:
            errors.append(f"第 {shot.order} 镜引用了未登记场景：{shot.scene_id}")
        for character_id in shot.character_ids:
            if character_id not in character_ids:
                errors.append(f"第 {shot.order} 镜引用了未登记角色：{character_id}")

    return errors
