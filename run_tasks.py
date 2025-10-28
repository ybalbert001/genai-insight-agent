import schedule
import time
import requests
import json
import logging
from datetime import datetime, timedelta
from dify_helper import invoke_slow_workflow

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('routine_tasks.log'),
        logging.StreamHandler()
    ]
)

workflow_api_key_hellogithub = 'app-lJpX4GANg9d6pud8ciHnh9EJ'
workflow_api_key_github_analyze = 'app-UWkAZ1R1rFKh5ppB5iONDzSx'

def run_project_analyze_job(repo: str, start_date: str):
    """
    run github_repo_analyze workflow
    """
    logging.info(f"开始分析项目: {repo}, 日期: {start_date}")
    try:
        result = invoke_slow_workflow(record = {"repo": repo, "start_date": start_date}, workflow_api_key=workflow_api_key_github_analyze)
        logging.info(f"项目分析完成: {repo}")
        return result
    except Exception as e:
        logging.error(f"项目分析失败: {repo}, 错误: {str(e)}")
        raise

def run_hellogithub_routine_job():
    """
    run daily_news_trigger_v3 workflow
    """
    logging.info("开始执行HelloGitHub例行任务")
    input_dict = {"task": "获取https://hellogithub.com/ 中前5个AI相关的项目，把相关项目的信息以json形式输出。\n\n## 参考步骤：\n1. 勾选https://hellogithub.com/的AI 标签\n2. 顺序点击进入每个项目(前5个)\n3. 获取详细信息包括：Stars数量，新增stars in Past 6 days, 项目描述, url 和 tags\n\n## 参考输出格式\n[\n{\n  \"name\": \"..\",\n  \"stars\" : \"..\",\n  \"new_stars_past_7_days\" : \"..\",\n  \"description\": \"...\",\n  \"url\" : \"...\",\n  \"tags\" : [...]\n}\n..\n]"}
    
    try:
        result = invoke_slow_workflow(record=input_dict, workflow_api_key=workflow_api_key_hellogithub)
        logging.info("HelloGitHub例行任务完成")
        return result
    except Exception as e:
        logging.error(f"HelloGitHub例行任务失败: {str(e)}")
        raise


# 每天12:00执行项目分析
schedule.every().day.at("10:30").do(lambda: run_project_analyze_job("https://github.com/vllm-project/vllm", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")))

schedule.every().day.at("10:35").do(lambda: run_project_analyze_job("https://github.com/sgl-project/sglang", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")))

schedule.every().day.at("10:40").do(lambda: run_project_analyze_job("https://github.com/langgenius/dify", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")))

schedule.every().day.at("10:45").do(lambda: run_project_analyze_job("https://github.com/cline/cline", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")))

schedule.every().day.at("10:50").do(lambda: run_project_analyze_job("https://github.com/BerriAI/litellm", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")))

schedule.every().day.at("10:55").do(lambda: run_project_analyze_job("https://github.com/hiyouga/LLaMA-Factory", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")))

# 运行调度器
logging.info("任务调度器启动")
while True:
    schedule.run_pending()
    time.sleep(1)
