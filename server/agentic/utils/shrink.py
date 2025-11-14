
from server.agentic.agents.nodes import PRState

def shrink_text(text: str, max_chars: int = 4000) -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]..."
    

def shrink_similar_prs(similar_prs, max_items=3, max_ctx=500):
    if not similar_prs:
        return []
    new_list = []
    for pr in similar_prs[:max_items]:
        ctx = pr.get("context", "")
        if len(ctx) > max_ctx:
            ctx = ctx[:max_ctx] + "...[truncated]"
        new_list.append({
            "ref_id": pr.get("ref_id", ""),
            "context": ctx,
            "score": pr.get("score", 0.0),
        })
    return new_list

def compress_state(state: PRState) -> PRState:
    # Copy original so we don't mutate state between nodes
    new_state = dict(state)

    # Compress large fields
    new_state["diff_content"] = shrink_text(state.get("diff_content", ""), 5000)
    new_state["pr_description"] = shrink_text(state.get("pr_description", ""), 2000)

    # Compress similar PRs context
    new_state["similar_prs"] = shrink_similar_prs(state.get("similar_prs", []))

    return new_state

