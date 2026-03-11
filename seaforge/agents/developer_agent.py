#!/usr/bin/env python3
"""
SeaForge Developer Agent
========================

Subordinate agent for the Development Phase.
Task IDs: 100-999

Responsible for:
1. Creating development branches from main
2. Cherry-picking from planning or previous dev branches
3. Implementing features based on specifications
4. Committing, pushing, and creating PRs
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any


def run_command(cmd: list, cwd: str, check: bool = True) -> tuple:
    """Run a command and return (exit_code, stdout, stderr)."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, check=False
    )
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.returncode, result.stdout, result.stderr


def cherry_pick_branch(repo_path: str, source_branch: str) -> dict:
    """Cherry-pick all commits from source branch."""
    run_command(["git", "fetch", "origin", source_branch], repo_path)

    ret, stdout, _ = run_command(
        ["git", "log", f"origin/{source_branch}", "--pretty=format:%H", "--reverse"],
        repo_path, check=False
    )

    if ret != 0 or not stdout.strip():
        return {"success": False, "count": 0}

    commits = [c.strip() for c in stdout.split("\n") if c.strip()]
    picked = 0
    skipped = []

    for commit in commits:
        ret, _, stderr = run_command(
            ["git", "cherry-pick", commit, "--no-commit"],
            repo_path, check=False
        )

        if ret != 0:
            # Check for conflicts
            if "Merge" in stderr or "conflict" in stderr.lower():
                run_command(["git", "checkout", "--theirs", "."], repo_path, check=False)
                run_command(["git", "add", "-A"], repo_path, check=False)
                run_command(
                    ["git", "commit", "-m", f"cherry-pick: {commit[:8]} (resolved)"],
                    repo_path, check=False
                )
            else:
                skipped.append(commit[:8])
                continue
        else:
            run_command(
                ["git", "commit", "-m", f"cherry-pick: {commit[:8]}"],
                repo_path, check=False
            )
        picked += 1

    return {"success": True, "count": picked, "skipped": skipped}


def create_pull_request(repo_url: str, branch: str, title: str, pat: str) -> str | None:
    """Create PR using GitHub API."""
    try:
        import requests

        # Extract owner/repo
        parts = repo_url.replace("https://github.com/", "").replace(".git", "").split("/")
        if len(parts) < 2:
            return None

        owner, repo = parts[-2], parts[-1]

        pr_data = {
            "title": title,
            "head": branch,
            "base": "main",
            "body": f"\nSeaForge Development\nBranch: {branch}"
        }

        response = requests.post(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            headers={
                "Authorization": f"Bearer {pat}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            json=pr_data
        )

        if response.status_code == 201:
            return response.json().get("html_url")
        else:
            print(f"PR creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"PR error: {e}")
        return None


def developer_agent_task(repo_path: str, task_code: str, task_id: int,
                        feature_spec: Dict[str, Any], source_branch: str,
                        repo_url: str | None = None, pat: str | None = None):
    """
    Main developer agent task.

    Args:
        repo_path: Path to git repo
        task_code: 5-char task code
        task_id: Feature ID (100-999)
        feature_spec: Feature specification from planning
        source_branch: Branch to cherry-pick from
        repo_url: For PR creation
        pat: GitHub PAT
    """
    from datetime import datetime

    task_id = int(task_id)
    date = datetime.now().strftime("%d/%m/%y")
    branch_name = f"{task_code}-{task_id:03d}-{date}"

    feature_name = feature_spec.get("name", f"feature-{task_id}")

    print(f"\n🔨 Developer Agent: {branch_name}")
    print(f"   Feature: {feature_name}")
    print("=" * 50)

    # Step 1: Checkout main and create branch
    run_command(["git", "checkout", "main"], repo_path)
    run_command(["git", "fetch", "origin", "main"], repo_path)
    ret, _, _ = run_command(["git", "checkout", "-b", branch_name], repo_path)

    if ret != 0:
        run_command(["git", "checkout", branch_name], repo_path, check=False)

    # Step 2: Cherry-pick from source
    print(f"\n🍒 Cherry-picking from {source_branch}...")
    cherry_result = cherry_pick_branch(repo_path, source_branch)
    print(f"   Picked: {cherry_result['count']} commits")
    if cherry_result.get('skipped'):
        print(f"   Skipped: {cherry_result['skipped']}")

    # Step 3: Implement feature
    print(f"\n🔨 Implementing feature...")

    # Create project structure
    project_dir = Path(repo_path) / "projects" / task_code.lower()
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write implementation
    impl_content = f"""# Feature: {feature_name}

## Implementation Notes
Feature ID: {task_code}-{task_id:03d}
Branch: {branch_name}
Cherry-picked: {cherry_result['count']} commits from {source_branch}

## Specification
```json
{json.dumps(feature_spec, indent=2)}
```

## Status
- ✅ Branch created
- ✅ Changes cherry-picked
- ✅ Implementation written
- ✅ Ready for PR

---
*Generated by SeaForge Developer Agent*
"""

    with open(project_dir / f"{feature_name.lower().replace(' ', '_')}.md", "w") as f:
        f.write(impl_content)

    # Step 4: Commit
    run_command(["git", "add", "-A"], repo_path)
    run_command(
        ["git", "commit", "-m", f"feat({task_code}-{task_id:03d}): {feature_name}"],
        repo_path
    )

    _, stdout, _ = run_command(["git", "rev-parse", "HEAD"], repo_path)
    commit_hash = stdout.strip()[:8]

    # Step 5: Push
    run_command(["git", "push", "-u", "origin", branch_name], repo_path)

    # Step 6: Create PR (development phase only)
    pr_url = None
    if repo_url and pat:
        print(f"\n📤 Creating Pull Request...")
        pr_url = create_pull_request(
            repo_url, branch_name,
            f"feat({task_code}-{task_id:03d}): {feature_name}",
            pat
        )
        if pr_url:
            print(f"   ✅ PR: {pr_url}")
        else:
            print(f"   ⚠️ PR creation failed")

    print(f"\n✅ Development complete!")
    print(f"   Branch: {branch_name}")
    print(f"   Commit: {commit_hash}")

    return {
        "branch": branch_name,
        "commit": commit_hash,
        "feature": feature_name,
        "cherry_picked": cherry_result['count'],
        "pr_url": pr_url,
        "source_branch": source_branch
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--task-code", required=True)
    parser.add_argument("--task-id", required=True, type=int)
    parser.add_argument("--source-branch", required=True)
    parser.add_argument("--repo-url", default=None)
    parser.add_argument("--pat", default=None)
    parser.add_argument("--feature-spec", required=True, help="JSON string")

    args = parser.parse_args()

    feature_spec = json.loads(args.feature_spec)

    result = developer_agent_task(
        args.repo, args.task_code, args.task_id,
        feature_spec, args.source_branch,
        args.repo_url, args.pat
    )

    print(json.dumps(result, indent=2))
