#!/usr/bin/env python3
"""
Data Analyzer Module
Handles data retrieval and analysis from DynamoDB
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta


class DataAnalyzer:
    """Analyzer for GenAI repo data from DynamoDB"""

    def __init__(self, dynamodb_script_path, region="us-east-1"):
        """
        Initialize the analyzer

        Args:
            dynamodb_script_path: Path to dynamodb_manager.py script
            region: AWS region for DynamoDB
        """
        self.script_path = Path(dynamodb_script_path)
        self.region = region

    def run_dynamodb_command(self, table, command, *args, json_output=True):
        """
        Execute DynamoDB command

        Args:
            table: Table name
            command: Command to execute (get, query, scan, etc.)
            *args: Additional command arguments
            json_output: Whether to parse JSON output

        Returns:
            Parsed data or None on error
        """
        cmd = [
            "python3", str(self.script_path),
            "--table", table,
            "--region", self.region,
            command
        ]
        cmd.extend(args)
        if json_output:
            cmd.append("--json")

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {' '.join(cmd)}", file=sys.stderr)
            print(f"Error: {result.stderr}", file=sys.stderr)
            return None

        if json_output:
            output = result.stdout.strip()
            lines = output.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('[') or line.strip().startswith('{'):
                    json_str = '\n'.join(lines[i:])
                    return json.loads(json_str)
        return result.stdout

    def get_human_p0_repos(self):
        """
        Get list of Human-P0 priority repos

        Returns:
            List of repo URLs
        """
        print("Fetching Human-P0 repos...")
        data = self.run_dynamodb_command("genai-repo-watchlist", "scan")
        if not data:
            return []

        repos = [
            item['project_url']
            for item in data
            if item.get('priority', '').lower() == 'human-p0'
        ]
        print(f"Found {len(repos)} Human-P0 repos")
        return repos

    def query_repo_data(self, repo_url, start_date, end_date=None):
        """
        Query repo data for a date range

        Args:
            repo_url: Repository URL
            start_date: Start date (datetime.date)
            end_date: End date (datetime.date), optional

        Returns:
            List of data records
        """
        args = [repo_url, "--start", start_date.strftime("%Y-%m-%d")]
        if end_date:
            args.extend(["--end", end_date.strftime("%Y-%m-%d")])

        return self.run_dynamodb_command("github-insight-raw-data", "query", *args)

    def calculate_daily_increments(self, data_list):
        """
        Calculate daily increment metrics

        Computes day-over-day changes in:
        - Total PRs (open + merged)
        - Merged PRs
        - Total Issues (open + closed)

        Also includes cumulative star count for trend visualization.

        Args:
            data_list: List of data records

        Returns:
            List of increment records with date, pr_increment, merged_pr_increment,
            issue_increment, star_count
        """
        data_list.sort(key=lambda x: x['collect_date'])
        increments = []

        for i in range(1, len(data_list)):
            prev = data_list[i-1]
            curr = data_list[i]

            prev_metrics = prev.get('metric_info', {})
            curr_metrics = curr.get('metric_info', {})

            # Calculate total PR increment
            prev_total_pr = int(prev_metrics.get('open_pr_count', '0')) + int(prev_metrics.get('merged_pr_count', '0'))
            curr_total_pr = int(curr_metrics.get('open_pr_count', '0')) + int(curr_metrics.get('merged_pr_count', '0'))
            pr_increment = curr_total_pr - prev_total_pr

            # Calculate merged PR increment
            prev_merged = int(prev_metrics.get('merged_pr_count', '0'))
            curr_merged = int(curr_metrics.get('merged_pr_count', '0'))
            merged_pr_increment = curr_merged - prev_merged

            # Calculate total issue increment
            prev_total_issue = int(prev_metrics.get('open_issue_count', '0')) + int(prev_metrics.get('closed_issue_count', '0'))
            curr_total_issue = int(curr_metrics.get('open_issue_count', '0')) + int(curr_metrics.get('closed_issue_count', '0'))
            issue_increment = curr_total_issue - prev_total_issue

            # Get current star count
            curr_stars = int(curr_metrics.get('stars', '0'))

            # Filter out days with no activity (data anomalies)
            if pr_increment > 0 or merged_pr_increment > 0 or issue_increment > 0:
                increments.append({
                    'date': curr['collect_date'],
                    'pr_increment': max(0, pr_increment),
                    'merged_pr_increment': max(0, merged_pr_increment),
                    'issue_increment': max(0, issue_increment),
                    'star_count': curr_stars
                })

        return increments

    def filter_outliers(self, increments, metric_key='pr_increment', threshold=3.0):
        """
        Filter out outlier data points

        Removes data points where value exceeds mean + threshold*std

        Args:
            increments: List of increment records
            metric_key: Metric to check for outliers
            threshold: Number of standard deviations for outlier detection

        Returns:
            Filtered list of increments
        """
        if not increments:
            return increments

        values = [inc[metric_key] for inc in increments]
        mean = sum(values) / len(values)

        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = variance ** 0.5

        # Filter outliers
        filtered = [
            inc for inc in increments
            if inc[metric_key] <= mean + threshold * std
        ]

        return filtered

    def extract_important_features(self, latest_data):
        """
        Extract important Feature updates

        Filters PRs with type=Feat and importance=High

        Args:
            latest_data: Latest day's data record

        Returns:
            List of feature records
        """
        features = []

        if not latest_data or 'pr_insight_list' not in latest_data:
            return features

        for pr in latest_data.get('pr_insight_list', []):
            if pr.get('type') == 'Feat' and pr.get('importance') == 'High':
                # Extract PR number from pr_link if available
                pr_link = pr.get('pr_link', '')
                pr_number = ''
                if pr_link and '/pull/' in pr_link:
                    pr_number = pr_link.split('/pull/')[-1].split('/')[0]
                elif pr_link and '/commit/' in pr_link:
                    # Handle commit links
                    pr_number = pr_link.split('/commit/')[-1][:7]  # Short commit hash

                features.append({
                    'meaning': pr.get('meaning', ''),
                    'type': pr.get('type', ''),
                    'importance': pr.get('importance', ''),
                    'pr_number': pr_number or pr.get('pr_number', ''),
                    'pr_link': pr_link,
                    'pr_title': pr.get('pr_title', '')
                })

        return features

    def extract_cloud_integrations(self, latest_data):
        """
        Extract cloud provider integration updates

        Filters PRs related to GenAI cloud services (AWS Bedrock/SageMaker, Azure, GCP, etc.)
        Excludes refactor and documentation PRs

        Args:
            latest_data: Latest day's data record

        Returns:
            List of cloud integration records
        """
        integrations = []

        if not latest_data or 'pr_insight_list' not in latest_data:
            return integrations

        # Cloud provider keywords (GenAI services)
        cloud_keywords = {
            'bedrock': 'AWS Bedrock',
            'sagemaker': 'AWS SageMaker',
            'aws': 'AWS',
            'azure': 'Azure',
            'openai': 'Azure OpenAI',
            'google': 'Google Cloud',
            'gcp': 'Google Cloud',
            'vertex': 'Vertex AI',
            'alibaba': 'Alibaba Cloud',
            'aliyun': 'Alibaba Cloud',
            'ali cloud': 'Alibaba Cloud'
        }

        for pr in latest_data.get('pr_insight_list', []):
            pr_type = pr.get('type', '').lower()
            # Skip refactor and documentation PRs
            if pr_type in ['refactor', 'doc', 'docs', 'chore']:
                continue

            meaning = pr.get('meaning', '').lower()

            for keyword, provider_name in cloud_keywords.items():
                if keyword in meaning:
                    # Extract PR number from pr_link if available
                    pr_link = pr.get('pr_link', '')
                    pr_number = ''
                    if pr_link and '/pull/' in pr_link:
                        pr_number = pr_link.split('/pull/')[-1].split('/')[0]
                    elif pr_link and '/commit/' in pr_link:
                        # Handle commit links
                        pr_number = pr_link.split('/commit/')[-1][:7]  # Short commit hash

                    integrations.append({
                        'meaning': pr.get('meaning', ''),
                        'cloud_provider': provider_name,
                        'type': pr.get('type', ''),
                        'importance': pr.get('importance', ''),
                        'pr_number': pr_number or pr.get('pr_number', ''),
                        'pr_link': pr_link,
                        'pr_title': pr.get('pr_title', '')
                    })
                    break

        return integrations
