"""漫画剧主图：目前只编排策划子图。"""

from langgraph.graph import END, START, StateGraph

from server.model import TextModel, build_text_model
from server.states import ComicDramaState
from server.subgraphs import build_planning_graph


def build_graph(text_model: TextModel):
    planning_graph = build_planning_graph(text_model)

    def planning(state: ComicDramaState) -> dict[str, object]:
        """在节点里调用策划子图，把整段策划流程作为一个节点跑完。"""
        child_result = planning_graph.invoke(state)
        # 子图返回完整事件历史；父图 reducer 只追加本轮新事件。
        return {
            **child_result,
            "events": child_result["events"][len(state["events"]) :],
        }

    builder = StateGraph(ComicDramaState)
    builder.add_node("planning_graph", planning)
    builder.add_edge(START, "planning_graph")
    builder.add_edge("planning_graph", END)

    return builder.compile()


graph = build_graph(build_text_model())
