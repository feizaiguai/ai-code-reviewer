"""
AI Code Reviewer - 自动代码审查工具
作者: 196408245@qq.com
功能: 分析代码并给出 review 建议（代码风格、潜在bug、性能优化）
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ReviewIssue:
    """代码问题"""
    severity: str  # high, medium, low
    category: str  # style, bug, performance, security
    line: int
    message: str
    suggestion: str


@dataclass
class ReviewResult:
    """审查结果"""
    file_path: str
    total_lines: int
    issues: List[ReviewIssue]
    summary: Dict[str, int]


class CodeStyleChecker:
    """代码风格检查器"""
    
    def check(self, code: str, filepath: str) -> List[ReviewIssue]:
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查行长度
            if len(line) > 120:
                issues.append(ReviewIssue(
                    severity="low",
                    category="style",
                    line=i,
                    message=f"行过长 ({len(line)} 字符)",
                    suggestion="建议将单行控制在 120 字符以内"
                ))
            
            # 检查缩进（应使用 4 空格）
            if line.startswith(' ' * 1) or line.startswith(' ' * 2):
                if '\t' not in line and line.strip():
                    pass  # 允许 2 空格缩进
            
            # 检查行尾空格
            if line.rstrip() != line:
                issues.append(ReviewIssue(
                    severity="low",
                    category="style",
                    line=i,
                    message="行尾存在多余空格",
                    suggestion="删除行尾空格"
                ))
            
            # 检查 TODO/FIXME 注释
            if re.search(r'(TODO|FIXME|HACK|XXX):?', line, re.IGNORECASE):
                issues.append(ReviewIssue(
                    severity="medium",
                    category="style",
                    line=i,
                    message="存在未完成的 TODO/FIXME 注释",
                    suggestion="尽快完成或创建 Issue 跟踪"
                ))
        
        return issues


class BugDetector:
    """潜在 Bug 检测器"""
    
    def check(self, code: str, filepath: str) -> List[ReviewIssue]:
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检测 == 与 = 混用
            if re.search(r'if\s+\w+\s*==\s*\w+\s*==', line):
                issues.append(ReviewIssue(
                    severity="high",
                    category="bug",
                    line=i,
                    message="可能的赋值错误: 连续使用 ==",
                    suggestion="检查是否应为单独的比较"
                ))
            
            # 检测 except pass
            if re.search(r'except.*:\s*$', line) or 'except:\n' in code[max(0, code.find(line)-50):code.find(line)+len(line)+10]:
                if i < len(lines) and lines[i].strip() == 'pass':
                    issues.append(ReviewIssue(
                        severity="high",
                        category="bug",
                        line=i,
                        message="检测到空的 except 块",
                        suggestion="至少记录日志或重新抛出异常"
                    ))
            
            # 检测未使用的变量
            if re.match(r'^\s*_\w*\s*=', line) or re.match(r'^\s*[^_\s]\w*\s*=\s*[^=]', line):
                var_match = re.match(r'^\s*(\w+)\s*=', line)
                if var_match and var_match.group(1) in ['temp', 'tmp', 'unused']:
                    issues.append(ReviewIssue(
                        severity="low",
                        category="bug",
                        line=i,
                        message=f"变量名 '{var_match.group(1)}' 可能未使用",
                        suggestion="使用 _ 前缀标记为有意未使用的变量"
                    ))
            
            # 检测硬编码的字符串拼接
            if "' '" in line or '" "' in line:
                issues.append(ReviewIssue(
                    severity="medium",
                    category="bug",
                    line=i,
                    message="可能使用了字符串拼接而非格式化",
                    suggestion="使用 f-string、format() 或 join() 方法"
                ))
        
        return issues


class PerformanceAnalyzer:
    """性能分析器"""
    
    def check(self, code: str, filepath: str) -> List[ReviewIssue]:
        issues = []
        
        # 检测字符串拼接在循环中
        if re.search(r'for\s+.*:\s*\n\s*.*\+\=', code) and '+ "' in code:
            issues.append(ReviewIssue(
                severity="medium",
                category="performance",
                line=0,
                message="检测到循环中的字符串拼接",
                suggestion="使用 list + join() 或列表推导式替代"
            ))
        
        # 检测重复计算
        patterns = [
            (r'len\([^)]+\)\s+in\s+', '在条件中重复计算长度'),
            (r'\.append\([^)]+\)\s*\n\s*for', '考虑使用列表推导式'),
        ]
        
        for pattern, msg in patterns:
            if re.search(pattern, code):
                issues.append(ReviewIssue(
                    severity="medium",
                    category="performance",
                    line=0,
                    message=msg,
                    suggestion="优化以提高性能"
                ))
        
        # 检测可迭代对象的重复迭代
        if code.count('.append') > 3 and 'for' in code:
            issues.append(ReviewIssue(
                severity="low",
                category="performance",
                line=0,
                message="多次 append 操作",
                suggestion="考虑使用列表推导式一次性生成"
            ))
        
        return issues


class PythonAnalyzer:
    """Python AST 深度分析"""
    
    def check(self, code: str, filepath: str) -> List[ReviewIssue]:
        issues = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # 检测嵌套过深
                if isinstance(node, (ast.If, ast.For, ast.While)):
                    depth = self._get_nesting_depth(node)
                    if depth > 4:
                        issues.append(ReviewIssue(
                            severity="medium",
                            category="style",
                            line=node.lineno,
                            message=f"嵌套深度过深 ({depth}层)",
                            suggestion="考虑重构以提高可读性，使用函数提取或合并条件"
                        ))
                
                # 检测过长函数
                if isinstance(node, ast.FunctionDef):
                    end_line = node.end_lineno or 0
                    start_line = node.lineno
                    func_length = end_line - start_line
                    
                    if func_length > 100:
                        issues.append(ReviewIssue(
                            severity="medium",
                            category="style",
                            line=node.lineno,
                            message=f"函数 '{node.name}' 过长 ({func_length} 行)",
                            suggestion="考虑拆分为更小的函数，每个函数不超过 100 行"
                        ))
                
                # 检测过短变量名
                if isinstance(node, ast.Name) and len(node.id) == 1:
                    issues.append(ReviewIssue(
                        severity="low",
                        category="style",
                        line=node.lineno,
                        message=f"变量名 '{node.id}' 过短",
                        suggestion="使用更有意义的变量名"
                    ))
        except SyntaxError:
            pass
        
        return issues
    
    def _get_nesting_depth(self, node) -> int:
        depth = 0
        current = node
        while hasattr(current, 'parent'):
            if isinstance(current.parent, (ast.If, ast.For, ast.While, ast.With)):
                depth += 1
            current = current.parent
        return depth


class AICodeReviewer:
    """AI 代码审查主类"""
    
    def __init__(self):
        self.style_checker = CodeStyleChecker()
        self.bug_detector = BugDetector()
        self.performance_analyzer = PerformanceAnalyzer()
        self.python_analyzer = PythonAnalyzer()
    
    def review_file(self, filepath: str) -> ReviewResult:
        """审查单个文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            print(f"读取文件失败: {filepath} - {e}")
            return None
        
        issues = []
        issues.extend(self.style_checker.check(code, filepath))
        issues.extend(self.bug_detector.check(code, filepath))
        issues.extend(self.performance_analyzer.check(code, filepath))
        
        if filepath.endswith('.py'):
            issues.extend(self.python_analyzer.check(code, filepath))
        
        # 统计
        summary = {
            'high': sum(1 for i in issues if i.severity == 'high'),
            'medium': sum(1 for i in issues if i.severity == 'medium'),
            'low': sum(1 for i in issues if i.severity == 'low'),
            'total': len(issues)
        }
        
        return ReviewResult(
            file_path=filepath,
            total_lines=len(code.split('\n')),
            issues=issues,
            summary=summary
        )
    
    def review_directory(self, dirpath: str, extensions: List[str] = None) -> List[ReviewResult]:
        """审查目录下的所有文件"""
        if extensions is None:
            extensions = ['.py', '.js', '.java', '.go', '.rs']
        
        results = []
        for ext in extensions:
            for filepath in Path(dirpath).rglob(f'*{ext}'):
                result = self.review_file(str(filepath))
                if result:
                    results.append(result)
        
        return results
    
    def print_report(self, result: ReviewResult):
        """打印审查报告"""
        print("\n" + "="*60)
        print(f"📄 文件: {result.file_path}")
        print(f"📊 总行数: {result.total_lines}")
        print(f"⚠️  问题数: {result.summary['total']}")
        print(f"   🔴 高危: {result.summary['high']}  |  🟡 中危: {result.summary['medium']}  |  🟢 低危: {result.summary['low']}")
        print("="*60)
        
        if result.issues:
            # 按严重程度排序
            severity_order = {'high': 0, 'medium': 1, 'low': 2}
            sorted_issues = sorted(result.issues, key=lambda x: severity_order.get(x.severity, 3))
            
            for issue in sorted_issues:
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(issue.severity, '⚪')
                category_icon = {'style': '📝', 'bug': '🐛', 'performance': '⚡', 'security': '🔒'}.get(issue.category, '📌')
                
                line_info = f"第 {issue.line} 行" if issue.line > 0 else "全局"
                print(f"\n{severity_icon} {category_icon} [{issue.severity.upper()}] {line_info}")
                print(f"   问题: {issue.message}")
                print(f"   建议: {issue.suggestion}")
        
        print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Code Reviewer - 智能代码审查工具')
    parser.add_argument('path', nargs='?', help='文件或目录路径')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归审查目录')
    parser.add_argument('-e', '--extensions', nargs='+', default=['.py'], help='要审查的文件扩展名')
    parser.add_argument('-o', '--output', help='输出报告到文件 (JSON格式)')
    parser.add_argument('--no-color', action='store_true', help='禁用彩色输出')
    
    args = parser.parse_args()
    
    reviewer = AICodeReviewer()
    
    if not args.path:
        # 演示模式
        print("\n🎯 AI Code Reviewer - 演示模式\n")
        demo_code = '''
import os

def process_data(data, tmp):
    result = ""
    for item in data:
        result += item
    return result

def example():
    x = 5
    if x == 10 == 20:
        pass
    return x

class MyClass:
    def __init__(self):
        self.value = 1
    
    def compute(self, data=[]):
        for i in data:
            print(i)
        return self.value
'''
        
        # 写入临时文件进行演示
        demo_file = 'demo_code.py'
        with open(demo_file, 'w', encoding='utf-8') as f:
            f.write(demo_code)
        
        result = reviewer.review_file(demo_file)
        reviewer.print_report(result)
        
        # 清理
        os.remove(demo_file)
        
        print("\n💡 使用方法:")
        print("   python main.py <文件路径>")
        print("   python main.py <目录路径> -r")
        print("   python main.py . -r -e .py .js")
        
    else:
        path = Path(args.path)
        
        if path.is_file():
            result = reviewer.review_file(str(path))
            if result:
                reviewer.print_report(result)
                
                if args.output:
                    with open(args.output, 'w', encoding='utf-8') as f:
                        json.dump({
                            'file_path': result.file_path,
                            'total_lines': result.total_lines,
                            'summary': result.summary,
                            'issues': [asdict(issue) for issue in result.issues]
                        }, f, indent=2, ensure_ascii=False)
                    print(f"\n📄 报告已保存到: {args.output}")
        
        elif path.is_dir():
            results = reviewer.review_directory(str(path), args.extensions)
            
            for result in results:
                reviewer.print_report(result)
            
            # 汇总统计
            total_issues = sum(r.summary['total'] for r in results)
            if total_issues > 0:
                print("\n" + "="*60)
                print(f"📊 汇总: 审查了 {len(results)} 个文件，共发现 {total_issues} 个问题")
                print("="*60)
            
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump([{
                        'file_path': r.file_path,
                        'total_lines': r.total_lines,
                        'summary': r.summary,
                        'issues': [asdict(issue) for issue in r.issues]
                    } for r in results], f, indent=2, ensure_ascii=False)
                print(f"\n📄 报告已保存到: {args.output}")


if __name__ == '__main__':
    main()
