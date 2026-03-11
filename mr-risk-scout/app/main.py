from fastapi import FastAPI, Request, Header, HTTPException
from typing import Optional, Dict, Any

from .config import settings
from .models import GitLabMergeRequestEvent
from .gitlab_client import GitLabClient
from .risk_engine import analyze
from .reporter import format_comment, upsert_risk_comment

from .models import DebugAnalyzeRequest
from .risk_engine import analyze, risk_result_to_dict
from .reporter import format_comment

app = FastAPI(title="MR Risk Scout")

gl = GitLabClient(base_url=settings.gitlab_base_url, token=settings.gitlab_token)


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/webhook/gitlab")
async def gitlab_webhook(
    request: Request,
    x_gitlab_token: Optional[str] = Header(default=None),
):
    # 1) Verify webhook secret
    if not x_gitlab_token or x_gitlab_token != settings.gitlab_webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook token")

    payload: Dict[str, Any] = await request.json()

    # 2) Only handle merge_request events for now
    if payload.get("object_kind") != "merge_request":
        return {"ignored": True, "reason": "not a merge_request event"}

    event = GitLabMergeRequestEvent.from_payload(payload)

    project_id = event.project.id
    mr_iid = event.object_attributes.iid

    # Optional: ignore actions you don't want
    action = (event.object_attributes.action or "").lower()
    if action and action not in {"open", "update", "reopen"}:
        return {"ignored": True, "reason": f"action={action}"}

    # 3) Fetch MR changes
    changes_payload = await gl.get_mr_changes(project_id, mr_iid)
    changes = changes_payload.get("changes", [])

    # 4) Analyze risk (MVP rules-only)
    result = analyze(changes)

    # 5) Post or update a single comment
    comment = format_comment(event.object_attributes.title, result)
    note = await upsert_risk_comment(gl, project_id, mr_iid, comment)

    return {"ok": True, "risk": {"score": result.score, "level": result.level}, "note_id": note.get("id")}

@app.post("/debug/analyze")
async def debug_analyze(req: DebugAnalyzeRequest):
    # Run the same analyzer you use for real GitLab MRs
    result = analyze(req.changes)

    # Optional: show what the MR comment would look like
    comment_preview = format_comment(req.title or "Debug MR", result)

    return {
        "risk": risk_result_to_dict(result),
        "comment_preview": comment_preview,
        "changes_count": len(req.changes),
    }