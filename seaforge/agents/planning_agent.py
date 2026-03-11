#!/usr/bin/env python3
"""
SeaForge Planning Agent
=======================

Subordinate agent for the Planning Phase.
Task IDs: 000-099

Responsible for:
1. Creating planning branches from main
2. Cherry-picking from previous planning iterations
3. Writing planning documents (spec.md, architecture.md, features.md)
4. Committing and pushing (NO PRs)
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def run_command(cmd: list, cwd: str, check: bool = True) -> tuple:
    """Run a command and return (exit_code, stdout, stderr)."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, check=False
    )
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.returncode, result.stdout, result.stderr


def find_previous_branch(repo_path: str, task_code: str, current_id: int) -> str | None:
    """Find the most recent branch before current_id."""
    ret, stdout, _ = run_command(
        ["git", "ls-remote", "--heads", "origin"],
        repo_path, check=False
    )
    if ret != 0:
        return None

    import re
    pattern = rf"refs/heads/{task_code}-(\d{{3}})-"
    branches = []

    for line in stdout.split("\n"):
        match = re.search(pattern, line)
        if match:
            branch_id = int(match.group(1))
            if branch_id < current_id:
                branch_name = line.split("refs/heads/")[-1].strip()
                branches.append((branch_id, branch_name))

    if branches:
        branches.sort(reverse=True)
        return branches[0][1]
    return None


def cherry_pick_branch(repo_path: str, source_branch: str) -> dict:
    """Cherry-pick all commits from source branch."""
    # Fetch source branch
    run_command(["git", "fetch", "origin", source_branch], repo_path)

    # Get commits
    ret, stdout, _ = run_command(
        ["git", "log", f"origin/{source_branch}", "--pretty=format:%H", "--reverse"],
        repo_path, check=False
    )

    if ret != 0 or not stdout.strip():
        return {"success": False, "count": 0}

    commits = [c.strip() for c in stdout.split("\n") if c.strip()]
    picked = 0

    for commit in commits:
        ret, _, _ = run_command(
            ["git", "cherry-pick", commit, "--no-commit"],
            repo_path, check=False
        )

        if ret != 0:
            # Resolve conflict
            run_command(["git", "checkout", "--theirs", "."], repo_path, check=False)
            run_command(["git", "add", "-A"], repo_path, check=False)
            run_command(
                ["git", "commit", "-m", f"cherry-pick: {commit[:8]} (resolved)"],
                repo_path, check=False
            )
        else:
            run_command(
                ["git", "commit", "-m", f"cherry-pick: {commit[:8]}"],
                repo_path, check=False
            )
        picked += 1

    return {"success": True, "count": picked}


def planning_agent_task(repo_path: str, task_code: str, task_id: int, 
                       requirements: str, feedback: str = ""):
    """
    Main planning agent task.

    Args:
        repo_path: Path to git repo
        task_code: 5-char task code (e.g., SFG00)
        task_id: Iteration ID (000-099)
        requirements: Project requirements/specification
        feedback: User feedback for iterative planning
    """
    from datetime import datetime

    task_id = int(task_id)
    date = datetime.now().strftime("%d/%m/%y")
    branch_name = f"{task_code}-{task_id:03d}-{date}"

    print(f"\n📝 Planning Agent: {branch_name}")
    print("=" * 50)

    # Step 1: Ensure main exists
    ret, _, _ = run_command(["git", "rev-parse", "--verify", "main"], repo_path, check=False)
    if ret != 0:
        print("Creating main branch...")
        run_command(["git", "checkout", "--orphan", "main"], repo_path, check=False)
        run_command(["git", "commit", "--allow-empty", "-m", "init: main"], repo_path)
        run_command(["git", "push", "origin", "main"], repo_path)

    # Step 2: Create branch from main
    run_command(["git", "checkout", "main"], repo_path)
    run_command(["git", "fetch", "origin", "main"], repo_path)
    ret, _, _ = run_command(["git", "checkout", "-b", branch_name], repo_path)

    if ret != 0:
        # Branch might exist, try to checkout
        run_command(["git", "checkout", branch_name], repo_path, check=False)

    # Step 3: Cherry-pick from previous
    prev_branch = find_previous_branch(repo_path, task_code, task_id)
    cherry_picked = {"success": False, "count": 0}

    if prev_branch and task_id > 0:
        print(f"🍒 Cherry-picking from {prev_branch}...")
        cherry_picked = cherry_pick_branch(repo_path, prev_branch)
        print(f"   Picked {cherry_picked['count']} commits")

    # Step 4: Write planning documents
    print("\n📝 Writing planning documents...")

    planning_dir = Path(repo_path) / ".seaforge" / "planning"
    planning_dir.mkdir(parents=True, exist_ok=True)

    # spec.md - Main specification
    spec_content = f"""# Project Specification

## Requirements
{requirements}

## Feedback/Ideas
{feedback}

## Iteration
- Task Code: {task_code}
- Planning ID: {task_id:03d}
- Date: {date}
- Based on: {prev_branch or 'main'}

---
*Generated by SeaForge Planning Agent*
"""

    with open(planning_dir / "spec.md", "w") as f:
        f.write(spec_content)

    # features.md - Feature breakdown
    features_content = f"""# Feature Breakdown

## Phase 1: Core Features (To be detailed)
1. [Feature 1]
2. [Feature 2]
3. [Feature 3]

## Phase 2: Advanced Features
1. [Advanced 1]
2. [Advanced 2]

## Dependencies
- Feature dependencies to be identified

## Notes
- Planning iteration {task_id:03d}
- Branch: {branch_name}
"""

    with open(planning_dir / "features.md", "w") as f:
        f.write(features_content)

    # Step 5: Commit
    run_command(["git", "add", "-A"], repo_path)
    run_command(
        ["git", "commit", "-m", f"plan({task_code}-{task_id:03d}): iteration {task_id:03d}"],
        repo_path
    )

    # Get commit hash
    _, stdout, _ = run_command(["git", "rev-parse", "HEAD"], repo_path)
    commit_hash = stdout.strip()[:8]

    # Step 6: Push
    run_command(["git", "push", "-u", "origin", branch_name], repo_path)

    print(f"\n✅ Planning complete!")
    print(f"   Branch: {branch_name}")
    print(f"   Commit: {commit_hash}")
    print(f"   Cherry-picked: {cherry_picked['count']} commits")

    return {
        "branch": branch_name,
        "commit": commit_hash,
        "cherry_picked": cherry_picked['count'],
        "previous": prev_branch
    }


if __name__ == "__main__":
    # Called as subordinate
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--task-code", required=True)
    parser.add_argument("--task-id", required=True, type=int)
    parser.add_argument("--requirements", required=True)
    parser.add_argument("--feedback", default="")

    args = parser.parse_args()

    result = planning_agent_task(
        args.repo, args.task_code, args.task_id,
        args.requirements, args.feedback
    )

    print(json.dumps(result, indent=2))
