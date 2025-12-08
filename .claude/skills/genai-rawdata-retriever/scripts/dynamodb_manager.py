import boto3
import json
import argparse
import sys
from datetime import datetime
from botocore.exceptions import ClientError
class DynamoDBManager:
    """
    DynamoDB管理器，用于管理GitHub Insight项目的数据表

    支持的表:
    - github-insight-raw-data: 存储github_repo_analyze的数据
    - github-trend-repo-candidates: 存储github_trend_analyze的数据
    - genai-repo-watchlist: 存储项目分级结果
    """

    # 支持的表名常量
    TABLE_GITHUB_INSIGHT_RAW_DATA = 'github-insight-raw-data'
    TABLE_GITHUB_TREND_REPO_CANDIDATES = 'github-trend-repo-candidates'
    TABLE_GENAI_REPO_WATCHLIST = 'genai-repo-watchlist'

    def __init__(self, table_name='github-insight-raw-data', region_name='us-east-1'):
        """
        初始化DynamoDB管理器

        Args:
            table_name: 要操作的表名，默认为'github-insight-raw-data'
            region_name: AWS区域名称，默认为'us-east-1'
        """
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table_name = table_name
        self.region_name = region_name
        self.table = None
    
    def create_table(self):
        """
        创建DynamoDB表

        github-insight-raw-data 和 github-trend-repo-candidates 使用:
        - 分区键: project_url (String)
        - 排序键: collect_date (String)

        genai-repo-watchlist 使用:
        - 分区键: project_url (String)
        - 无排序键（每个repo只保留一条记录）

        - 计费模式: PAY_PER_REQUEST（按需付费）

        Returns:
            bool: 成功返回True（包括表已存在的情况），失败返回False
        """
        try:
            # genai-repo-watchlist 表不使用 sort key
            if self.table_name == self.TABLE_GENAI_REPO_WATCHLIST:
                key_schema = [
                    {
                        'AttributeName': 'project_url',
                        'KeyType': 'HASH'  # 分区键
                    }
                ]
                attribute_definitions = [
                    {
                        'AttributeName': 'project_url',
                        'AttributeType': 'S'  # String类型
                    }
                ]
            else:
                # 其他表使用 partition key + sort key
                key_schema = [
                    {
                        'AttributeName': 'project_url',
                        'KeyType': 'HASH'  # 分区键
                    },
                    {
                        'AttributeName': 'collect_date',
                        'KeyType': 'RANGE'  # 排序键
                    }
                ]
                attribute_definitions = [
                    {
                        'AttributeName': 'project_url',
                        'AttributeType': 'S'  # String类型
                    },
                    {
                        'AttributeName': 'collect_date',
                        'AttributeType': 'S'  # String类型
                    }
                ]

            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                BillingMode='PAY_PER_REQUEST'  # 按需付费模式
            )

            # 等待表创建完成
            print(f"正在创建表 {self.table_name}，请稍候...")
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
                print(f"创建表 {self.table_name} 时出错: {e}")
                return False
    
    def put_item(self, project_url, collect_date=None, other_attributes=None):
        """
        向表中添加项目

        Args:
            project_url: 项目URL（分区键）
            collect_date: 收集日期（排序键）- genai-repo-watchlist 表不需要此参数
            other_attributes: 其他属性字典，默认为None

        Returns:
            bool: 成功返回True，失败返回False
        """
        if not self.table:
            self.table = self.dynamodb.Table(self.table_name)

        item = {
            'project_url': project_url,
        }

        # genai-repo-watchlist 表不使用 collect_date
        if self.table_name != self.TABLE_GENAI_REPO_WATCHLIST:
            if collect_date is None:
                print(f"错误: 表 {self.table_name} 需要 collect_date 参数")
                return False
            item['collect_date'] = collect_date

        if other_attributes:
            item.update(other_attributes)

        try:
            self.table.put_item(Item=item)
            if self.table_name == self.TABLE_GENAI_REPO_WATCHLIST:
                print(f"成功添加/更新项目到表 {self.table_name}: {project_url}")
            else:
                print(f"成功添加项目到表 {self.table_name}: {project_url} (日期: {collect_date})")
            return True
        except ClientError as e:
            print(f"添加项目到表 {self.table_name} 时出错: {e}")
            return False
    
    def get_item(self, project_url, collect_date=None):
        """
        获取指定项目的数据

        Args:
            project_url: 项目URL（分区键）
            collect_date: 收集日期（排序键）- genai-repo-watchlist 表不需要此参数

        Returns:
            dict: 项目数据字典，如果不存在或出错则返回None
        """
        if not self.table:
            self.table = self.dynamodb.Table(self.table_name)

        try:
            # genai-repo-watchlist 表不使用 collect_date
            if self.table_name == self.TABLE_GENAI_REPO_WATCHLIST:
                key = {'project_url': project_url}
            else:
                if collect_date is None:
                    print(f"错误: 表 {self.table_name} 需要 collect_date 参数")
                    return None
                key = {
                    'project_url': project_url,
                    'collect_date': collect_date
                }

            response = self.table.get_item(Key=key)
            item = response.get('Item')

            if item:
                if self.table_name == self.TABLE_GENAI_REPO_WATCHLIST:
                    print(f"成功获取项目数据: {project_url}")
                else:
                    print(f"成功获取项目数据: {project_url} (日期: {collect_date})")
            else:
                if self.table_name == self.TABLE_GENAI_REPO_WATCHLIST:
                    print(f"未找到项目数据: {project_url}")
                else:
                    print(f"未找到项目数据: {project_url} (日期: {collect_date})")
            return item
        except ClientError as e:
            print(f"从表 {self.table_name} 获取项目时出错: {e}")
            return None
    
    def query_items(self, project_url, start_date=None, end_date=None):
        """
        按日期范围查询指定项目的数据

        Args:
            project_url: 项目URL（分区键）
            start_date: 开始日期（可选），格式如 '2025-01-01'
            end_date: 结束日期（可选），格式如 '2025-01-31'

        Returns:
            list: 项目数据列表，如果出错则返回空列表
        """
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
            items = response.get('Items', [])
            print(f"成功查询到 {len(items)} 条数据: {project_url}")
            return items
        except ClientError as e:
            print(f"从表 {self.table_name} 查询项目时出错: {e}")
            return []

    def scan_items(self, limit=None):
        """
        扫描表中的所有项目（注意：scan操作在大表中可能很慢且昂贵）

        Args:
            limit: 返回的最大项目数，默认返回所有项目

        Returns:
            list: 项目数据列表，如果出错则返回空列表
        """
        if not self.table:
            self.table = self.dynamodb.Table(self.table_name)

        try:
            if limit:
                response = self.table.scan(Limit=limit)
            else:
                response = self.table.scan()

            items = response.get('Items', [])

            # 处理分页（如果数据量大）
            while 'LastEvaluatedKey' in response and (limit is None or len(items) < limit):
                if limit:
                    remaining = limit - len(items)
                    response = self.table.scan(
                        ExclusiveStartKey=response['LastEvaluatedKey'],
                        Limit=remaining
                    )
                else:
                    response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))

            print(f"成功扫描到 {len(items)} 条数据")
            return items
        except ClientError as e:
            print(f"从表 {self.table_name} 扫描数据时出错: {e}")
            return []

    def delete_item(self, project_url, collect_date=None):
        """
        删除指定项目

        Args:
            project_url: 项目URL（分区键）
            collect_date: 收集日期（排序键）- genai-repo-watchlist 表不需要此参数

        Returns:
            bool: 成功返回True，失败返回False
        """
        if not self.table:
            self.table = self.dynamodb.Table(self.table_name)

        try:
            # genai-repo-watchlist 表不使用 collect_date
            if self.table_name == self.TABLE_GENAI_REPO_WATCHLIST:
                key = {'project_url': project_url}
            else:
                if collect_date is None:
                    print(f"错误: 表 {self.table_name} 需要 collect_date 参数")
                    return False
                key = {
                    'project_url': project_url,
                    'collect_date': collect_date
                }

            self.table.delete_item(Key=key)

            if self.table_name == self.TABLE_GENAI_REPO_WATCHLIST:
                print(f"成功删除项目: {project_url}")
            else:
                print(f"成功删除项目: {project_url} (日期: {collect_date})")
            return True
        except ClientError as e:
            print(f"从表 {self.table_name} 删除项目时出错: {e}")
            return False

def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(
        description='DynamoDB Manager - 管理GitHub Insight项目的数据表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 创建表
  python dynamodb_manager.py --table github-insight-raw-data create-table

  # 获取单个项目数据（使用默认表 github-insight-raw-data）
  python dynamodb_manager.py get https://github.com/vllm-project/vllm 2025-01-15

  # 获取 genai-repo-watchlist 表的数据（不需要日期）
  python dynamodb_manager.py --table genai-repo-watchlist get https://github.com/vllm-project/vllm

  # 查询历史数据（指定表，不支持 genai-repo-watchlist）
  python dynamodb_manager.py --table github-trend-repo-candidates query https://github.com/vllm-project/vllm --start 2025-01-01 --end 2025-01-07

  # 添加数据到 github-insight-raw-data
  python dynamodb_manager.py put https://github.com/vllm-project/vllm 2025-01-15 --data '{"stars": 60500}'

  # 添加/更新数据到 genai-repo-watchlist（不需要日期，会覆盖现有记录）
  python dynamodb_manager.py --table genai-repo-watchlist put https://github.com/vllm-project/vllm --data '{"priority": "high"}'

  # 扫描表数据
  python dynamodb_manager.py --table github-trend-repo-candidates scan --limit 10

  # 删除数据
  python dynamodb_manager.py delete https://github.com/vllm-project/vllm 2025-01-15

  # 删除 genai-repo-watchlist 表的数据（不需要日期）
  python dynamodb_manager.py --table genai-repo-watchlist delete https://github.com/vllm-project/vllm
        """
    )

    # 全局参数
    parser.add_argument('--table', default='github-insight-raw-data',
                       choices=['github-insight-raw-data', 'github-trend-repo-candidates', 'genai-repo-watchlist'],
                       help='表名 (默认: github-insight-raw-data)')
    parser.add_argument('--region', default='us-east-1',
                       help='AWS区域 (默认: us-east-1)')

    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # create-table 命令
    create_parser = subparsers.add_parser('create-table', help='创建DynamoDB表')

    # get 命令
    get_parser = subparsers.add_parser('get', help='获取单个项目数据')
    get_parser.add_argument('project_url', help='项目URL')
    get_parser.add_argument('collect_date', nargs='?', help='收集日期 (YYYY-MM-DD) - genai-repo-watchlist 表不需要')
    get_parser.add_argument('--json', action='store_true', help='以JSON格式输出')

    # query 命令
    query_parser = subparsers.add_parser('query', help='查询项目历史数据（不支持 genai-repo-watchlist 表）')
    query_parser.add_argument('project_url', help='项目URL')
    query_parser.add_argument('--start', help='开始日期 (YYYY-MM-DD)')
    query_parser.add_argument('--end', help='结束日期 (YYYY-MM-DD)')
    query_parser.add_argument('--json', action='store_true', help='以JSON格式输出')

    # put 命令
    put_parser = subparsers.add_parser('put', help='添加或更新项目数据')
    put_parser.add_argument('project_url', help='项目URL')
    put_parser.add_argument('collect_date', nargs='?', help='收集日期 (YYYY-MM-DD) - genai-repo-watchlist 表不需要')
    put_parser.add_argument('--data', required=True, help='JSON格式的数据')
    put_parser.add_argument('--file', help='从文件读取JSON数据')

    # scan 命令
    scan_parser = subparsers.add_parser('scan', help='扫描表中所有数据')
    scan_parser.add_argument('--limit', type=int, help='限制返回的数据条数')
    scan_parser.add_argument('--json', action='store_true', help='以JSON格式输出')

    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除项目数据')
    delete_parser.add_argument('project_url', help='项目URL')
    delete_parser.add_argument('collect_date', nargs='?', help='收集日期 (YYYY-MM-DD) - genai-repo-watchlist 表不需要')
    delete_parser.add_argument('--confirm', action='store_true', help='跳过确认提示')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 创建管理器实例
    manager = DynamoDBManager(table_name=args.table, region_name=args.region)

    try:
        # 执行命令
        if args.command == 'create-table':
            success = manager.create_table()
            sys.exit(0 if success else 1)

        elif args.command == 'get':
            data = manager.get_item(args.project_url, args.collect_date)
            if data:
                if args.json:
                    print(json.dumps(data, indent=2, default=str))
                else:
                    print(f"\n项目: {args.project_url}")
                    print(f"日期: {args.collect_date}")
                    print("\n数据:")
                    print(json.dumps(data, indent=2, default=str))
                sys.exit(0)
            else:
                sys.exit(1)

        elif args.command == 'query':
            # genai-repo-watchlist 表不支持 query 操作
            if args.table == 'genai-repo-watchlist':
                print(f"错误: genai-repo-watchlist 表不支持 query 操作")
                print(f"提示: 使用 'get' 命令获取单个项目数据，或使用 'scan' 命令浏览所有数据")
                sys.exit(1)

            items = manager.query_items(args.project_url, args.start, args.end)
            if args.json:
                print(json.dumps(items, indent=2, default=str))
            else:
                print(f"\n查询结果: {len(items)} 条数据")
                for item in items:
                    print(f"\n日期: {item.get('collect_date')}")
                    print(json.dumps(item, indent=2, default=str))
            sys.exit(0)

        elif args.command == 'put':
            # 读取数据
            if args.file:
                with open(args.file, 'r') as f:
                    other_attributes = json.load(f)
            else:
                other_attributes = json.loads(args.data)

            success = manager.put_item(args.project_url, args.collect_date, other_attributes)
            sys.exit(0 if success else 1)

        elif args.command == 'scan':
            items = manager.scan_items(limit=args.limit)
            if args.json:
                print(json.dumps(items, indent=2, default=str))
            else:
                print(f"\n扫描结果: {len(items)} 条数据")
                for item in items:
                    print(f"\n项目: {item.get('project_url')}")
                    print(f"日期: {item.get('collect_date')}")
                    print(json.dumps(item, indent=2, default=str))
            sys.exit(0)

        elif args.command == 'delete':
            if not args.confirm:
                if args.table == 'genai-repo-watchlist':
                    response = input(f"确认删除 {args.project_url}? [y/N]: ")
                else:
                    response = input(f"确认删除 {args.project_url} (日期: {args.collect_date})? [y/N]: ")
                if response.lower() != 'y':
                    print("操作已取消")
                    sys.exit(0)

            success = manager.delete_item(args.project_url, args.collect_date)
            sys.exit(0 if success else 1)

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()