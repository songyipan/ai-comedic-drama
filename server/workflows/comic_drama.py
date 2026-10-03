"""漫画剧工作流图。"""

from langgraph.graph import END, START, StateGraph

from server.nodes import mark_planning_ready, receive_idea
from server.states import ComicDramaState


def build_comic_drama_graph():
    """连接接收创意和确认策划就绪两个节点。"""
    builder = StateGraph(ComicDramaState)
    builder.add_node("receive_idea", receive_idea)
    builder.add_node("mark_planning_ready", mark_planning_ready)
    builder.add_edge(START, "receive_idea")
    builder.add_edge("receive_idea", "mark_planning_ready")
    builder.add_edge("mark_planning_ready", END)
    return builder.compile()


graph = build_comic_drama_graph()
