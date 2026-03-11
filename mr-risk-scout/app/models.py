from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class MergeRequestAttributes(BaseModel):
    iid: int
    id: int
    title: str
    state: str
    action: Optional[str] = None  # open/update/merge/close etc (depends on event)
    url: Optional[str] = None


class ProjectInfo(BaseModel):
    id: int
    web_url: Optional[str] = None
    path_with_namespace: Optional[str] = None


class GitLabMergeRequestEvent(BaseModel):
    object_kind: str
    project: ProjectInfo
    object_attributes: MergeRequestAttributes
    # Keep flexible so GitLab payload changes won't break us
    raw: Dict[str, Any] = {}

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "GitLabMergeRequestEvent":
        return cls(
            object_kind=payload.get("object_kind", ""),
            project=ProjectInfo(**payload.get("project", {})),
            object_attributes=MergeRequestAttributes(**payload.get("object_attributes", {})),
            raw=payload,
        )
    

class DebugAnalyzeRequest(BaseModel):
    title: Optional[str] = "Debug MR"
    changes: List[Dict[str, Any]]