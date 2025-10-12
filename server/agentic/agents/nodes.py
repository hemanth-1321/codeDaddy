from typing import TypedDict, List, Annotated,Optional
from operator import add
from server.agentic.utils.llm_client import llm
from server.agentic.utils.vector_tool import search_vector_tool, search_learnings_tool

class SimilarPR(TypedDict):
    ref_id: str
    context: str
    score: float

class PRState(TypedDict):
    pr_number: int
    repo_name: str
    diff_content: str
    pr_description: str

    similar_prs: list
    security_issues: Annotated[List[str], add]
    code_quality_issues: Annotated[List[str], add]
    performance_issues: Annotated[List[str], add]
    test_suggestions: Annotated[List[str], add]
    commit_sha:int
    learnings: str
    progress_comment_id: Optional[int]
    final_review: str
    review_complete: bool

def fetch_context_agent(state: PRState) -> dict:
    print("fetch_context_agent running")
    search_query = f"{state.get('pr_number', '')} {state.get('repo_name', '')}"

    raw_similar_pr = search_vector_tool(search_query)
    similar_pr: List[SimilarPR] = [
        {
            "ref_id": str(item.get("ref_id", "")),
            "context": str(item.get("context", "")),
            "score": float(item.get("score", 0.0))
        }
        for item in raw_similar_pr
    ]

    learnings = search_learnings_tool(search_query)

    # ONLY return the keys you're updating
    return {"similar_prs": similar_pr, "learnings": str(learnings)}

def security_agent(state: PRState) -> dict:
    print("security_agent running")
    learnings = state.get("learnings", "")
    context = state.get("similar_prs", [])

    prompt = f"""
You are a security expert. Review the diff and historical context and list security issues.

PR #{state['pr_number']} - {state['repo_name']}
Description:
{state.get('pr_description', '')}

Diff:
{state.get('diff_content', '')}

Learnings:
{learnings}

Context (similar PRs):
{context}

Return each finding on a separate line, prefixed with severity (CRITICAL / MAJOR / MINOR) if applicable.
"""
    res = llm.invoke(prompt)
    issues = [line.strip() for line in res.content.splitlines() if line.strip()]
    
    # ONLY return the security_issues key
    return {"security_issues": issues}

def code_quality_agent(state: PRState) -> dict:
    print("code_quality_agent running")
    learnings = state.get("learnings", "")
    context = state.get("similar_prs", [])

    prompt = f"""
You are a code quality expert. For the given PR diff, return a bullet list of code quality issues.

PR #{state['pr_number']} - {state['repo_name']}
Diff:
{state.get('diff_content', '')}

Learnings:
{learnings}

Context:
{context}

Check: naming conventions, duplication, readability, anti-patterns.
"""
    res = llm.invoke(prompt)
    issues = [line.strip() for line in res.content.splitlines() if line.strip()]
    
    # ONLY return the code_quality_issues key
    return {"code_quality_issues": issues}

def performance_agent(state: PRState) -> dict:
    print("performance_agent running")
    learnings = state.get("learnings", "")
    context = state.get("similar_prs", [])

    prompt = f"""
You are a performance expert. Identify potential performance issues in this PR diff.

PR #{state['pr_number']} - {state['repo_name']}
Diff:
{state.get('diff_content', '')}

Learnings:
{learnings}

Context:
{context}
"""
    res = llm.invoke(prompt)
    issues = [line.strip() for line in res.content.splitlines() if line.strip()]
    
    return {"performance_issues": issues}

def test_agent(state: PRState) -> dict:
    print("test_agent running")
    learnings = state.get("learnings", "")
    context = state.get("similar_prs", [])

    prompt = f"""
You are a testing expert. Based on the PR diff, suggest:
- Unit tests
- Edge cases
- Integration tests or mocks needed

PR #{state['pr_number']} - {state['repo_name']}
Diff:
{state.get('diff_content', '')}

Learnings:
{learnings}

Context:
{context}
"""
    res = llm.invoke(prompt)
    issues = [line.strip() for line in res.content.splitlines() if line.strip()]
    
    return {"test_suggestions": issues}
