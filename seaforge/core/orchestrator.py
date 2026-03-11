#!/usr/bin/env python3
"""
SeaForge Orchestrator
=====================

Main orchestration logic for SeaForge platform.
Manages planning and development phases via subordinate delegation.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.git_manager import SeaForgeGitManager


class SeaForgeOrchestrator:
    """
    Main orchestrator for SeaForge development workflow.

    Workflows:
    1. Planning Phase (000-099): No PRs, iterative with user
    2. Development Phase (100-999): With PRs, feature-by-feature
    """

    PLANNING_MAX = 99
    DEV_MIN = 100
    DEV_MAX = 999

    def __init__(self, repo_path: str, task_code: str = "SFG00", 
                 pat: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.task_code = task_code
        self.pat = pat
        self.git = SeaForgeGitManager(repo_path, task_code)

        # Load or create features tracking
        self.features_file = self.repo_path / ".seaforge" / "features.json"
        self.iterations = {}
        self.current_phase = "not_started"

    def load_features(self) -> Dict[str, Any]:
        """Load features data from JSON."""
        if self.features_file.exists():
            with open(self.features_file) as f:
                return json.load(f)
        return {"features": [], "iterations": {}, "metadata": {}}

    def save_features(self, data: Dict[str, Any]):
        """Save features data to JSON."""
        self.features_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.features_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_current_date(self) -> str:
        return datetime.now().strftime("%d/%m/%y")

    def start_planning_phase(self, initial_requirements: str) -> str:
        """
        Start planning phase (000-099).
        Creates initial planning branch and delegates to planning subordinate.
        """
        print("\n🌊 SeaForge: Starting Planning Phase")
        print("=" * 50)

        # Ensure main exists
        self.git.ensure_main_branch()

        # Create planning-000 branch
        task_id = 0
        branch = self.git.create_branch(task_id)

        print(f"\n📋 Initial Planning: {branch}")
        print(f"Requirements: {initial_requirements[:100]}...")

        # Return branch info for subordinate to use
        ctx = {
            "phase": "planning",
            "task_id": task_id,
            "task_code": self.task_code,
            "branch": branch,
            "requirements": initial_requirements
        }

        return json.dumps(ctx, indent=2)

    def continue_planning(self, task_id: int, feedback: str) -> str:
        """
        Continue planning with user feedback.
        Creates new planning branch (if task_id > previous).
        """
        prev_id = task_id - 1

        # Find previous branch to cherry-pick from
        prev_branch = self.git.find_previous_branch(task_id)

        # Create new planning branch
        branch = self.git.create_branch(task_id)

        if prev_branch and prev_id >= 0:
            print(f"\n🍒 Cherry-picking from {prev_branch}...")
            result = self.git.cherry_pick_from_branch(prev_branch)
            print(f"   Picked {result.get('count', 0)} commits")

        ctx = {
            "phase": "planning",
            "task_id": task_id,
            "task_code": self.task_code,
            "branch": branch,
            "feedback": feedback,
            "previous_branch": prev_branch
        }

        return json.dumps(ctx, indent=2)

    def start_development_phase(self, features: List[Dict[str, Any]], 
                               latest_planning_branch: str) -> str:
        """
        Start development phase (100-999).
        Takes finalized plan and breaks into features to implement.
        """
        print("\n🔧 SeaForge: Starting Development Phase")
        print("=" * 50)

        dev_features = []
        for i, feature in enumerate(features, start=self.DEV_MIN):
            feature["id"] = i
            dev_features.append(feature)

        # Save features
        data = self.load_features()
        data["features"] = dev_features
        data["metadata"] = {
            "current_phase": "development",
            "latest_planning_branch": latest_planning_branch,
            "total_features": len(dev_features)
        }
        self.save_features(data)

        return json.dumps({
            "phase": "development",
            "task_code": self.task_code,
            "feature_count": len(dev_features),
            "features": dev_features,
            "source_planning": latest_planning_branch
        }, indent=2)

    def implement_feature(self, feature_id: int, latest_dev_branch: Optional[str] = None):
        """
        Implement a single development feature.
        Creates branch, cherry-picks, delegates to dev subordinate.
        """
        data = self.load_features()
        feature = next((f for f in data["features"] if f["id"] == feature_id), None)

        if not feature:
            raise ValueError(f"Feature {feature_id} not found")

        # Create dev branch
        branch = self.git.create_branch(feature_id)

        # Cherry-pick from latest branch (planning or previous dev)
        source_branch = latest_dev_branch or data["metadata"].get("latest_planning_branch")
        if source_branch:
            print(f"\n🍒 Cherry-picking from {source_branch}...")
            result = self.git.cherry_pick_from_branch(source_branch)
            print(f"   Picked {result.get('count', 0)} commits")

        ctx = {
            "phase": "development",
            "feature": feature,
            "task_code": self.task_code,
            "branch": branch
        }

        return json.dumps(ctx, indent=2)

    def report_progress(self) -> str:
        """Generate progress report for dashboard."""
        data = self.load_features()
        features = data.get("features", [])

        if not features:
            return json.dumps({
                "status": "planning",
                "completed": 0,
                "total": 0,
                "percentage": 0
            })

        completed = sum(1 for f in features if f.get("passes", False))
        total = len(features)
        percentage = (completed / total * 100) if total > 0 else 0

        return json.dumps({
            "status": data["metadata"].get("current_phase", "unknown"),
            "completed": completed,
            "total": total,
            "percentage": round(percentage, 2),
            "features": features
        }, indent=2)


if __name__ == "__main__":
    # Simple CLI usage
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <repo_path> [task_code]")
        sys.exit(1)

    orch = SeaForgeOrchestrator(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "SFG00")
    print(orch.report_progress())
