#!/usr/bin/env python3
"""
TLDR.tech AI News Fetcher
Fetches AI news from tldr.tech for emerging insights analysis
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def generate_tldr_urls(days=7):
    """
    Generate tldr.tech URLs for the past N days

    Args:
        days: Number of days to look back

    Returns:
        List of (date, url) tuples
    """
    today = datetime.now().date()
    urls = []

    for i in range(days):
        date = today - timedelta(days=i)
        # tldr.tech uses YYYY-MM-DD format in URLs
        date_str = date.strftime('%Y-%m-%d')
        url = f"https://tldr.tech/ai/{date_str}"
        urls.append((date_str, url))

    return urls


def create_fetch_instructions(days=7):
    """
    Create instructions for Claude to fetch tldr.tech content

    Since this script runs in skill context, it outputs instructions
    for Claude to use WebFetch tool to retrieve the content.

    Args:
        days: Number of days to look back

    Returns:
        Dict with URLs and prompts for Claude
    """
    urls = generate_tldr_urls(days)

    instructions = {
        "metadata": {
            "fetch_date": datetime.now().isoformat(),
            "lookback_days": days,
            "num_urls": len(urls)
        },
        "urls_to_fetch": []
    }

    for date_str, url in urls:
        instructions["urls_to_fetch"].append({
            "date": date_str,
            "url": url,
            "prompt": (
                "Extract the main AI news items from this TLDR newsletter. "
                "For each news item, provide: "
                "1) Title or topic, "
                "2) Brief summary (1-2 sentences), "
                "3) Key technical terms or technologies mentioned, "
                "4) Category (e.g., model release, infrastructure, tooling, research). "
                "Focus on technical developments relevant to GenAI practitioners."
            )
        })

    return instructions


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate fetch instructions for tldr.tech AI news'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back (default: 7)'
    )
    parser.add_argument(
        '--output',
        help='Output JSON file path (default: stdout)'
    )

    args = parser.parse_args()

    # Generate fetch instructions
    instructions = create_fetch_instructions(args.days)

    # Output as JSON
    json_output = json.dumps(instructions, indent=2, ensure_ascii=False)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_output, encoding='utf-8')
        print(f"✅ Fetch instructions saved to: {output_path}", file=sys.stderr)
    else:
        print(json_output)

    # Print summary
    print(f"\nSummary:", file=sys.stderr)
    print(f"  URLs to fetch: {instructions['metadata']['num_urls']}", file=sys.stderr)
    print(f"  Date range: {instructions['urls_to_fetch'][-1]['date']} to {instructions['urls_to_fetch'][0]['date']}",
          file=sys.stderr)
    print(f"\nClaude should use WebFetch tool to retrieve content from each URL.", file=sys.stderr)


if __name__ == "__main__":
    main()
