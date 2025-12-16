#!/usr/bin/env python3
"""
GenAI Insight Report Generator
Main script for generating comprehensive GenAI project insight reports
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import local modules
sys.path.insert(0, str(Path(__file__).parent))

from data_analyzer import DataAnalyzer
from chart_generator import ChartGenerator

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("Warning: jinja2 not installed. Install with: pip install jinja2")
    print("Falling back to basic template rendering")


class ReportGenerator:
    """Main report generator orchestrating data analysis and report creation"""

    def __init__(self, output_dir, dynamodb_script_path, region="us-east-1"):
        """
        Initialize the report generator

        Args:
            output_dir: Directory to save reports and charts
            dynamodb_script_path: Path to dynamodb_manager.py
            region: AWS region
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.images_dir = self.output_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self.analyzer = DataAnalyzer(dynamodb_script_path, region)
        self.chart_gen = ChartGenerator(self.images_dir)

    def generate_report(self, days=15, max_features=5, max_features_per_repo=3, target_date=None):
        """
        Generate a complete GenAI insight report

        Args:
            days: Number of days to analyze (default: 15)
            max_features: Maximum total features to include (default: 5)
            max_features_per_repo: Maximum features per repo (default: 3)
            target_date: Target date for report (default: today)

        Returns:
            Path to generated report file
        """
        print("="*60)
        print("GenAI Insight Report Generator")
        print("="*60)

        today = target_date if target_date else datetime.now().date()
        start_date = today - timedelta(days=days)
        end_date = today

        print(f"\nAnalysis period: {start_date} to {end_date}")
        print(f"Analysis window: {days} days\n")

        # Step 1: Get Human-P0 repos
        repos = self.analyzer.get_human_p0_repos()
        if not repos:
            print("No Human-P0 repos found. Exiting.")
            return None

        print(f"Analyzing {len(repos)} repos\n")

        # Step 2: Collect data for all repos
        repos_data = {}
        all_increments = {}
        repo_names = {}
        repo_stars = {}  # Store current star count for each repo

        for repo_url in repos:
            repo_name = repo_url.split('/')[-1]
            repo_names[repo_url] = repo_name
            print(f"Processing: {repo_name}")

            # Get 15-day data
            data_list = self.analyzer.query_repo_data(repo_url, start_date, end_date)
            if not data_list:
                print(f"  - No data found")
                continue

            print(f"  - Found data for {len(data_list)} days")

            # Calculate daily increments
            increments = self.analyzer.calculate_daily_increments(data_list)
            all_increments[repo_url] = increments

            # Get data for target date only (no fallback to previous day)
            latest_data = self.analyzer.query_repo_data(repo_url, today, today)

            if not latest_data or len(latest_data) == 0:
                print(f"  - No data found for {today}")
                repos_data[repo_url] = {'features': [], 'cloud_integrations': []}
                repo_stars[repo_url] = 0
                continue

            latest_data = latest_data[0]
            print(f"  - Using data from {today}")

            # Extract current star count from latest data
            current_stars = int(latest_data.get('metric_info', {}).get('stars', '0'))
            repo_stars[repo_url] = current_stars

            # Extract features and cloud integrations
            features = self.analyzer.extract_important_features(latest_data)
            cloud_integrations = self.analyzer.extract_cloud_integrations(latest_data)

            repos_data[repo_url] = {
                'features': features,
                'cloud_integrations': cloud_integrations
            }

            print(f"  - Found {len(features)} important features")
            print(f"  - Found {len(cloud_integrations)} cloud integrations")

        # Step 3: Generate charts
        print("\nGenerating charts...")
        date_str = today.strftime("%Y%m%d")
        chart_path = self.chart_gen.generate_activity_charts(
            all_increments, repo_names, date_str
        )

        # Step 4: Generate markdown report
        print("\nGenerating report...")
        report_path = self._generate_markdown_report(
            repos_data, all_increments, repo_names, repo_stars, chart_path, today, max_features, max_features_per_repo
        )

        print("\n" + "="*60)
        print("Report generation complete!")
        print(f"Report: {report_path}")
        print(f"Charts: {self.images_dir}")
        print("="*60)

        return report_path

    def _generate_markdown_report(self, repos_data, all_increments, repo_names, repo_stars, chart_path, today, max_features, max_features_per_repo):
        """
        Generate markdown report content using Jinja2 template

        Args:
            repos_data: Dict of repo data with features and integrations
            all_increments: Dict of increment data for all repos
            repo_names: Dict mapping repo URLs to display names
            repo_stars: Dict mapping repo URLs to current star counts
            chart_path: Path to generated chart
            today: Date object for today
            max_features: Maximum total features
            max_features_per_repo: Maximum features per repo

        Returns:
            Path to saved report file
        """
        # Prepare template data
        template_data = self._prepare_template_data(
            repos_data, all_increments, repo_names, repo_stars, chart_path, today, max_features, max_features_per_repo
        )

        # Generate report using Jinja2 if available
        if JINJA2_AVAILABLE:
            report_content = self._render_with_jinja2(template_data)
        else:
            report_content = self._render_basic(template_data)

        # Save report
        report_path = self.output_dir / f"GenAI_Insight_Report_{today.strftime('%Y%m%d')}.md"
        report_path.write_text(report_content, encoding='utf-8')

        print(f"Report saved: {report_path}")
        return report_path

    def _prepare_template_data(self, repos_data, all_increments, repo_names, repo_stars, chart_path, today, max_features, max_features_per_repo):
        """
        Prepare data for template rendering

        Args:
            repos_data: Dict of repo data with features and integrations
            all_increments: Dict of increment data for all repos
            repo_names: Dict mapping repo URLs to display names
            repo_stars: Dict mapping repo URLs to current star counts
            chart_path: Path to generated chart
            today: Date object for today
            max_features: Maximum total features
            max_features_per_repo: Maximum features per repo

        Returns:
            Dict with all template variables
        """
        # Collect repo links for data source
        all_repos = list(repos_data.keys())
        repo_links = ', '.join([f"[{url.split('/')[-1]}]({url})" for url in all_repos])

        # Prepare features by repo
        features_by_repo = []
        feature_count = 0
        section_number = 1

        for repo_url, data in repos_data.items():
            if not data.get('features') or feature_count >= max_features:
                continue

            repo_name = repo_url.split('/')[-1]
            repo_full_name = '/'.join(repo_url.split('/')[-2:])
            features = data['features'][:max_features_per_repo]

            if features:
                repo_features = []
                for feat in features:
                    if feature_count >= max_features:
                        break

                    # Extract title from PR title or meaning
                    pr_title = feat.get('pr_title', '')
                    meaning = feat.get('meaning', '')

                    if pr_title:
                        title = pr_title
                    else:
                        # Use first sentence as title
                        sentences = meaning.split('。')
                        title = sentences[0] if sentences else meaning[:50]

                    # Use pr_link directly from data, or construct from pr_number
                    pr_number = feat.get('pr_number', '')
                    pr_url = feat.get('pr_link', '')
                    if not pr_url and pr_number:
                        pr_url = f"{repo_url}/pull/{pr_number}"

                    repo_features.append({
                        'title': title,
                        'pr_number': pr_number,
                        'pr_url': pr_url,
                        'pr_title': pr_title,
                        'description': meaning
                    })
                    feature_count += 1

                features_by_repo.append({
                    'section_number': f"1.{section_number}",
                    'repo_name': repo_name,
                    'repo_full_name': repo_full_name,
                    'features': repo_features
                })
                section_number += 1

        # Prepare cloud integrations by repo
        cloud_integrations_by_repo = []
        cloud_section_number = 1

        for repo_url, data in repos_data.items():
            if not data.get('cloud_integrations'):
                continue

            repo_name = repo_url.split('/')[-1]
            repo_full_name = '/'.join(repo_url.split('/')[-2:])
            integrations = data['cloud_integrations']

            if integrations:
                repo_integrations = []
                for integ in integrations:
                    meaning = integ.get('meaning', '')

                    # Extract title (first sentence)
                    title_part = meaning.split('。')[0] if '。' in meaning else meaning[:50]

                    # Use pr_link directly from data, or construct from pr_number
                    pr_number = integ.get('pr_number', '')
                    pr_url = integ.get('pr_link', '')
                    if not pr_url and pr_number:
                        pr_url = f"{repo_url}/pull/{pr_number}"

                    repo_integrations.append({
                        'cloud_provider': integ.get('cloud_provider', 'Unknown'),
                        'title': title_part,
                        'pr_number': pr_number,
                        'pr_url': pr_url,
                        'pr_title': integ.get('pr_title', ''),
                        'description': meaning
                    })

                cloud_integrations_by_repo.append({
                    'section_number': f"2.{cloud_section_number}",
                    'repo_name': repo_name,
                    'repo_full_name': repo_full_name,
                    'integrations': repo_integrations
                })
                cloud_section_number += 1

        # Calculate community metrics for analysis
        metrics_summary = []
        for repo_url, increments in all_increments.items():
            if not increments:
                continue

            repo_name = repo_names.get(repo_url, repo_url.split('/')[-1])

            # Calculate average daily metrics
            total_pr = sum(inc['pr_increment'] for inc in increments)
            total_merged = sum(inc['merged_pr_increment'] for inc in increments)
            total_issues = sum(inc['issue_increment'] for inc in increments)
            days_count = len(increments)

            # Get current star count
            current_stars = repo_stars.get(repo_url, 0)

            metrics_summary.append({
                'repo': repo_name,
                'repo_url': repo_url,
                'avg_daily_pr': round(total_pr / days_count, 1),
                'avg_daily_merged': round(total_merged / days_count, 1),
                'avg_daily_issues': round(total_issues / days_count, 1),
                'current_stars': current_stars,
                'days': days_count
            })

        # Calculate analysis dates
        start_date = today - timedelta(days=15)

        return {
            'date': today.strftime('%Y-%m-%d'),
            'repo_links': repo_links,
            'features_by_repo': features_by_repo,
            'cloud_integrations_by_repo': cloud_integrations_by_repo,
            'chart_image_path': f"images/{chart_path.name}",
            'analysis_days': 15,
            'analysis_start_date': start_date.strftime('%Y-%m-%d'),
            'analysis_end_date': today.strftime('%Y-%m-%d'),
            'metrics_summary': metrics_summary,  # Raw metrics for Claude to interpret
            'interpretation': None,  # To be filled by Claude
            'emerging_insights': None,  # For future use
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _render_with_jinja2(self, template_data):
        """
        Render report using Jinja2 template

        Args:
            template_data: Dict with template variables

        Returns:
            Rendered report content
        """
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent / 'templates'
        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Load and render template
        template = env.get_template('report_template.md.j2')
        return template.render(**template_data)

    def _render_basic(self, template_data):
        """
        Fallback: render report without Jinja2 (basic string formatting)

        Args:
            template_data: Dict with template variables

        Returns:
            Rendered report content
        """
        lines = [
            f"# GenAI Insight Report - {template_data['date']}",
            "",
            "## 数据来源",
            f"> https://github.com ({template_data['repo_links']})",
            ">",
            "> https://tldr.tech/ai/",
            "",
            "## 1. 重点项目更新 (Priority Repo Updates)",
            ""
        ]

        # Add features
        if template_data['features_by_repo']:
            for repo_info in template_data['features_by_repo']:
                lines.append(f"### {repo_info['section_number']} {repo_info['repo_name']} ({repo_info['repo_full_name']})")
                lines.append("")

                for feature in repo_info['features']:
                    lines.append(f"**{feature['title']}**")
                    if feature['pr_number'] and feature['pr_url']:
                        pr_line = f"- **PR**: [#{feature['pr_number']}]({feature['pr_url']})"
                        if feature['pr_title']:
                            pr_line += f" - {feature['pr_title']}"
                        lines.append(pr_line)
                    lines.append(f"- **描述**: {feature['description']}")
                    lines.append("")
        else:
            lines.append("*本期暂无重要功能更新*")
            lines.append("")

        # Add cloud integrations
        lines.extend([
            "## 2. 云厂商集成进展",
            ""
        ])

        if template_data['cloud_integrations_by_repo']:
            for repo_info in template_data['cloud_integrations_by_repo']:
                lines.append(f"### {repo_info['section_number']} {repo_info['repo_name']} ({repo_info['repo_full_name']})")
                lines.append("")

                for integ in repo_info['integrations']:
                    lines.append(f"**[{integ['cloud_provider']}] {integ['title']}**")
                    if integ['pr_number'] and integ['pr_url']:
                        pr_line = f"- **PR**: [#{integ['pr_number']}]({integ['pr_url']})"
                        if integ['pr_title']:
                            pr_line += f" - {integ['pr_title']}"
                        lines.append(pr_line)
                    lines.append(f"- {integ['description']}")
                    lines.append("")
        else:
            lines.append("*本期暂无云厂商集成更新*")
            lines.append("")

        # Add community analysis
        lines.extend([
            "---",
            "",
            "## 3. 开源项目社区生态指标",
            "",
            f"![社区活跃度分析]({template_data['chart_image_path']})",
            "",
            f"**分析周期**: 近{template_data['analysis_days']}天 ({template_data['analysis_start_date']} 至 {template_data['analysis_end_date']})",
            "",
            "上图展示了三个关键指标的每日增量趋势：",
            "- **每日新增PR**: 包括open和merged的总PR数量",
            "- **每日Merged PR**: 成功合并的PR数量",
            "- **每日新增Issue**: 新开启的Issue数量",
            "",
            "每条线代表一个不同的仓库，支持跨仓库对比（横向）和时间趋势分析（纵向）。",
            "",
            "**解读**:",
            template_data['interpretation'],
            "",
            "---",
            "",
            f"**报告生成时间**: {template_data['generation_time']}",
            ""
        ])

        return '\n'.join(lines)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate GenAI Insight Report from DynamoDB data'
    )
    parser.add_argument(
        '--output-dir',
        default='report_output',
        help='Output directory for reports (default: report_output)'
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
        help='Number of days to analyze (default: 15)'
    )
    parser.add_argument(
        '--max-features',
        type=int,
        default=5,
        help='Maximum total features to include (default: 5)'
    )
    parser.add_argument(
        '--max-features-per-repo',
        type=int,
        default=3,
        help='Maximum features per repo (default: 3)'
    )
    parser.add_argument(
        '--date',
        help='Target date for report (format: YYYY-MM-DD, default: today)'
    )

    args = parser.parse_args()

    # Validate dynamodb script exists
    if not Path(args.dynamodb_script).exists():
        print(f"Error: dynamodb_manager.py not found at {args.dynamodb_script}")
        sys.exit(1)

    # Parse target date if provided
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
            sys.exit(1)

    # Generate report
    generator = ReportGenerator(
        output_dir=args.output_dir,
        dynamodb_script_path=args.dynamodb_script,
        region=args.region
    )

    report_path = generator.generate_report(
        days=args.days,
        max_features=args.max_features,
        max_features_per_repo=args.max_features_per_repo,
        target_date=target_date
    )

    if report_path:
        print(f"\n✅ Success! Report generated at: {report_path}")
    else:
        print("\n❌ Report generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
