from server.agentic.agents.nodes import fetch_context_agent, code_quality_agent, security_agent, test_agent, performance_agent, aggregator_agent, PRState
from langgraph.graph import StateGraph, START, END

# Create graph
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

# Generate image bytes
image_bytes = workflow.get_graph().draw_mermaid_png()

# Write to file
with open("pr_review_workflow.png", "wb") as f:
    f.write(image_bytes)

print("Workflow image saved to pr_review_workflow.png")
