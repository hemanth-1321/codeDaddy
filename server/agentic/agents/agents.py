from typing import TypedDict, List
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

    similar_prs: List[SimilarPR]
    security_issues: List[str]
    code_quality_issues: List[str]
    performance_issues: List[str]
    test_suggestions: List[str]

    learnings: str
    final_review: str
    review_complete: bool

def fetch_context_agent(state: PRState) -> PRState:
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

    return {**state, "similar_prs": similar_pr, "learnings": str(learnings)}

def security_agent(state: PRState) -> PRState:
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
    combined_issues = state.get("security_issues", []) + issues
    return {**state, "security_issues": combined_issues}

def code_quality_agent(state: PRState) -> PRState:
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
    combined_issues = state.get("code_quality_issues", []) + issues
    return {**state, "code_quality_issues": combined_issues}

def performance_agent(state: PRState) -> PRState:
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
    combined_issues = state.get("performance_issues", []) + issues
    return {**state, "performance_issues": combined_issues}

def test_agent(state: PRState) -> PRState:
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
    combined_issues = state.get("test_suggestions", []) + issues
    return {**state, "test_suggestions": combined_issues}

def aggregator_agent(state: PRState) -> PRState:
    print("aggregator_agent running")

    security = "\n".join(f"- {s}" for s in state.get("security_issues", [])) or "None"
    quality = "\n".join(f"- {s}" for s in state.get("code_quality_issues", [])) or "None"
    performance = "\n".join(f"- {s}" for s in state.get("performance_issues", [])) or "None"
    tests = "\n".join(f"- {s}" for s in state.get("test_suggestions", [])) or "None"
    learnings = state.get("learnings", "None")

    prompt = f"""
You are an expert PR reviewer. Using the findings below, generate a **GitHub Markdown comment** ready to post on the PR.

Requirements:
- Use Markdown headings (##, ###) and bullet points.
- Include a short **Executive Summary** at the top.
- Mark critical issues clearly.
- Keep it concise, actionable, and professional.
- if found or used learning mention it as also in 2 lines

### Executive Summary
Provide a brief high-level overview of the PR review here.

### Security Findings:
{security}

### Code Quality Findings:
{quality}

### Performance Findings:
{performance}

### Test Suggestions:
{tests}

### Learnings:
{learnings}
"""
    resp = llm.invoke(prompt)
    return {**state, "final_review": resp.content, "review_complete": True}
