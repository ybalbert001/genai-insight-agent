#!/usr/bin/env python3
"""
Chart Generator Module
Creates matplotlib visualizations for GenAI insight reports
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path


class ChartGenerator:
    """Generator for matplotlib charts with academic paper styling"""

    def __init__(self, output_dir):
        """
        Initialize the chart generator

        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configure matplotlib with academic paper style
        self._configure_matplotlib()

        # Define color palette
        self.colors = [
            '#1f77b4',  # Blue
            '#ff7f0e',  # Orange
            '#2ca02c',  # Green
            '#d62728',  # Red
            '#9467bd',  # Purple
            '#8c564b',  # Brown
            '#e377c2',  # Pink
            '#7f7f7f',  # Gray
            '#bcbd22',  # Yellow-green
            '#17becf'   # Cyan
        ]

    def _configure_matplotlib(self):
        """Configure matplotlib with academic paper styling"""
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
        plt.rcParams['font.size'] = 9
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['grid.linewidth'] = 0.5
        plt.rcParams['lines.linewidth'] = 1.5
        plt.rcParams['axes.unicode_minus'] = False

    def generate_activity_charts(self, all_increments, repo_names, date_str):
        """
        Generate community activity charts

        Creates four subplots showing:
        1. Daily New PRs
        2. Daily Merged PRs
        3. Daily New Open Issues
        4. Daily Star Increments

        Args:
            all_increments: Dict mapping repo_url to list of increment records
            repo_names: Dict mapping repo_url to display names
            date_str: Date string for filename

        Returns:
            Path to saved chart file
        """
        print("Generating activity charts...")

        fig, axes = plt.subplots(2, 2, figsize=(14, 8))
        axes = axes.flatten()

        metrics = [
            ('pr_increment', 'Daily New PRs', axes[0]),
            ('merged_pr_increment', 'Daily Merged PRs', axes[1]),
            ('issue_increment', 'Daily New Open Issues', axes[2]),
            ('star_increment', 'Daily Star Increments', axes[3])
        ]

        for metric_key, title, ax in metrics:
            for idx, (repo_url, increments) in enumerate(all_increments.items()):
                if not increments:
                    continue

                dates = [datetime.strptime(inc['date'], '%Y-%m-%d') for inc in increments]
                values = [inc.get(metric_key, 0) for inc in increments]

                repo_name = repo_names.get(repo_url, repo_url.split('/')[-1])
                color = self.colors[idx % len(self.colors)]

                ax.plot(dates, values,
                       marker='o',
                       markersize=3,
                       label=repo_name,
                       color=color,
                       alpha=0.8)

            ax.set_title(title, fontsize=10, fontweight='bold')
            ax.set_xlabel('Date', fontsize=9)
            ax.set_ylabel('Count', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(fontsize=7, loc='best', framealpha=0.9)

            # Format date axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)

        plt.tight_layout()

        chart_path = self.output_dir / f"community_activity_{date_str}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Chart saved: {chart_path}")
        return chart_path

    def generate_comprehensive_chart(self, all_increments, repo_names, date_str):
        """
        Generate comprehensive 2x2 chart with multiple metrics

        Creates four subplots showing different aspects of community activity

        Args:
            all_increments: Dict mapping repo_url to list of increment records
            repo_names: Dict mapping repo_url to display names
            date_str: Date string for filename

        Returns:
            Path to saved chart file
        """
        print("Generating comprehensive chart...")

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

        metrics = [
            ('pr_increment', 'Daily New PRs', ax1),
            ('merged_pr_increment', 'Daily Merged PRs', ax2),
            ('issue_increment', 'Daily New Issues', ax3),
            ('pr_increment', 'Activity Trend', ax4)  # Can be customized
        ]

        for idx, (repo_url, increments) in enumerate(all_increments.items()):
            if not increments:
                continue

            dates = [datetime.strptime(inc['date'], '%Y-%m-%d') for inc in increments]
            repo_name = repo_names.get(repo_url, repo_url.split('/')[-1])
            color = self.colors[idx % len(self.colors)]

            # Plot on each subplot
            for metric_key, title, ax in metrics[:3]:
                values = [inc[metric_key] for inc in increments]
                ax.plot(dates, values,
                       marker='o',
                       markersize=3,
                       label=repo_name,
                       color=color,
                       alpha=0.8)

            # Fourth subplot - combined view
            pr_values = [inc['pr_increment'] for inc in increments]
            merged_values = [inc['merged_pr_increment'] for inc in increments]
            combined_values = [p + m for p, m in zip(pr_values, merged_values)]
            ax4.plot(dates, combined_values,
                    marker='o',
                    markersize=3,
                    label=repo_name,
                    color=color,
                    alpha=0.8)

        # Configure all subplots
        for metric_key, title, ax in metrics:
            ax.set_title(title, fontsize=11, fontweight='bold')
            ax.set_xlabel('Date', fontsize=9)
            ax.set_ylabel('Count', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(fontsize=7, loc='best', framealpha=0.9)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)

        fig.suptitle('GenAI Project Community Activity Analysis',
                    fontsize=14, fontweight='bold')

        plt.tight_layout()

        chart_path = self.output_dir / f"comprehensive_activity_{date_str}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Comprehensive chart saved: {chart_path}")
        return chart_path

    def generate_single_metric_chart(self, all_increments, repo_names, metric_key, title, date_str):
        """
        Generate a single metric chart

        Args:
            all_increments: Dict mapping repo_url to list of increment records
            repo_names: Dict mapping repo_url to display names
            metric_key: Metric to plot (e.g., 'pr_increment')
            title: Chart title
            date_str: Date string for filename

        Returns:
            Path to saved chart file
        """
        print(f"Generating {title} chart...")

        fig, ax = plt.subplots(figsize=(10, 5))

        for idx, (repo_url, increments) in enumerate(all_increments.items()):
            if not increments:
                continue

            dates = [datetime.strptime(inc['date'], '%Y-%m-%d') for inc in increments]
            values = [inc[metric_key] for inc in increments]

            repo_name = repo_names.get(repo_url, repo_url.split('/')[-1])
            color = self.colors[idx % len(self.colors)]

            ax.plot(dates, values,
                   marker='o',
                   markersize=4,
                   label=repo_name,
                   color=color,
                   alpha=0.8,
                   linewidth=2)

        ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Count', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=8, loc='best', framealpha=0.9)

        # Format date axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)

        plt.tight_layout()

        safe_title = title.lower().replace(' ', '_')
        chart_path = self.output_dir / f"{safe_title}_{date_str}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Chart saved: {chart_path}")
        return chart_path
