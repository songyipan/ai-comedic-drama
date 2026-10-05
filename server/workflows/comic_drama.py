"""漫画剧主图：目前只编排策划子图。"""

from langgraph.graph import END, START, StateGraph

from server.states import ComicDramaState
from server.subgraphs import planning_graph


def build_graph():
    builder = StateGraph(ComicDramaState)
    builder.add_node("planning_graph", planning_graph)
    builder.add_edge(START, "planning_graph")
    builder.add_edge("planning_graph", END)

    return builder.compile()


graph = build_graph()
