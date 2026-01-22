"""
使用增强解析器获取竞彩网数据
"""
import asyncio
from backend.scrapers.enhanced_parser import enhanced_parser


def use_enhanced_parser():
    """使用增强解析器"""
    print("使用增强解析器...")
    # 示例用法
    result = enhanced_parser.parse_html("<html><body>test</body></html>")
    print(f"解析结果: {result}")
    return result


if __name__ == "__main__":
    use_enhanced_parser()
