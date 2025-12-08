import json
import requests
import time
import random
from typing import Dict, Any, List, Optional, Tuple, Union
from json_repair import repair_json

WORKFLOW_URL = 'http://dify-alb-1-281306538.us-west-2.elb.amazonaws.com/v1/workflows/run'

def invoke_slow_workflow(record: Dict[str, Any], workflow_api_key:str) -> str:
    """
    使用DifyHelper调用Dify API（流式模式）
    
    Args:
        record: 工作流的输入数据
        workflow_api_key: 工作流API密钥
        
    Returns:
        工作流响应文本
    """
    # 创建DifyHelper实例
    dify_helper = DifyHelper(
        workflow_api_url=WORKFLOW_URL,
        workflow_api_key=workflow_api_key
    )
    
    # 调用工作流API
    return dify_helper.invoke_workflow(record, response_mode="streaming")

class DifyHelper:
    def __init__(self, workflow_api_url: str = "http://dify-alb-1-281306538.us-west-2.elb.amazonaws.com/v1/workflows/run", workflow_api_key: str = None, max_retries=5, base_delay=10, max_delay=600, timeout=900):
        """
        Initialize the DifyHelper with retry parameters.
        
        Args:
            workflow_api_url: The URL for the workflow API (default: Dify ALB URL)
            workflow_api_key: The API key for authentication
            max_retries: Maximum number of retry attempts (default: 5)
            base_delay: Initial delay in seconds (default: 10)
            max_delay: Maximum delay in seconds (default: 600)
            timeout: Request timeout in seconds (default: 900 = 15 minutes)
        """
        self.workflow_api_url = workflow_api_url
        self.workflow_api_key = workflow_api_key
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.timeout = timeout
        
        # 创建一个会话对象以复用连接
        self.session = requests.Session()
        # 设置连接池参数
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # 我们自己处理重试
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def invoke_workflow(self, record: Dict[str, Any], response_mode: str = "streaming") -> Union[Dict, str]:
        """
        Invoke the workflow with retry mechanism and exponential backoff.
        
        Args:
            record: The input data for the workflow
            response_mode: The response mode, either "streaming" or "blocking" (default: "streaming")
            
        Returns:
            The workflow output or an error dict if all retries fail
        """
        headers = {
            "Authorization": f"Bearer {self.workflow_api_key}", 
            "Content-Type": "application/json",
            "Connection": "keep-alive",  # 保持连接
            "User-Agent": "genai-insight/1.0"
        }
        payload = {
            "inputs": record,
            "response_mode": response_mode,
            "user": "genai-insight"
        }
        
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                print(f"尝试调用工作流 (第 {retry_count + 1} 次)...")
                
                if response_mode == "blocking":
                    # For blocking mode, we don't need streaming
                    response = self.session.post(
                        self.workflow_api_url, 
                        headers=headers, 
                        data=json.dumps(payload), 
                        timeout=self.timeout
                    )
                    response.raise_for_status()  # Raise an exception for 4XX/5XX responses
                    
                    # Process blocking response
                    result = response.json()
                    print("工作流调用成功 (blocking模式)")
                    return result["data"].get("outputs", {})
                else:
                    # For streaming mode
                    response = self.session.post(
                        self.workflow_api_url, 
                        headers=headers, 
                        data=json.dumps(payload), 
                        timeout=self.timeout, 
                        stream=True
                    )
                    response.raise_for_status()  # Raise an exception for 4XX/5XX responses
                    
                    # Process streaming response
                    text_chunks = []
                    
                    for line in response.iter_lines(decode_unicode=True):
                        if not line:
                            continue

                        # Remove the "data: " prefix if present
                        if line.startswith('data: '):
                            line = line[6:]  # Remove "data: " prefix
                        
                        # Skip empty lines or ping events
                        if not line or line == 'event: ping':
                            continue
                            
                        try:
                            # Parse the JSON data
                            data = json.loads(line)
                            
                            # Only collect text from "text_chunk" events
                            if data.get("event") == "text_chunk":
                                chunk_data = data.get("data", {}).get("text", "")
                                text_chunks.append(chunk_data)
                        except json.JSONDecodeError:
                            # Skip lines that aren't valid JSON
                            continue

                    result = "".join(text_chunks)
                    print(f"工作流调用成功 (streaming模式)，返回文本长度: {len(result)}")
                    return result
                
            except requests.exceptions.Timeout as e:
                last_error = e
                retry_count += 1
                print(f"请求超时 (第 {retry_count} 次尝试): {e}")
                
                if retry_count > self.max_retries:
                    break
                    
                # 对于超时错误，使用更长的等待时间
                delay = min(self.max_delay, self.base_delay * (2 ** retry_count))
                jitter = random.uniform(0, 0.1 * delay)
                sleep_time = delay + jitter
                
                print(f"等待 {sleep_time:.2f} 秒后重试...")
                time.sleep(sleep_time)
                
            except requests.exceptions.HTTPError as e:
                last_error = e
                retry_count += 1
                
                # 检查是否是504错误
                if hasattr(e, 'response') and e.response.status_code == 504:
                    print(f"Gateway Timeout (504) 错误 (第 {retry_count} 次尝试): {e}")
                    
                    if retry_count > self.max_retries:
                        break
                        
                    # 对于504错误，使用指数退避
                    delay = min(self.max_delay, self.base_delay * (2 ** retry_count))
                    jitter = random.uniform(0, 0.1 * delay)
                    sleep_time = delay + jitter
                    
                    print(f"等待 {sleep_time:.2f} 秒后重试...")
                    time.sleep(sleep_time)
                else:
                    # 其他HTTP错误不重试
                    print(f"HTTP错误 (不重试): {e}")
                    break
                    
            except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
                last_error = e
                retry_count += 1
                print(f"请求异常 (第 {retry_count} 次尝试): {e}")
                
                if retry_count > self.max_retries:
                    break
                
                # Calculate delay with exponential backoff and jitter
                delay = min(self.max_delay, self.base_delay * (2 ** (retry_count - 1)))
                jitter = random.uniform(0, 0.1 * delay)
                sleep_time = delay + jitter
                
                print(f"等待 {sleep_time:.2f} 秒后重试...")
                time.sleep(sleep_time)
        
        # 所有重试都失败了
        print(f"所有 {self.max_retries} 次重试都失败了。最后的错误: {last_error}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"最后的响应: {response.text[:500]}...")
            
        # Return a result with the original content as translation as fallback
        return "" if response_mode == 'streaming' else {}
    
    def close(self):
        """
        关闭会话连接
        """
        if hasattr(self, 'session'):
            self.session.close()
    
    def __enter__(self):
        """
        上下文管理器入口
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口，自动关闭会话
        """
        self.close()