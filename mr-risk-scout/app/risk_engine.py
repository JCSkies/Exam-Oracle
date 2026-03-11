from dataclasses import dataclass
from typing import List, Dict, Any


HIGH_RISK_PATH_HINTS = [
    "auth", "security", "middleware",
    "infra", "deploy", ".gitlab-ci.yml",
    "migrations", "db/migrations",
    "config", ".env", "secrets",
]


@dataclass
class RiskResult:
    score: int  # 0-10
    level: str  # Low/Medium/High
    reasons: List[str]
    stats: Dict[str, Any]


def _level(score: int) -> str:
    if score <= 3:
        return "Low"
    if score <= 6:
        return "Medium"
    return "High"


def analyze(changes: List[Dict[str, Any]]) -> RiskResult:
    # changes: list of {"old_path","new_path","diff",...}
    files = []
    additions = 0
    deletions = 0

    for c in changes:
        path = c.get("new_path") or c.get("old_path") or ""
        files.append(path)
        diff = c.get("diff", "") or ""
        # super rough churn estimate
        additions += diff.count("\n+") - (1 if diff.startswith("+") else 0)
        deletions += diff.count("\n-") - (1 if diff.startswith("-") else 0)

    file_count = len(files)
    churn = max(0, additions) + max(0, deletions)

    score = 0
    reasons: List[str] = []

    # Rule: big MR
    if churn > 400:
        score += 1
        reasons.append(f"Large diff (approx churn {churn} lines).")
    if file_count > 20:
        score += 1
        reasons.append(f"Touches many files ({file_count}).")

    # Rule: high-risk paths
    risky_hits = []
    for f in files:
        lower = f.lower()
        if any(hint in lower for hint in HIGH_RISK_PATH_HINTS):
            risky_hits.append(f)

    if risky_hits:
        score += 2
        reasons.append("Touches higher-risk areas (auth/infra/config/migrations/etc).")

    # Rule: tests missing heuristic
    prod_touched = any(
        not ("test" in f.lower() or "spec" in f.lower())
        for f in files
    )
    tests_touched = any(("test" in f.lower() or "spec" in f.lower()) for f in files)
    if prod_touched and not tests_touched:
        score += 1
        reasons.append("No obvious test changes detected.")

    score = min(10, score)


    return RiskResult(
        score=score,
        level=_level(score),
        reasons=reasons if reasons else ["No major risk signals found by basic rules."],
        stats={"file_count": file_count, "approx_churn": churn, "risky_files_count": len(risky_hits)},
    )

def risk_result_to_dict(result: RiskResult) -> dict:
    return {
        "score": result.score,
        "level": result.level,
        "reasons": result.reasons,
        "stats": result.stats,
    }