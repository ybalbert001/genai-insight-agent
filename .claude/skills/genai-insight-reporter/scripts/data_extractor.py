#!/usr/bin/env python3
"""
Data Extractor for Claude Review
Extracts raw feature and integration data in JSON format for AI curation
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from data_analyzer import DataAnalyzer


def extract_data_for_review(dynamodb_script_path, days=15, region="us-east-1"):
    """
    Extract raw data for Claude to review

    Args:
        dynamodb_script_path: Path to dynamodb_manager.py
        days: Number of days to look back
        region: AWS region

    Returns:
        Dict with features, integrations, and metadata
    """
    analyzer = DataAnalyzer(dynamodb_script_path, region)

    today = datetime.now().date()
    start_date = today - timedelta(days=days)

    print(f"Extracting data from {start_date} to {today}...", file=sys.stderr)

    # Get Human-P0 repos
    repos = analyzer.get_human_p0_repos()
    if not repos:
        print("No Human-P0 repos found", file=sys.stderr)
        return None

    extraction_result = {
        "metadata": {
            "extraction_date": today.isoformat(),
            "analysis_window_days": days,
            "num_repos": len(repos)
        },
        "repos": []
    }

    for repo_url in repos:
        repo_name = '/'.join(repo_url.split('/')[-2:])
        print(f"Processing {repo_name}...", file=sys.stderr)

        # Get latest data (try today and yesterday)
        latest_data = None
        for date_offset in [0, 1]:
            check_date = today - timedelta(days=date_offset)
            latest = analyzer.query_repo_data(repo_url, check_date, check_date)
            if latest and len(latest) > 0:
                latest_data = latest[0]
                print(f"  Using data from {check_date}", file=sys.stderr)
                break

        if not latest_data:
            print(f"  No recent data found", file=sys.stderr)
            continue

        # Extract all High-importance PRs for review (not just Feat)
        candidate_features = []
        if 'pr_insight_list' in latest_data:
            for pr in latest_data['pr_insight_list']:
                if pr.get('importance') == 'High':
                    candidate_features.append({
                        'type': pr.get('type', ''),
                        'importance': pr.get('importance', ''),
                        'meaning': pr.get('meaning', ''),
                        'pr_number': pr.get('pr_number', ''),
                        'pr_title': pr.get('pr_title', ''),
                        'pr_url': pr.get('pr_url', ''),
                        # Include raw data for context
                        '_raw_pr': pr
                    })

        # Extract all potential cloud integrations
        candidate_integrations = []
        if 'pr_insight_list' in latest_data:
            cloud_keywords = ['bedrock', 'sagemaker', 'aws', 'azure', 'openai',
                            'google', 'gcp', 'vertex', 'alibaba', 'aliyun', 'ali cloud']

            for pr in latest_data['pr_insight_list']:
                meaning = pr.get('meaning', '').lower()

                # Check if any keyword matches
                matched_keywords = [kw for kw in cloud_keywords if kw in meaning]

                if matched_keywords:
                    candidate_integrations.append({
                        'type': pr.get('type', ''),
                        'importance': pr.get('importance', ''),
                        'meaning': pr.get('meaning', ''),
                        'pr_number': pr.get('pr_number', ''),
                        'pr_title': pr.get('pr_title', ''),
                        'pr_url': pr.get('pr_url', ''),
                        'matched_keywords': matched_keywords,
                        '_raw_pr': pr
                    })

        repo_info = {
            "repo_name": repo_name,
            "repo_url": repo_url,
            "data_date": latest_data.get('collect_date', ''),
            "candidate_features": candidate_features,
            "candidate_cloud_integrations": candidate_integrations,
            "stats": {
                "num_candidate_features": len(candidate_features),
                "num_candidate_integrations": len(candidate_integrations)
            }
        }

        extraction_result["repos"].append(repo_info)
        print(f"  Found {len(candidate_features)} feature candidates, "
              f"{len(candidate_integrations)} integration candidates", file=sys.stderr)

    return extraction_result


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Extract raw data in JSON format for Claude to review and curate'
    )
    parser.add_argument(
        '--dynamodb-script',
        required=True,
        help='Path to dynamodb_manager.py script'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=15,
        help='Number of days to look back (default: 15)'
    )
    parser.add_argument(
        '--output',
        help='Output JSON file path (default: stdout)'
    )

    args = parser.parse_args()

    # Validate dynamodb script exists
    if not Path(args.dynamodb_script).exists():
        print(f"Error: dynamodb_manager.py not found at {args.dynamodb_script}",
              file=sys.stderr)
        sys.exit(1)

    # Extract data
    result = extract_data_for_review(
        args.dynamodb_script,
        days=args.days,
        region=args.region
    )

    if not result:
        print("Failed to extract data", file=sys.stderr)
        sys.exit(1)

    # Output JSON
    json_output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_output, encoding='utf-8')
        print(f"\n✅ Data extracted to: {output_path}", file=sys.stderr)
    else:
        print(json_output)

    # Print summary
    print(f"\nSummary:", file=sys.stderr)
    print(f"  Repos analyzed: {result['metadata']['num_repos']}", file=sys.stderr)
    total_features = sum(r['stats']['num_candidate_features'] for r in result['repos'])
    total_integrations = sum(r['stats']['num_candidate_integrations'] for r in result['repos'])
    print(f"  Total feature candidates: {total_features}", file=sys.stderr)
    print(f"  Total integration candidates: {total_integrations}", file=sys.stderr)


if __name__ == "__main__":
    main()
