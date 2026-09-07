#!/usr/bin/env python3
"""Scan cy123676/octo-server-product-board and record exam cron evidence.

No external group delivery is performed until exam group id and proctor are configured.
The script reads the GitHub token from the workspace secret file and never prints it.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

OWNER = "cy123676"
REPO = "octo-server-product-board"
API = "https://api.github.com"
WORKSPACE = Path(__file__).resolve().parents[2]
BOARD = Path(__file__).resolve().parents[1]
TOKEN_FILE = WORKSPACE / ".secrets" / "github-octo-board-token"
RUNTIME = BOARD / "runtime"
RUNS = RUNTIME / "scan_runs"
PENDING = RUNTIME / "pending_broadcasts"
STATE_FILE = RUNTIME / "scan_state.json"
DELIVERY_FILE = RUNTIME / "delivery_config.json"


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(ts: dt.datetime) -> str:
    return ts.isoformat().replace("+00:00", "Z")


def read_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    raise RuntimeError("GitHub token not configured")


def gh_json(method: str, url: str, token: str, data: dict | None = None):
    body = None
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "octo-server-product-manager-scan",
        "Authorization": f"Bearer {token}",
    }
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            if not raw:
                return None
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"GitHub API {method} {url} failed HTTP {e.code}: {msg}") from None


def gh_get_all_issues(token: str):
    issues = []
    page = 1
    while True:
        url = f"{API}/repos/{OWNER}/{REPO}/issues?state=all&per_page=100&page={page}"
        batch = gh_json("GET", url, token)
        if not batch:
            break
        for item in batch:
            if "pull_request" not in item:
                issues.append(item)
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.2)
    return issues


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def normalize_issue(issue: dict) -> dict:
    return {
        "number": issue["number"],
        "title": issue.get("title", ""),
        "state": issue.get("state", ""),
        "labels": sorted([l.get("name", "") for l in issue.get("labels", []) if l.get("name")]),
        "updated_at": issue.get("updated_at", ""),
        "comments": issue.get("comments", 0),
        "html_url": issue.get("html_url", ""),
    }


def diff_issues(previous: dict, current: dict) -> list[dict]:
    prev_issues = previous.get("issues", {}) if isinstance(previous, dict) else {}
    changes = []
    for num, cur in sorted(current.items(), key=lambda kv: int(kv[0])):
        old = prev_issues.get(num)
        if old is None:
            changes.append({"type": "new_issue", "issue": cur})
            continue
        fields = []
        for key in ["title", "state", "labels", "comments", "updated_at"]:
            if old.get(key) != cur.get(key):
                fields.append({"field": key, "old": old.get(key), "new": cur.get(key)})
        if fields:
            changes.append({"type": "issue_changed", "issue": cur, "fields": fields})
    for num, old in sorted(prev_issues.items(), key=lambda kv: int(kv[0])):
        if num not in current:
            changes.append({"type": "issue_missing_from_api", "issue": old})
    return changes


def delivery_config() -> dict:
    default = {
        "enabled": False,
        "reason": "exam group id and proctor are not confirmed yet",
        "target": "",
        "proctor_mention": "",
    }
    cfg = load_json(DELIVERY_FILE, default)
    if not isinstance(cfg, dict):
        return default
    return {**default, **cfg}


def make_broadcast(run: dict, changes: list[dict], cfg: dict) -> str:
    lines = []
    lines.append("# 待发送考试群播报草稿")
    lines.append("")
    lines.append(f"- run_id: `{run['run_id']}`")
    lines.append(f"- repo: `{OWNER}/{REPO}`")
    lines.append(f"- mode: `{run['mode']}`")
    lines.append(f"- delivery_enabled: `{cfg.get('enabled', False)}`")
    lines.append("")
    lines.append("## 变化摘要")
    if not changes:
        lines.append("无变化。按考试规则：不外发无更新消息。")
    for ch in changes:
        issue = ch["issue"]
        lines.append(f"- {ch['type']}: #{issue['number']} {issue['title']} ({issue['html_url']})")
        for f in ch.get("fields", []):
            if f["field"] == "updated_at":
                continue
            lines.append(f"  - {f['field']}: `{f['old']}` → `{f['new']}`")
    lines.append("")
    lines.append("## 外发状态")
    if cfg.get("enabled"):
        lines.append("已配置外发目标；实际发送仍需 Agent 在考试群上下文中确认 @ 主考格式。")
    else:
        lines.append("未外发：考试群号和主考人尚未确认，避免发错群或漏 @ 主考。")
    return "\n".join(lines) + "\n"


def put_files_one_commit(token: str, branch: str, files: list[Path], message: str) -> str:
    ref_url = f"{API}/repos/{OWNER}/{REPO}/git/ref/heads/{branch}"
    ref = gh_json("GET", ref_url, token)
    base_sha = ref["object"]["sha"]
    base_commit = gh_json("GET", f"{API}/repos/{OWNER}/{REPO}/git/commits/{base_sha}", token)
    base_tree = base_commit["tree"]["sha"]
    tree_items = []
    for path in files:
        rel = path.relative_to(BOARD).as_posix()
        content = path.read_text(encoding="utf-8")
        blob = gh_json("POST", f"{API}/repos/{OWNER}/{REPO}/git/blobs", token, {
            "content": content,
            "encoding": "utf-8",
        })
        tree_items.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    tree = gh_json("POST", f"{API}/repos/{OWNER}/{REPO}/git/trees", token, {
        "base_tree": base_tree,
        "tree": tree_items,
    })
    commit = gh_json("POST", f"{API}/repos/{OWNER}/{REPO}/git/commits", token, {
        "message": message,
        "tree": tree["sha"],
        "parents": [base_sha],
    })
    gh_json("PATCH", f"{API}/repos/{OWNER}/{REPO}/git/refs/heads/{branch}", token, {"sha": commit["sha"], "force": False})
    return commit["sha"]


def main() -> int:
    started = now_utc()
    run_id = started.strftime("%Y%m%dT%H%M%SZ")
    RUNS.mkdir(parents=True, exist_ok=True)
    PENDING.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)

    token = read_token()
    previous = load_json(STATE_FILE, {"issues": {}})
    issues = gh_get_all_issues(token)
    current = {str(i["number"]): normalize_issue(i) for i in issues}
    changes = diff_issues(previous, current)
    cfg = delivery_config()

    run = {
        "run_id": run_id,
        "started_at": iso(started),
        "finished_at": iso(now_utc()),
        "repo": f"{OWNER}/{REPO}",
        "mode": "scan_only_no_external_delivery" if not cfg.get("enabled") else "scan_with_delivery_config_present",
        "delivery": cfg,
        "issue_count": len(current),
        "change_count": len(changes),
        "changes": changes,
    }
    run_file = RUNS / f"{run_id}.json"
    run_file.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    index_file = RUNS / "index.jsonl"
    with index_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps({k: run[k] for k in ["run_id", "started_at", "finished_at", "repo", "mode", "issue_count", "change_count"]}, ensure_ascii=False) + "\n")

    state = {
        "repo": f"{OWNER}/{REPO}",
        "last_scan_at": run["finished_at"],
        "last_run_id": run_id,
        "last_change_count": len(changes),
        "issues": current,
    }
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    files_to_push = [run_file, index_file, STATE_FILE]
    if changes:
        pending = PENDING / f"{run_id}.md"
        pending.write_text(make_broadcast(run, changes, cfg), encoding="utf-8")
        files_to_push.append(pending)

    commit_sha = put_files_one_commit(token, "main", files_to_push, f"chore: record product board scan {run_id}")
    print(json.dumps({
        "ok": True,
        "run_id": run_id,
        "issue_count": len(current),
        "change_count": len(changes),
        "pushed_commit": commit_sha,
        "external_delivery": bool(cfg.get("enabled")),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1)
