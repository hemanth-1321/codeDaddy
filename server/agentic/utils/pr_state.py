from typing import TypedDict, List, Annotated, Optional
from operator import add

class PRState(TypedDict):
    pr_number: int
    repo_name: str
    diff_content: str
    pr_description: str
    installation_id: int
    similar_prs: list
    security_issues: Annotated[List[str], add]
    code_quality_issues: Annotated[List[str], add]
    performance_issues: Annotated[List[str], add]
    test_suggestions: Annotated[List[str], add]
    commit_sha: int
    learnings: str
    progress_comment_id: Optional[int]
    final_review: str
    review_complete: bool
