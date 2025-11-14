import os
from server.agentic.agents.nodes import PRState
from server.agentic.utils.llm_client import llm
from server.servcies.github import post_pr_comment, update_pr_comment


def aggregator_agent(state: PRState) -> dict:
 
    print("aggregator_agent running")

    security = state.get("security_issues", [])
    quality = state.get("code_quality_issues", [])
    performance = state.get("performance_issues", [])
    tests = state.get("test_suggestions", [])
    learnings = state.get("learnings", "")
    
    # Get PR metadata
    pr_title = state.get("pr_title", "PR Review")
    files_changed = state.get("files_changed", [])
    pr_description = state.get("pr_description", "")
    pr_number = state.get("pr_number", "")
    repo_name = state.get("repo_name", "")
    
    # NEW: Get progress comment info
    progress_comment_id = state.get("progress_comment_id")
    owner = state.get("owner", "")
    repo = state.get("repo", "")
    installation_id = state.get("installation_id")

    # Fallback: Extract owner/repo if not provided
    if not owner or not repo:
        try:
            owner, repo = repo_name.split("/")
        except ValueError:
            raise ValueError(f"Invalid repo_name format: '{repo_name}'. Expected 'owner/repo'.")

    file_issues = {}
    for issue in security + quality + performance:
        for file_path in files_changed:
            if file_path in str(issue):
                if file_path not in file_issues:
                    file_issues[file_path] = []
                file_issues[file_path].append(issue)
    
    prompt = f"""
You are CodeDaddy, an expert AI code reviewer. Generate a comprehensive GitHub PR review comment.

PR Title: {pr_title}
PR Description: {pr_description}
Files Changed: {len(files_changed)} files
File List: {', '.join(files_changed[:5])}{"..." if len(files_changed) > 5 else ""}

### Review Data:
Key point: **any direct console or stderr print used for debugging (`print`, `println`, `console.log`, `eprintln`) should be flagged and asked to be removed in just in single sentence.**  
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

Generate a CodeRabbit-style review following this EXACT structure:

## Walkthrough

[2-3 sentences describing what this PR accomplishes - be specific about the features/changes added]

## Changes

| Cohort / File(s) | Summary |
|------------------|---------|
{chr(10).join(f"| **{file_path.split('/')[-2] if '/' in file_path else 'Root'}** | [Describe changes] |" for file_path in files_changed[:3])}
| ... | ... |

---

[IF there are significant code changes to highlight, create a section like this:]

### 🔧 Key Implementation Details

**[Feature/Component Name]**

Describe the main changes in 2-3 sentences, highlighting architectural decisions or important patterns.

---

## Poem

[Generate a creative 4-5 line poem about the PR changes, using proper markdown blockquote]

> Your Daddy reviews code with care and grace,  
> [Line 2 about the specific changes]  
> [Line 3 about the improvements]  
> [Line 4 celebrating the work] 🐰✨

---

> [!TIP]
> **🔮 [Clever tip related to the changes]**
> 
> [1-2 sentences with actionable advice]

---

<details>
<summary>✨ Finishing Touches</summary>

[Add 2-3 small polish suggestions or nice-to-haves that would enhance the PR]

</details>

---

## Review Comments

[IF there are issues, structure them as actionable comments:]

### 📁 **[filename.ext]**

**Comment on lines +[line_start] to +[line_end]**

[Issue description with severity emoji: 🔴 Critical, 🟡 Medium, 🟢 Low]

**Suggestion:**
```[language]
// Show corrected code snippet
```

**Rationale:** [Explain why this matters]

---

[Repeat for each file with issues]

---

## Summary by CodeDaddy

- **New Features**
  - [List new features added]
  - [Another feature]

- **Bug Fixes**
  - [List any bugs fixed]

- **Improvements**
  - [List improvements made]
  - [Performance enhancements]

- **Tests**
  - [Test coverage additions]

- **Documentation**
  - [Any doc updates]

---

Thanks for using code-Daddy! It's free for OSS, and your support helps us grow. If you like it, consider giving us a shout-out.

<details>
<summary>❤️ Share</summary>

[Add a brief thank you message]

</details>

<details>
<summary>📚 Tips</summary>

[Add 2-3 helpful tips for using code-Daddy or improving the PR]

</details>

---

CRITICAL FORMATTING RULES:
1. Use GitHub markdown alerts: > [!NOTE], > [!TIP], > [!WARNING]
2. Use <details> tags for collapsible sections
3. Include emojis liberally: 🔴🟡🟢✅🔧🔮✨🧔🏻‍♂️❤️📚
4. Create actual file-specific comments with line numbers when issues are found
5. Always include the poem - make it creative and relevant
6. Add "Actionable comments posted: [N]" section if there are inline comments
7. Use proper markdown tables with alignment
8. Keep the professional yet friendly CodeRabbit tone
9. Include expandable sections (Finishing Touches, Share, Tips)
10. End with the signature "Thanks for using CodeDaddy!"
11. Structure issues as specific, actionable comments on code blocks
12. Use syntax highlighting in code blocks

Make it look EXACTLY like a real CodeDaddy review with all the visual polish and helpful structure.
"""

    resp = llm.invoke(prompt)
    review_content = resp.content
    
    print("Final CodeRabbit-style review generated")
    
    total_issues = len(security) + len(quality) + len(performance)
    critical_issues = len(security)
    
    actionable_comments = sum(len(issues) for issues in file_issues.values())
    
    result = {
        "final_review": review_content,
        "review_complete": True,
        "total_issues": total_issues,
        "critical_issues": critical_issues,
        "actionable_comments": actionable_comments,
        "review_status": "changes_requested" if total_issues > 0 else "approved",
        "files_with_comments": list(file_issues.keys())
    }
    
    print(f"Review stats: {result}")
    
    # Post or update the comment
    if progress_comment_id:
        # Update the existing "in progress" comment
        try:
            print(f"Updating progress comment {progress_comment_id} with final review")
            update_pr_comment(
                comment_id=progress_comment_id,
                owner=owner,
                repo=repo,
                body=review_content,
                installation_id=installation_id
            )
            print("✅ Progress comment updated with final review")
        except Exception as e:
            print(f"❌ Failed to update comment {progress_comment_id}: {e}")
            print("Posting as new comment instead")
            post_pr_comment(
                pr_number=pr_number,
                owner=owner,
                repo=repo,
                body=review_content,
                installation_id=installation_id
            )
    else:
        print("No progress comment found, posting new comment")
        post_pr_comment(
            pr_number=pr_number,
            owner=owner,
            repo=repo,
            body=review_content,
            installation_id=installation_id
        )
    
    return result