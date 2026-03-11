#!/usr/bin/env python3
"""
SeaForge Git Manager
====================

Handles GitHub workflow for SeaForge:
- Branch creation from main (not orphan)
- Cherry-pick from previous iterations
- Commit, push, PR creation
"""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class SeaForgeGitManager:
    """Manages git operations for SeaForge workflow."""

    def __init__(self, repo_path: str, task_code: str, remote: str = "origin"):
        self.repo_path = Path(repo_path).resolve()
        self.task_code = task_code.upper()
        self.remote = remote
        self.main_branch = "main"

    def _run_git(self, args: List[str], check: bool = True) -> tuple[int, str, str]:
        """Execute git command and return (exit_code, stdout, stderr)."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            if check and result.returncode != 0:
                print(f"Git error: {result.stderr}")
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            print(f"Git execution error: {e}")
            return 1, "", str(e)

    def ensure_main_branch(self) -> bool:
        """Ensure main branch exists, create if not."""
        ret, _, _ = self._run_git(["rev-parse", "--verify", self.main_branch], check=False)
        if ret != 0:
            print("Creating main branch...")
            self._run_git(["checkout", "--orphan", self.main_branch], check=False)
            self._run_git(["commit", "--allow-empty", "-m", "init: main branch"])
            self._run_git(["push", self.remote, self.main_branch])
            return True
        return True

    def get_branch_name(self, task_id: int, date: Optional[str] = None) -> str:
        """Generate branch name following SeaForge convention."""
        if date is None:
            date = datetime.now().strftime("%d/%m/%y")
        return f"{self.task_code}-{task_id:03d}-{date}"

    def find_previous_branch(self, current_task_id: int) -> Optional[str]:
        """Find the most recent branch before current_task_id."""
        ret, stdout, _ = self._run_git(
            ["ls-remote", "--heads", self.remote], check=False
        )
        if ret != 0:
            return None

        pattern = rf"refs/heads/{self.task_code}-(\d{{3}})-"
        branches = []

        for line in stdout.split("\n"):
            match = re.search(pattern, line)
            if match:
                branch_id = int(match.group(1))
                if branch_id < current_task_id:
                    branch_name = line.split("refs/heads/")[-1].strip()
                    branches.append((branch_id, branch_name))

        if branches:
            branches.sort(reverse=True)
            return branches[0][1]
        return None

    def create_branch(self, task_id: int, date: Optional[str] = None) -> str:
        """Create new branch from main."""
        self.ensure_main_branch()
        branch_name = self.get_branch_name(task_id, date)

        # Checkout main first
        self._run_git(["checkout", self.main_branch])
        # Fetch latest
        self._run_git(["fetch", self.remote, self.main_branch])
        # Create branch from main
        self._run_git(["checkout", "-b", branch_name])

        print(f"Created branch: {branch_name}")
        return branch_name

    def cherry_pick_from_branch(self, source_branch: str) -> Dict[str, Any]:
        """Cherry-pick commits from source branch."""
        # Fetch source branch
        self._run_git(["fetch", self.remote, source_branch])

        # Get commits from source branch
        ret, stdout, _ = self._run_git([
            "log", f"{self.remote}/{source_branch}", 
            "--pretty=format:%H", "--reverse"
        ], check=False)

        if ret != 0 or not stdout.strip():
            return {"success": False, "message": "No commits to cherry-pick", "commits": []}

        commits = [c.strip() for c in stdout.split("\n") if c.strip()]
        picked = []

        for commit in commits:
            ret, _, stderr = self._run_git([
                "cherry-pick", commit, "--no-commit"
            ], check=False)

            if ret != 0:
                # Resolve conflict by taking their changes
                self._run_git(["checkout", "--theirs", "."], check=False)
                self._run_git(["add", "-A"], check=False)
                self._run_git([
                    "commit", "-m", f"cherry-pick: {commit[:8]} (resolved)" 
                ], check=False)
            else:
                # Commit picked changes
                self._run_git(["commit", "-m", f"cherry-pick: {commit[:8]}"], check=False)

            picked.append(commit[:8])

        return {
            "success": True,
            "commits": picked,
            "count": len(picked)
        }

    def commit_changes(self, task_id: int, message: str, phase: str = "dev") -> str:
        """Commit changes with semantic message."""
        self._run_git(["add", "-A"])
        commit_msg = f"{phase}({self.task_code}-{task_id:03d}): {message}"
        self._run_git(["commit", "-m", commit_msg])

        # Get commit hash
        _, stdout, _ = self._run_git(["rev-parse", "HEAD"])
        return stdout.strip()

    def push_branch(self, branch_name: str) -> bool:
        """Push branch to remote."""
        ret, _, _ = self._run_git(["push", self.remote, branch_name])
        return ret == 0

    def create_pull_request(self, repo_url: str, branch_name: str, title: str, 
                          pat: str) -> Optional[str]:
        """Create PR using GitHub API (Development only, task_id >= 100)."""
        import requests

        # Extract owner/repo from URL
        parts = repo_url.replace("https://github.com/", "").replace(".git", "").split("/")
        if len(parts) < 2:
            return None

        owner, repo = parts[0], parts[1]
        pr_data = {
            "title": title,
            "head": branch_name,
            "base": self.main_branch,
            "body": f"\nSeaForge development iteration\nBranch: {branch_name}"
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


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python git_manager.py <repo_path> <task_code> [task_id]")
        sys.exit(1)

    manager = SeaForgeGitManager(sys.argv[1], sys.argv[2])

    if len(sys.argv) > 3:
        task_id = int(sys.argv[3])
        branch = manager.create_branch(task_id)
        print(f"Created: {branch}")
