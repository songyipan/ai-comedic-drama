from langgraph.graph import END, START, StateGraph

from server.model import TextModel, build_text_model
from server.nodes import make_analyze_requirement, receive_idea
from server.states import ComicDramaState


def build_graph(text_model: TextModel):
    builder = StateGraph(ComicDramaState)
    builder.add_node("receive_idea", receive_idea)
    builder.add_node("analyze_requirement", make_analyze_requirement(text_model))

    builder.add_edge(START, "receive_idea")
    builder.add_edge("receive_idea", "analyze_requirement")
    builder.add_edge("analyze_requirement", END)

    return builder.compile()


graph = build_graph(build_text_model())
