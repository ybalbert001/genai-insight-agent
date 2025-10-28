import time
import requests
import json
import os
from datetime import datetime, timedelta
from dify_helper import invoke_slow_workflow
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

WORKFLOW_URL = 'http://dify-alb-1-281306538.us-west-2.elb.amazonaws.com/v1/workflows/run'

workflow_api_key_hellogithub = os.getenv('WORKFLOW_API_KEY_HELLOGITHUB')
workflow_api_key_github_analyze = os.getenv('WORKFLOW_API_KEY_GITHUB_ANALYZE')

if not workflow_api_key_hellogithub or not workflow_api_key_github_analyze:
    raise ValueError("请在.env文件中设置WORKFLOW_API_KEY_HELLOGITHUB和WORKFLOW_API_KEY_GITHUB_ANALYZE")

def run_project_analyze_job(repo: str, start_date: str):
    """
    run github_repo_analyze workflow
    """

    return invoke_slow_workflow(record = {"repo": repo, "start_date": start_date}, workflow_api_key=workflow_api_key_github_analyze)

def run_hellogithub_routine_job():
    """
    run daily_news_trigger_v3 workflow
    """
    input_dict = {"task": "获取https://hellogithub.com/ 中前5个AI相关的项目，把相关项目的信息以json形式输出。\n\n## 参考步骤：\n1. 勾选https://hellogithub.com/的AI 标签\n2. 顺序点击进入每个项目(前5个)\n3. 获取详细信息包括：Stars数量，新增stars in Past 6 days, 项目描述, url 和 tags\n\n## 参考输出格式\n[\n{\n  \"name\": \"..\",\n  \"stars\" : \"..\",\n  \"new_stars_past_7_days\" : \"..\",\n  \"description\": \"...\",\n  \"url\" : \"...\",\n  \"tags\" : [...]\n}\n..\n]"}
    
    return invoke_slow_workflow(record=input_dict, workflow_api_key=workflow_api_key_hellogithub)

#run_project_analyze_job("https://github.com/vllm-project/vllm", '2025-10-22')
#run_project_analyze_job("https://github.com/sgl-project/sglang", '2025-10-22')
run_project_analyze_job("https://github.com/langgenius/dify", '2025-10-22')
#run_project_analyze_job("https://github.com/cline/cline", '2025-10-22')
#run_project_analyze_job("https://github.com/BerriAI/litellm", '2025-10-22')
#run_project_analyze_job("https://github.com/hiyouga/LLaMA-Factory", '2025-10-22')
