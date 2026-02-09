#!/usr/bin/env python3
"""
TLDR AI Newsletter Fetcher
Fetches TLDR AI newsletter HTML files from S3 and uses LLM to generate summaries
"""

import boto3
import json
from datetime import date
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote

class TLDRFetcher:
    """从 S3 获取 TLDR AI Newsletter HTML 数据"""

    S3_BUCKET = "aws-genai-insight-report-cn-bucket"
    S3_PREFIX = "genai-reports/tldr_ai"
    TLDR_BASE_URL = "https://d2085bnaxxamc7.cloudfront.net/tldr_ai"

    def __init__(self, region: str = "ap-northeast-1", bedrock_region: str = "us-east-1"):
        """
        Initialize the TLDR fetcher

        Args:
            region: AWS region for S3 bucket
            bedrock_region: AWS region for Bedrock
        """
        self.s3_client = boto3.client('s3', region_name=region)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=bedrock_region)

    def fetch_tldr_news(self, target_date: date, max_items: int = 5) -> List[Dict]:
        """
        获取指定日期的 TLDR 新闻，使用 LLM 生成看点简介

        Args:
            target_date: Target date to fetch news for
            max_items: Maximum number of items to return

        Returns:
            List of news items with cn_title, summary, and link
        """
        date_str = target_date.strftime("%Y-%m-%d")
        print(f"  Fetching TLDR AI news for {date_str}...")

        # 1. 列出 S3 对象
        s3_keys = self._list_s3_objects(date_str)
        if not s3_keys:
            print(f"  - No TLDR data found for {date_str}")
            return []

        print(f"  - Found {len(s3_keys)} HTML files in S3")

        # 2. 下载并解析所有 HTML 文件
        items = []
        for key in s3_keys:
            item = self._download_and_parse(key, date_str)
            if item:
                items.append(item)

        print(f"  - Parsed {len(items)} items successfully")

        # 3. 使用 LLM 按话题吸引力和内容详细程度排序
        print(f"  - Ranking {len(items)} items with LLM...")
        sorted_items = self._sort_by_llm(items, max_items)

        # 4. 为 top N 条生成简介
        print(f"  - Generating summaries for top {len(sorted_items)} items...")
        for item in sorted_items:
            item['summary'] = self._generate_summary_with_llm(
                item.get('cn_title', ''),
                item.get('content', '')
            )

        return sorted_items

    def _list_s3_objects(self, date_str: str) -> List[str]:
        """
        列出指定日期目录下的所有 HTML 对象

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            List of S3 object keys
        """
        prefix = f"{self.S3_PREFIX}/{date_str}/"
        keys = []

        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.S3_BUCKET, Prefix=prefix):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        key = obj['Key']
                        # 跳过目录本身
                        if key != prefix:
                            keys.append(key)
        except Exception as e:
            print(f"  - Error listing S3 objects: {e}")

        return keys

    def _download_and_parse(self, key: str, date_str: str) -> Optional[Dict]:
        """
        下载并解析单个 HTML 文件

        Args:
            key: S3 object key
            date_str: Date string for building CDN link

        Returns:
            Dict with cn_title, content, link, or None if failed
        """
        try:
            response = self.s3_client.get_object(Bucket=self.S3_BUCKET, Key=key)
            html_content = response['Body'].read().decode('utf-8')

            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # 提取标题 (优先 <h1>，其次 <title>)
            h1_tag = soup.find('h1')
            title_tag = soup.find('title')
            title = ''
            if h1_tag:
                title = h1_tag.get_text(strip=True)
            elif title_tag:
                title = title_tag.get_text(strip=True)

            # 提取正文内容 (所有 <p> 标签)
            paragraphs = soup.find_all('p')
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text:
                    content_parts.append(text)
            content = '\n'.join(content_parts)

            # 生成公开访问链接
            filename = key.split('/')[-1]
            filename_encoded = quote(filename, safe='')
            
            link = f"{self.TLDR_BASE_URL}/{date_str}/{filename_encoded}"

            return {
                'cn_title': title,
                'content': content,
                'link': link
            }
        except Exception as e:
            print(f"  - Error downloading {key}: {e}")
            return None

    def _generate_summary_with_llm(self, title: str, content: str) -> str:
        """
        使用 LLM 生成不超过100字的看点简介

        Args:
            title: Article title
            content: Article content

        Returns:
            Summary string (max 100 chars)
        """
        if not content:
            return "暂无简介"

        prompt = f"""请为以下文章生成一段最具看点的简介，要求：
1. 不超过100字
2. 突出最吸引读者的核心观点
3. 语言精炼有力

标题：{title}
内容：{content[:3000]}

只返回简介内容，不要有其他说明。"""

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 256,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            })

            response = self.bedrock_client.invoke_model(
                modelId="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
                body=body
            )

            result = json.loads(response['body'].read())
            summary = result['content'][0]['text'].strip()
            return summary
        except Exception as e:
            print(f"  - Error generating summary: {e}")
            # Fallback: 返回前100字
            return content[:100] + "..." if len(content) > 100 else content

    def _sort_by_llm(self, items: List[Dict], max_items: int = 5) -> List[Dict]:
        """
        使用 LLM 对新闻进行排序

        排序标准：
        1. 话题是否吸引人注意（技术相关性、行业影响力）
        2. 内容是否详细和有信息量

        Args:
            items: List of news items
            max_items: Maximum number of items to return

        Returns:
            Sorted list of news items
        """
        if not items:
            return []

        # 构建 prompt，让 LLM 返回排序后的索引
        news_list = []
        for i, item in enumerate(items):
            news_list.append(f"""
[{i}] 标题: {item.get('cn_title', '')}
内容: {item.get('content', '')[:500]}...
""")

        prompt = f"""你是一位 GenAI 领域的技术专家，需要为解决方案架构师筛选最有价值的 AI 新闻。

以下是今天的 {len(items)} 条 AI 新闻，请按照以下标准进行排序：

**排序标准（按重要性递减）：**
1. **话题吸引力**：与 AI/ML 技术发展密切相关，对技术从业者有实际价值
2. **内容详细程度**：内容详实、有深度分析，而非简单的新闻摘要
3. **行业影响力**：涉及重要公司、重大技术突破或行业趋势

**新闻列表：**
{''.join(news_list)}

请返回排序后的新闻索引（只返回前 {max_items} 条最有价值的），格式为 JSON 数组，例如：[3, 1, 7, 0, 5]

只返回 JSON 数组，不要有其他内容。"""

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            })

            response = self.bedrock_client.invoke_model(
                modelId="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
                body=body
            )

            result = json.loads(response['body'].read())
            content = result['content'][0]['text'].strip()

            # 解析返回的索引数组
            import re
            match = re.search(r'\[[\d,\s]+\]', content)
            if match:
                indices = json.loads(match.group())
                # 根据索引重新排序
                sorted_items = []
                for idx in indices:
                    if 0 <= idx < len(items):
                        sorted_items.append(items[idx])
                print(f"  - LLM selected {len(sorted_items)} items")
                return sorted_items

        except Exception as e:
            print(f"  - LLM ranking failed: {e}, returning first {max_items} items")

        # Fallback: 返回前 N 条
        return items[:max_items]


if __name__ == "__main__":
    # 测试代码
    from datetime import datetime, timedelta

    fetcher = TLDRFetcher()

    # 获取昨天的数据进行测试
    yesterday = datetime.now().date() - timedelta(days=1)
    news = fetcher.fetch_tldr_news(yesterday, max_items=3)

    print(f"\nFound {len(news)} news items:")
    for i, item in enumerate(news, 1):
        print(f"\n{i}. {item.get('cn_title')}")
        print(f"   Link: {item.get('link')}")
        print(f"   Summary: {item.get('summary')}")
