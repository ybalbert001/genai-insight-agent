#!/usr/bin/env python3
"""
GenAI Repository Admission Filter

根据客观准入规则评估GitHub趋势仓库，判断是否应纳入监控池。
"""

import json
import argparse
import sys
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum


class Priority(Enum):
    """Priority levels for repository admission"""
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    REJECTED = "REJECTED"


@dataclass
class AdmissionResult:
    """Result of admission evaluation"""
    project_url: str
    collect_date: str
    priority: Priority
    matched_rules: List[str]
    reasons: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'project_url': self.project_url,
            'collect_date': self.collect_date,
            'priority': self.priority.value,
            'matched_rules': self.matched_rules,
            'reasons': self.reasons
        }


class RepoAdmissionFilter:
    """Filter for evaluating repository admission based on objective rules"""

    # Rule 1: Explosive growth thresholds
    EXPLOSIVE_STARS_THRESHOLD = 500
    EXPLOSIVE_GROWTH_RATE = 0.05  # 5%

    # Rule 2: Mature project thresholds
    MATURE_STARS_THRESHOLD = 20000
    MATURE_FORKS_THRESHOLD = 2000

    # Rule 3: Stable growth thresholds
    STABLE_STARS_MIN = 5000
    STABLE_STARS_MAX = 20000
    STABLE_INCREMENTAL_MIN = 150
    STABLE_FORKS_MIN = 500

    # Official/Infrastructure keywords
    OFFICIAL_KEYWORDS = [
        "official", "sdk", "protocol", "standard",
        "specification", "reference implementation"
    ]

    KNOWN_ORGS = [
        "openai", "anthropic", "google", "microsoft",
        "meta", "huggingface", "modelcontextprotocol",
        "langchain-ai", "qdrant", "weaviate"
    ]

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str):
        """Print log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[INFO] {message}", file=sys.stderr)

    def evaluate_repository(self, repo_data: Dict[str, Any]) -> AdmissionResult:
        """
        Evaluate a single repository against admission rules

        Args:
            repo_data: Repository data with required fields

        Returns:
            AdmissionResult with priority and matched rules
        """
        project_url = repo_data.get("project_url", "")
        collect_date = repo_data.get("collect_date", "")

        # Extract metrics
        metrics = self._extract_metrics(repo_data)

        # Apply filters first
        passed_filters, filter_reason = self._apply_filters(repo_data, metrics)

        if not passed_filters:
            return AdmissionResult(
                project_url=project_url,
                collect_date=collect_date,
                priority=Priority.REJECTED,
                matched_rules=[],
                reasons=[filter_reason]
            )

        # Evaluate rules
        matched_rules = []
        reasons = []

        rule1_match, rule1_reason = self._check_rule1_explosive_growth(metrics)
        if rule1_match:
            matched_rules.append("Rule1: Explosive Growth")
            reasons.append(rule1_reason)

        rule2_match, rule2_reason = self._check_rule2_mature_project(metrics)
        if rule2_match:
            matched_rules.append("Rule2: Mature Project")
            reasons.append(rule2_reason)

        rule3_match, rule3_reason = self._check_rule3_stable_growth(metrics)
        if rule3_match:
            matched_rules.append("Rule3: Stable Growth")
            reasons.append(rule3_reason)

        rule4_match, rule4_reason = self._check_rule4_official_infra(repo_data, metrics)
        if rule4_match:
            matched_rules.append("Rule4: Official/Infrastructure")
            reasons.append(rule4_reason)

        # Determine priority
        priority = self._determine_priority(
            rule1_match, rule2_match, rule3_match, rule4_match
        )

        self.log(f"Repository {project_url}: {priority.value}")
        self.log(f"  Matched rules: {matched_rules}")

        return AdmissionResult(
            project_url=project_url,
            collect_date=collect_date,
            priority=priority,
            matched_rules=matched_rules,
            reasons=reasons
        )

    def _extract_metrics(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize metrics from repository data"""
        cumulative_stars = int(repo_data.get("cumulative_stars", 0))
        incremental_stars = int(repo_data.get("incremental_stars", 0))
        forks = int(repo_data.get("forks", 0))

        growth_rate = 0.0
        if cumulative_stars > 0:
            growth_rate = incremental_stars / cumulative_stars

        return {
            "cumulative_stars": cumulative_stars,
            "incremental_stars": incremental_stars,
            "forks": forks,
            "growth_rate": growth_rate,
            "programming_language": repo_data.get("programming_language", ""),
            "description": repo_data.get("description", "").lower()
        }

    def _apply_filters(self, repo_data: Dict[str, Any], metrics: Dict[str, Any]) -> tuple[bool, str]:
        """
        Apply mandatory filters

        Returns:
            (passed, reason) tuple
        """
        # Filter 1: Must be AI-related
        is_ai_related = repo_data.get("is_AI_related_project", False)
        if not is_ai_related:
            return False, "Not AI-related project"

        # Filter 2: Must not be tutorial collection
        is_tutorial = repo_data.get("is_tutorial_collection", False)
        if is_tutorial:
            return False, "Tutorial collection excluded"

        # Filter 3: Must have programming language
        if not metrics["programming_language"]:
            return False, "No programming language specified"

        return True, ""

    def _check_rule1_explosive_growth(self, metrics: Dict[str, Any]) -> tuple[bool, str]:
        """
        Rule 1: Explosive growth project
        - Daily incremental stars >= 500
        - OR growth rate >= 5%
        """
        incremental = metrics["incremental_stars"]
        rate = metrics["growth_rate"]

        if incremental >= self.EXPLOSIVE_STARS_THRESHOLD:
            return True, f"爆发式增长: +{incremental} stars/日"

        if rate >= self.EXPLOSIVE_GROWTH_RATE:
            return True, f"高增长率: {rate:.1%}"

        return False, ""

    def _check_rule2_mature_project(self, metrics: Dict[str, Any]) -> tuple[bool, str]:
        """
        Rule 2: Mature project (well-known repo monitoring)
        - Cumulative stars >= 20,000
        - Forks >= 2,000
        """
        stars = metrics["cumulative_stars"]
        forks = metrics["forks"]

        if stars >= self.MATURE_STARS_THRESHOLD and forks >= self.MATURE_FORKS_THRESHOLD:
            return True, f"成熟项目: {stars:,} stars, {forks:,} forks"

        return False, ""

    def _check_rule3_stable_growth(self, metrics: Dict[str, Any]) -> tuple[bool, str]:
        """
        Rule 3: Stable growth project (potential rising star)
        - Cumulative stars: 5,000-20,000
        - Daily incremental >= 150
        - Forks >= 500
        """
        stars = metrics["cumulative_stars"]
        incremental = metrics["incremental_stars"]
        forks = metrics["forks"]

        in_star_range = self.STABLE_STARS_MIN <= stars <= self.STABLE_STARS_MAX
        has_incremental = incremental >= self.STABLE_INCREMENTAL_MIN
        has_forks = forks >= self.STABLE_FORKS_MIN

        if in_star_range and has_incremental and has_forks:
            return True, f"稳定增长: {stars:,} stars, +{incremental}/日, {forks} forks"

        return False, ""

    def _check_rule4_official_infra(self, repo_data: Dict[str, Any], metrics: Dict[str, Any]) -> tuple[bool, str]:
        """
        Rule 4: Official/Infrastructure project
        - Description contains official keywords
        - OR from known organizations
        """
        description = metrics["description"]
        project_url = repo_data.get("project_url", "").lower()

        # Check keywords in description
        for keyword in self.OFFICIAL_KEYWORDS:
            if keyword in description:
                return True, f"官方/基础设施: 含'{keyword}'关键词"

        # Check known organizations in URL
        for org in self.KNOWN_ORGS:
            if f"github.com/{org}/" in project_url:
                return True, f"知名组织: {org}"

        return False, ""

    def _determine_priority(
        self,
        rule1: bool,
        rule2: bool,
        rule3: bool,
        rule4: bool
    ) -> Priority:
        """
        Determine priority based on matched rules

        Priority logic:
        - P0: Rule1 (explosive growth) - needs immediate analysis
        - P1: Rule2 (mature) OR (Rule1 + Rule3) - key focus
        - P2: Rule3 (stable) OR Rule4 (infra) - continuous observation
        - P3: Passed filters only - monitoring pool
        """
        if rule1:
            return Priority.P0

        if rule2:
            return Priority.P1

        if rule3 or rule4:
            return Priority.P2

        return Priority.P3

    def evaluate_batch(self, repos: List[Dict[str, Any]]) -> List[AdmissionResult]:
        """
        Evaluate multiple repositories

        Args:
            repos: List of repository data

        Returns:
            List of AdmissionResult
        """
        results = []
        for repo in repos:
            result = self.evaluate_repository(repo)
            results.append(result)
        return results


def main():
    parser = argparse.ArgumentParser(
        description="评估GitHub趋势仓库的准入规则"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="输入JSON文件路径 (默认: stdin)"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出JSON文件路径 (默认: stdout)"
    )
    parser.add_argument(
        "-p", "--priority",
        choices=["P0", "P1", "P2", "P3"],
        action="append",
        help="按优先级过滤 (可多次指定)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出模式"
    )

    args = parser.parse_args()

    # Read input
    if args.input == "-":
        input_data = json.load(sys.stdin)
    else:
        with open(args.input, 'r') as f:
            input_data = json.load(f)

    # Handle both single repo and list of repos
    if isinstance(input_data, dict):
        repos = [input_data]
    else:
        repos = input_data

    # Evaluate repositories
    filter_obj = RepoAdmissionFilter(verbose=args.verbose)
    results = filter_obj.evaluate_batch(repos)

    # Filter by priority if specified
    if args.priority:
        priority_filter = [Priority[p] for p in args.priority]
        results = [r for r in results if r.priority in priority_filter]

    # Generate output
    output = [r.to_dict() for r in results]
    output_json = json.dumps(output, indent=2, ensure_ascii=False)

    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
