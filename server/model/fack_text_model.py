"""假模型"""

from typing import Any

from server.schema import (
    CharacterProfile,
    CreativeRequirement,
    SceneProfile,
    StoryOutline,
    Storyboard,
)

# 《零点之后》的五个故事节拍，镜头数不足就取前几个，超出就循环并给 shot_id 加序号
_STORY_BEATS = [
    {
        "shot_id": "shot_meeting",
        "action": "深夜办公室里，小林还在敲键盘赶工，屏幕旁忽然亮起微光，阿沐从漫画里探身跨出。",
        "composition": "小林位于画面左侧台灯暖光下，阿沐在右侧屏幕旁现身，背景是落地窗外的深蓝夜景。",
        "dialogue": "阿沐：咦，这里就是你的世界吗？",
        "camera_motion": "固定机位",
        "start_frame": "深夜办公室，暖黄台灯下穿浅灰衬衫的小林对着电脑敲键盘，落地窗外是深蓝夜景。",
        "end_frame": "暖黄台灯下，黑色长发的阿沐站在电脑旁回头看向屏幕，小林惊讶地转过身。",
        "video_prompt": "屏幕白光闪动，阿沐从画面里探身跨出落到办公桌旁，小林转头瞪大眼睛。",
    },
    {
        "shot_id": "shot_deadline",
        "action": "阿沐指向墙上的挂钟说明来意，小林从工位起身凑近屏幕。",
        "composition": "阿沐在前景中央抬手指向背景挂钟，小林在右侧起身望向她。",
        "dialogue": "阿沐：零点前我必须回到漫画，不然我会从故事里消失。",
        "camera_motion": "固定机位",
        "start_frame": "阿沐站在办公桌旁抬手指向墙上挂钟，小林半起身望向她，暖黄台灯光覆盖前景。",
        "end_frame": "挂钟指针逼近零点，两人并肩站在亮着的屏幕前。",
        "video_prompt": "阿沐焦急地比划并指向挂钟，小林从工位起身走到屏幕前。",
    },
    {
        "shot_id": "shot_search",
        "action": "两人在办公区的旧纸箱堆里翻找被遗落的最后一页。",
        "composition": "小林蹲在画面左侧翻纸箱，阿沐在右侧举起一张画稿对照。",
        "dialogue": "小林：被遗落的最后一页，会混在这些旧稿里吗？",
        "camera_motion": "固定机位",
        "start_frame": "暖黄台灯下，小林蹲在纸箱堆旁翻找画稿，阿沐在旁边举着画稿对照。",
        "end_frame": "阿沐从纸箱里抽出一张泛黄画稿，两人凑到灯下查看。",
        "video_prompt": "两人交替翻动纸箱里的画稿，阿沐抽出一张泛黄画稿举到灯下。",
    },
    {
        "shot_id": "shot_drawing",
        "action": "小林摊开空白稿纸提笔作画，阿沐在旁边屏息注视。",
        "composition": "小林在台灯下居于画面中央执笔，阿沐站在右侧俯身看着纸面。",
        "dialogue": "小林：原来最后一页，要由我来画完。",
        "camera_motion": "缓慢推近",
        "start_frame": "台灯下小林摊开空白稿纸握着笔，阿沐站在右侧俯身注视。",
        "end_frame": "稿纸上画出阿沐回到漫画的轮廓，她的眼里映出画稿的线条。",
        "video_prompt": "小林落笔画出线条，镜头缓慢推近稿纸，阿沐屏息注视。",
    },
    {
        "shot_id": "shot_farewell",
        "action": "零点钟声响起，阿沐挥手化作光点，回到屏幕中的漫画里。",
        "composition": "阿沐在前景中央挥手，屏幕在背景亮起，小林在右侧挥手回应。",
        "dialogue": "阿沐：等下一页画好，我们就会重逢。",
        "camera_motion": "固定机位",
        "start_frame": "阿沐站在亮起的屏幕前挥手，小林在右侧挥手回应，暖黄与深蓝光影交错。",
        "end_frame": "阿沐化作光点没入屏幕，小林对着亮着的漫画页面微笑。",
        "video_prompt": "阿沐挥手后化作光点飘向屏幕，光点没入漫画页面，页面泛起微光。",
    },
]


class FakeTextModel:
    """本地开发使用的确定性替身，不发起任何网络请求。"""

    def __init__(
        self,
        response: dict[str, Any] | None = None,
        *,
        planning_fault: str = "none",
        storyboard_fault: str = "none",
    ) -> None:
        self._response = response
        self._planning_fault = planning_fault
        self._storyboard_fault = storyboard_fault

    def analyze_requirement(self, raw_requirement: str) -> CreativeRequirement:
        response = self._response or {
            "title": "零点之后",
            "genre": "都市奇幻",
            "target_audience": "喜欢悬疑反转的年轻观众",
            "duration_seconds": 45,
            "shot_count": 5,
            "visual_style": "冷暖对比的二维漫画",
            "aspect_ratio": "9:16",
            "core_idea": raw_requirement,
            "constraints": [],
        }
        return CreativeRequirement.model_validate(response)

    def generate_story_outline(self, requirement: CreativeRequirement) -> StoryOutline:
        return StoryOutline(
            opening="小林在深夜办公室加班，漫画角色阿沐突然出现在屏幕旁。",
            conflict="阿沐必须在零点前回到漫画，否则会从故事中消失。",
            development="小林和阿沐寻找被遗落的最后一页，逐渐理解彼此的孤独。",
            turning_point="小林发现最后一页需要由自己画出，才能让故事继续。",
            ending="零点钟声响起，阿沐回到漫画，留下两人重逢的约定。",
            theme="用创作连接两个世界，也让孤独的人获得陪伴。",
        )

    def generate_characters(
        self, requirement: CreativeRequirement, outline: StoryOutline
    ) -> list[CharacterProfile]:
        if self._planning_fault == "characters":
            raise ValueError("Fake 角色分支故意失败")

        return [
            CharacterProfile(
                character_id="char_xiaolin",
                name="小林",
                identity="深夜加班的程序员",
                personality="认真但有些孤独",
                appearance="短发，眼下略有倦意",
                clothing="浅灰衬衫与深色长裤",
                visual_keywords=["短发", "浅灰衬衫"],
            ),
            CharacterProfile(
                character_id="char_amu",
                name="阿沐",
                identity="从漫画中走出的女孩",
                personality="勇敢而温柔",
                appearance="黑色长发，明亮的眼睛",
                clothing="暖黄色外套与白色裙子",
                visual_keywords=["黑色长发", "暖黄色外套"],
            ),
        ]

    def generate_scenes(
        self, requirement: CreativeRequirement, outline: StoryOutline
    ) -> list[SceneProfile]:
        if self._planning_fault == "scenes":
            raise ValueError("Fake 场景分支故意失败")

        return [
            SceneProfile(
                scene_id="scene_office",
                name="深夜办公室",
                time="午夜前后",
                location="电脑桌与落地窗相邻的开放办公区",
                lighting="台灯暖光与窗外冷光交错",
                colors="暖黄和深蓝",
                visual_keywords=["二维漫画", "暖黄台灯", "深蓝夜景"],
            )
        ]

    def generate_storyboard(
        self,
        requirement: CreativeRequirement,
        outline: StoryOutline,
        characters: list[CharacterProfile],
        scenes: list[SceneProfile],
    ) -> list[Storyboard]:
        if not scenes:
            raise ValueError("缺少已登记场景，不能生成分镜")

        # 需求自带的校验器已保证总时长能落在 2~12 秒 × 镜头数内，均分后无需再夹范围
        count = requirement.shot_count
        base, extra = divmod(requirement.duration_seconds, count)
        scene_id = scenes[0].scene_id
        lead_ids = [character.character_id for character in characters[:2]]
        style = requirement.visual_style

        shots = []
        for index in range(count):
            beat = _STORY_BEATS[index % len(_STORY_BEATS)]
            suffix = f"_{index // len(_STORY_BEATS) + 1}" if index >= len(_STORY_BEATS) else ""
            shots.append(
                Storyboard(
                    shot_id=beat["shot_id"] + suffix,
                    order=index + 1,
                    duration_seconds=base + (1 if index < extra else 0),
                    scene_id=scene_id,
                    character_ids=list(lead_ids),
                    action=beat["action"],
                    composition=beat["composition"],
                    dialogue=beat["dialogue"],
                    camera_motion=beat["camera_motion"],
                    start_frame_prompt=f"{style}，{beat['start_frame']}",
                    end_frame_prompt=f"{style}，{beat['end_frame']}",
                    video_prompt=beat["video_prompt"],
                )
            )

        # 三种分镜故障都保持字段级校验通过，只能被后续语义校验节点识别
        fault = self._storyboard_fault
        if fault == "duplicate_id":
            shots[1] = shots[1].model_copy(update={"shot_id": shots[0].shot_id})
        elif fault == "unknown_character":
            shots[0] = shots[0].model_copy(
                update={"character_ids": [*shots[0].character_ids, "char_ghost"]}
            )
        elif fault == "duration_mismatch":
            last = shots[-1]
            drift = last.duration_seconds - 1 if last.duration_seconds > 2 else last.duration_seconds + 1
            shots[-1] = last.model_copy(update={"duration_seconds": drift})

        return shots
