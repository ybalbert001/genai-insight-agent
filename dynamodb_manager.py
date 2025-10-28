import boto3
from datetime import datetime
from botocore.exceptions import ClientError
class DynamoDBManager:
    def __init__(self, region_name='us-east-1'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table_name = 'github-insight-raw-data'  # 修改为您的表名
        self.table = None
    
    def create_table(self):
        """创建DynamoDB表"""
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'project_url',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'collect_date',
                        'KeyType': 'RANGE'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'project_url',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'collect_date',
                        'AttributeType': 'S'
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # 等待表创建完成
            table.wait_until_exists()
            self.table = table
            print(f"表 {self.table_name} 创建成功！")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"表 {self.table_name} 已存在，使用现有表")
                self.table = self.dynamodb.Table(self.table_name)
                return True
            else:
                print(f"创建表时出错: {e}")
                return False
    
    def put_item(self, project_url, collect_date, other_attributes):
        """向表中添加项目"""
        if not self.table:
            self.table = self.dynamodb.Table(self.table_name)
        
        item = {
            'project_url': project_url,
            'collect_date': collect_date,
        }
        item.update(other_attributes)

        import pdb 
        pdb.set_trace()
        
        try:
            self.table.put_item(Item=item)
            print(f"成功添加项目: {project_url}")
        except ClientError as e:
            print(f"添加项目时出错: {e}")
    
    def get_item(self, project_url, collect_date):
        """获取指定项目"""
        if not self.table:
            self.table = self.dynamodb.Table(self.table_name)
        
        try:
            response = self.table.get_item(
                Key={
                    'project_url': project_url,
                    'collect_date': collect_date
                }
            )
            return response.get('Item')
        except ClientError as e:
            print(f"获取项目时出错: {e}")
            return None
    
    def query_items(self, project_url, start_date=None, end_date=None):
        """范围查询指定项目的数据"""
        if not self.table:
            self.table = self.dynamodb.Table(self.table_name)
        
        try:
            key_condition = boto3.dynamodb.conditions.Key('project_url').eq(project_url)
            
            if start_date and end_date:
                key_condition = key_condition & boto3.dynamodb.conditions.Key('collect_date').between(start_date, end_date)
            elif start_date:
                key_condition = key_condition & boto3.dynamodb.conditions.Key('collect_date').gte(start_date)
            elif end_date:
                key_condition = key_condition & boto3.dynamodb.conditions.Key('collect_date').lte(end_date)
            
            response = self.table.query(KeyConditionExpression=key_condition)
            return response.get('Items', [])
        except ClientError as e:
            print(f"查询项目时出错: {e}")
            return []
# 使用示例
if __name__ == "__main__":
    # 创建管理器实例
    db_manager = DynamoDBManager()
    
    # 创建表
    db_manager.create_table()

    data = { "static_info": { "description": "Easy, fast, and cheap LLM serving for everyone", "tags": "llm,inference,serving,pytorch,machine-learning,ai" }, "metric_info": { "stars": 60500, "forks": 10700, "open_pr_count": 1164, "merged_pr_count": 0, "open_issue_count": 1836, "closed_issue_count": 9591 }, "pr_list": [ "https://github.com/vllm-project/vllm/pull/22456", "https://github.com/vllm-project/vllm/pull/27121", "https://github.com/vllm-project/vllm/pull/27139", "https://github.com/vllm-project/vllm/pull/27150", "https://github.com/vllm-project/vllm/pull/27111", "https://github.com/vllm-project/vllm/pull/27130", "https://github.com/vllm-project/vllm/pull/27149", "https://github.com/vllm-project/vllm/pull/26908", "https://github.com/vllm-project/vllm/pull/27106", "https://github.com/vllm-project/vllm/pull/26587", "https://github.com/vllm-project/vllm/pull/27035", "https://github.com/vllm-project/vllm/pull/27127", "https://github.com/vllm-project/vllm/pull/27143", "https://github.com/vllm-project/vllm/pull/26074", "https://github.com/vllm-project/vllm/pull/27135", "https://github.com/vllm-project/vllm/pull/27122", "https://github.com/vllm-project/vllm/pull/25515", "https://github.com/vllm-project/vllm/pull/26663", "https://github.com/vllm-project/vllm/pull/25398" ], "crucial_change": { "README_Change": "", "release_Change": "" }, "pr_insight_list": [ { "type": "Feat", "importance": "Medium", "meaning": "为vLLM项目添加了插件系统支持，允许用户通过Python entry-points机制注册自定义的StatLoggerBase实现，使用户能够在不修改内部代码的情况下向vLLM运行时注入自定义的指标日志记录器。这个功能通过vllm.stat_logger_plugins插件组实现，包含了完整的测试用例和文档更新，增强了vLLM的可扩展性和可观测性能力。" }, { "type": "FixBug", "importance": "High", "meaning": "针对DeepSeek V3.2模型禁用FP8 KV缓存默认设置，解决在FULL_AND_PIECEWISE CUDA图模式下的精度问题和分布式并行（DP/EP）配置中的FlashMLA错误。这是一个临时性修复，直到FP8 KV缓存功能稳定化完成。该修改将FP8 KV缓存从默认启用改为可选启用，确保DeepSeek V3.2模型的稳定运行。" }, { "type": "FixBug", "importance": "Medium", "meaning": "这是一个针对PyTorch 2.9的monkey patch修复，解决了图分区签名相关的bug。主要修复了test_attn_quant测试失败的问题，该问题与Inductor分区代码生成和注意力机制+nvfp4量化融合有关。修复包括两个方面：1) 在vllm/env_override.py中添加了get_graph_partition_signature的monkey patch来回移PyTorch的修复；2) 更新了测试文件中的日志基础设施，从caplog_mp_spawn改为caplog_vllm以适配dynamo图分区的需求。这个修复对于vllm项目升级到PyTorch 2.9版本的兼容性至关重要。" }, { "type": "Refactor", "importance": "Minor", "meaning": "将vllm.utils中的性能分析工具(cprofile和cprofile_context函数)重构到新的vllm.utils.profiling模块中，提高代码组织结构。同时保持向后兼容性，通过__getattr__机制为旧的导入路径提供弃用警告，并更新了相关文档。这是一个代码组织优化的重构，不影响功能但改善了项目结构的清晰度。" }, { "type": "FixBug", "importance": "Medium", "meaning": "修复了Gemma-3-1b-it模型的测试失败问题。通过更新Flash Attention依赖版本，解决了test_lm_eval_accuracy_v1_engine测试用例的失败，确保了该模型在vLLM中的正确性验证。这是一个重要的模型兼容性修复，涉及到Flash Attention组件的更新。" }, { "type": "Docs", "importance": "Minor", "meaning": "这是一个文档改进的PR，为之前的两个PR (#26737和#26961)添加了澄清性注释。主要在shm_broadcast.py和output.py文件中添加了代码注释，解释了共享内存缓冲区大小的设计理由以及消息队列操作顺序的逻辑。这些注释提高了代码的可读性和可维护性，帮助开发者更好地理解代码背后的设计决策。" }, { "type": "FixBug", "importance": "Medium", "meaning": "修复了barrier超时异常中字符串格式化错误的bug。原代码使用printf风格的字符串格式化参数传递给RuntimeError构造函数，但Python异常构造函数不会自动插值这些参数，导致异常消息显示为未格式化的元组，影响错误信息的可读性。通过改用f-string格式化字符串，确保超时值能正确显示为格式化的秒数，提升了错误消息的可读性和代码的健壮性。" }, { "type": "Chore", "importance": "Medium", "meaning": "这是一个代码重构PR，将vllm.utils模块中的PyTorch相关辅助函数分离到单独的文件中。主要目的是清理和重组代码结构，提高代码的模块化和可维护性。PR涉及119个文件的修改，新增772行代码，删除714行代码，包括移动STR_DTYPE_TO_TORCH_DTYPE、kv_caches工具函数、CUDA相关函数、张量操作函数等到新的torch_utils.py文件中。这种重构有助于更好地组织代码，使PyTorch相关功能更加集中和易于管理，是vllm项目代码清理工作的一部分。" }, { "type": "Perf", "importance": "Minor", "meaning": "在QwenVL模型的注意力模块中移除了不必要的.contiguous()调用，通过基准测试验证了这一优化在xformers和flash attention后端下都能正常工作，并带来了轻微的性能提升（输出token吞吐量从1051.90 tok/s提升到1060.55 tok/s，TTFT从44047.03ms降低到43825.06ms）。这是一个代码优化改进，移除了冗余的内存连续化操作，提高了推理效率。" }, { "type": "Refactor", "importance": "Medium", "meaning": "重构注意力层的KV缓存规范获取机制，将get_kv_cache_spec方法添加到AttentionLayerBase基类中。这样不同的注意力层可以定义自己的KV缓存规范，使模型运行器无需处理不同注意力类型和模型特定的hack代码（如DSv32 Indexer）。通过方法分发系统简化了ENCODER、ENCODER_ONLY和ENCODER_DECODER类型的管理，提高了代码的可维护性和扩展性。" }, { "type": "FixBug", "importance": "High", "meaning": "修复CPU注意力后端中预填充注意力的关键bug。主要解决了：1) 在混合预填充/解码请求中Q/K/V张量索引计算错误的问题；2) 禁用了在某些CPU架构上不支持的前缀缓存功能；3) 确保批处理和单独运行提示时输出结果一致性。这个修复对于CPU推理的正确性至关重要，特别是在处理批量请求时。" }, { "type": "Feat", "importance": "High", "meaning": "为vLLM项目添加对DeepGEMM和Blackwell架构的支持，这是一个重要的功能增强，扩展了vLLM在最新GPU架构上的兼容性和性能优化能力。该PR修改了FP8量化层的实现，通过环境变量VLLM_USE_DEEP_GEMM启用DeepGEMM功能，并在B200硬件上通过了测试验证，对于支持新一代NVIDIA GPU架构具有重要意义。" }, { "type": "Refactor", "importance": "Medium", "meaning": "将vllm.utils模块中的内存相关工具函数重构分离到专门的子模块中，包括创建vllm.utils.mem_constants存放内存常量（MB_bytes, GiB_bytes等）和vllm.utils.mem_utils存放内存工具函数（get_cpu_memory, DeviceMemoryProfiler等）。这是#26900大型重构工作的一部分，旨在改善代码组织结构和模块化程度，使内存相关功能更加清晰分离，便于维护和使用。虽然主要是代码移动和导入路径更新，但对提升项目架构质量具有重要意义。" }, { "type": "Test", "importance": "Medium", "meaning": "为 /health 端点添加自动化测试，验证当引擎死亡时正确返回 503 状态码。这是对 #24897 修复的回归测试，确保健康检查端点在引擎故障时的行为符合预期，提高了代码覆盖率并防止未来的功能回归。测试使用 mock 技术模拟 EngineDeadError 异常，验证端点返回正确的 HTTP 503 状态而不是 500 错误。" }, { "type": "Docs", "importance": "Medium", "meaning": "更新了CPU功能兼容性文档，将推测解码(Speculative Decoding)在CPU上的支持状态从支持(✅)更改为不支持(❌)，确保文档与v1版本的实际功能实现保持一致" }, { "type": "Feat", "importance": "Medium", "meaning": "更新DeepEP依赖到最新版本(commit 73b6ea4)，新增对hidden_size=3072的支持，这对于gpt-oss低延迟数据并行/专家并行场景很有用。同时优化了性能敏感路径中的成员检查，将列表改为frozenset以提升查找效率。" }, { "type": "Feat", "importance": "High", "meaning": "为GPT-OSS工具调用添加结构化标签支持，通过约束模型输出来解决Chain of Thought推理中的两个关键问题：1）防止模型在未提供工具服务器时生成函数调用；2）确保模型只生成工具服务器中实际存在的函数。这是一个重要的功能增强，提高了工具调用的准确性和可靠性，减少了无效的推理轮次，但代码审查中发现了全局字典变异和日志语句的严重bug需要修复。" }, { "type": "Test", "importance": "Medium", "meaning": "修复v1版本注意力机制后端正确性测试中的KV缓存布局问题。原本测试假设KV缓存的维度布局为(num_blocks, 2, ...)，但在H100上运行时出现解包错误。此PR通过修改测试代码，为Triton注意力后端提供正确的(num_blocks, 2, ...)KV缓存布局，使其与FlashInfer后端保持一致，确保15个注意力后端测试能够在H100上正常通过。这是为了支持即将启用的CI测试而进行的必要修复。" }, { "type": "Perf", "importance": "Medium", "meaning": "为NVIDIA H100 PCIe GPU优化FP8 MoE模型的融合MoE内核配置，通过调整参数从E=128,N=384改为E=64,N=768并支持FP8 dtype，在Qwen3-30B-A3B-FP8模型上实现了1.6-2.9%的吞吐量提升和约2%的延迟降低。这是一个针对特定硬件和模型类型的性能优化配置文件添加。" } ] }
    
    # 添加示例数据
    db_manager.put_item(
        project_url='https://github.com/vllm-project/vllm',
        collect_date='2025-10-17',
        other_attributes = data
    )

    # data=db_manager.get_item(
    #     project_url='https://github.com/vllm-project/vllm',
    #     collect_date='2025-10-18'
    # )

    print(data)