from server.agentic.agents.nodes import fetch_context_agent, code_quality_agent, security_agent, test_agent, performance_agent, PRState
from server.agentic.agents.aggregator_agent import aggregator_agent
from langgraph.graph import StateGraph, START, END

graph = StateGraph(PRState)

graph.add_node("fetch_context_agent", fetch_context_agent)
graph.add_node("security_agent", security_agent)
graph.add_node("code_quality_agent", code_quality_agent)
graph.add_node("performance_agent", performance_agent)
graph.add_node("test_agent", test_agent)
graph.add_node("aggregator_agent", aggregator_agent)

graph.add_edge(START, "fetch_context_agent")
graph.add_edge("fetch_context_agent", "security_agent")
graph.add_edge("fetch_context_agent", "code_quality_agent")
graph.add_edge("fetch_context_agent", "performance_agent")
graph.add_edge("fetch_context_agent", "test_agent")
graph.add_edge("security_agent", "aggregator_agent")
graph.add_edge("code_quality_agent", "aggregator_agent")
graph.add_edge("performance_agent", "aggregator_agent")
graph.add_edge("test_agent", "aggregator_agent")
graph.add_edge("aggregator_agent", END)


# Compile workflow
workflow = graph.compile()

