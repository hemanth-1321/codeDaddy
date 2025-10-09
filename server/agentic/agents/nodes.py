from typing import TypedDict, List, Annotated
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
    # Use Annotated with add operator for fields that multiple agents update
    security_issues: Annotated[List[str], add]
    code_quality_issues: Annotated[List[str], add]
    performance_issues: Annotated[List[str], add]
    test_suggestions: Annotated[List[str], add]

    learnings: str
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
    
    # ONLY return the performance_issues key
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
    
    # ONLY return the test_suggestions key
    return {"test_suggestions": issues}

def aggregator_agent(state: PRState) -> dict:
    """
    Generates a comprehensive CodeRabbit-style PR review comment.
    """
    print("aggregator_agent running")

    security = state.get("security_issues", [])
    quality = state.get("code_quality_issues", [])
    performance = state.get("performance_issues", [])
    tests = state.get("test_suggestions", [])
    learnings = state.get("learnings", "")
    
    # Get PR metadata
    pr_title = state.get("pr_title", "PR Review")
    files_changed = state.get("files_changed", [])
    
    prompt = f"""
You are an expert PR reviewer like CodeRabbit. Generate a **comprehensive GitHub Markdown review comment** for this PR.

PR Title: {pr_title}
Files Changed: {len(files_changed)} files

### Review Data:

**Security Findings:**
{chr(10).join(f"- {s}" for s in security) if security else "✅ No security issues detected"}

**Code Quality Findings:**
{chr(10).join(f"- {q}" for q in quality) if quality else "✅ Code quality looks good"}

**Performance Findings:**
{chr(10).join(f"- {p}" for p in performance) if performance else "✅ No performance concerns"}

**Test Suggestions:**
{chr(10).join(f"- {t}" for t in tests) if tests else "✅ Test coverage appears adequate"}

**Learnings Applied:**
{learnings if learnings else "No specific learnings referenced"}

---

Generate a review comment following this EXACT structure:

## 🔍 PR Review Summary

### 📊 Overview
[2-3 sentence executive summary highlighting key changes and overall assessment]

### 🎯 Walkthrough
[Brief description of what this PR accomplishes and its scope]

---

### 📋 Changes

| Component/File(s) | Summary of Changes |
|-------------------|-------------------|
[Create a table row for each major change area with file paths and description]

---

### ⚠️ Issues Found

[ONLY include sections below if there are actual issues. Skip empty sections.]

#### 🔒 Security Issues
[List security findings with severity levels: 🔴 Critical, 🟡 Medium, 🟢 Low]

#### 🎨 Code Quality
[List code quality issues with specific file locations and line numbers]

#### ⚡ Performance Concerns
[List performance issues with recommendations]

#### 🧪 Testing Recommendations
[List test suggestions with rationale]

---

### ✅ Recommendations

[Prioritized list of actionable items:
1. [Most critical items first]
2. [Medium priority items]
3. [Nice-to-have improvements]]

---

### 📚 Applied Learnings
[If learnings were used, briefly mention them in 1-2 lines. Otherwise skip this section.]

---

### 💡 Additional Notes
[Any other observations, patterns noticed, or suggestions for future improvements]

---

**Review Status:** {"🔴 Changes Requested" if (security or quality or performance) else "✅ Approved"}

---
*Generated with ❤️ by AI PR Reviewer*

IMPORTANT FORMATTING RULES:
- Use proper markdown syntax with ##, ###, ####
- Use emoji for visual hierarchy (🔍 📊 🎯 ⚠️ 🔒 etc.)
- Include tables where appropriate
- Use bullet points with proper indentation
- Add severity indicators for issues (🔴🟡🟢)
- Keep descriptions concise but actionable
- Skip sections that have no findings
- Always maintain professional tone
- Include file paths and line numbers when referencing specific code
"""

    resp = llm.invoke(prompt)
    print("Final review generated")
    
    # Parse the response and add metadata
    review_content = resp.content
    
    # Calculate review stats
    total_issues = len(security) + len(quality) + len(performance)
    critical_issues = len(security)
    print(
       {
             "final_review": review_content,
        "review_complete": True,
        "total_issues": total_issues,
        "critical_issues": critical_issues,
        "review_status": "changes_requested" if total_issues > 0 else "approved",
       }
    )
    return {
        "final_review": review_content,
        "review_complete": True,
        "total_issues": total_issues,
        "critical_issues": critical_issues,
        "review_status": "changes_requested" if total_issues > 0 else "approved"
    }
