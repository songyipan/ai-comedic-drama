from typing import Literal

from langgraph.graph import END, START, StateGraph

from server.model import TextModel, build_text_model
from server.nodes import (
    finish_planning,
    make_analyze_requirement,
    make_generate_characters,
    make_generate_scenes,
    make_generate_story_outline,
    make_generate_storyboard,
    receive_idea,
    storyboard_invalid,
    storyboard_ready,
    validate_storyboard,
)
from server.states import ComicDramaState


def route_storyboard_validation(
    state: ComicDramaState,
) -> Literal["storyboard_ready", "storyboard_invalid"]:
    """按校验结果把流程分流到就绪或待修订终点。

    返回注解用 Literal 写明分支目标，LangGraph 依赖它推断条件边的两个去向。
    """
    validation = state["storyboard_validation"]
    if validation.is_valid:
        return "storyboard_ready"
    return "storyboard_invalid"


def build_graph(text_model: TextModel):
    builder = StateGraph(ComicDramaState)
    builder.add_node("receive_idea", receive_idea)
    builder.add_node("analyze_requirement", make_analyze_requirement(text_model))
    builder.add_node("generate_story_outline", make_generate_story_outline(text_model))
    builder.add_node("generate_characters", make_generate_characters(text_model))
    builder.add_node("generate_scenes", make_generate_scenes(text_model))
    builder.add_node("finish_planning", finish_planning)
    builder.add_node("generate_storyboard", make_generate_storyboard(text_model))
    builder.add_node("validate_storyboard", validate_storyboard)
    builder.add_node("storyboard_ready", storyboard_ready)
    builder.add_node("storyboard_invalid", storyboard_invalid)

    builder.add_edge(START, "receive_idea")
    builder.add_edge("receive_idea", "analyze_requirement")
    builder.add_edge("analyze_requirement", "generate_story_outline")
    builder.add_edge("generate_story_outline", "generate_characters")
    builder.add_edge("generate_story_outline", "generate_scenes")
    builder.add_edge(["generate_characters", "generate_scenes"], "finish_planning")
    builder.add_edge("finish_planning", "generate_storyboard")
    builder.add_edge("generate_storyboard", "validate_storyboard")
    builder.add_conditional_edges("validate_storyboard", route_storyboard_validation)
    builder.add_edge("storyboard_ready", END)
    builder.add_edge("storyboard_invalid", END)

    return builder.compile()


graph = build_graph(build_text_model())
