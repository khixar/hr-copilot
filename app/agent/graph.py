from langgraph.graph import END, START, StateGraph

from app.agent.nodes import answer, classify, escalate, retrieve
from app.agent.state import AgentState


def _route(state: AgentState) -> str:
    return "escalate" if state["should_escalate"] else "answer"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("retrieve", retrieve)
    graph.add_node("classify", classify)
    graph.add_node("answer", answer)
    graph.add_node("escalate", escalate)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "classify")
    graph.add_conditional_edges("classify", _route)
    graph.add_edge("answer", END)
    graph.add_edge("escalate", END)

    return graph.compile()


compiled = build_graph()
