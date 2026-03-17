#!/usr/bin/env python3
"""
AI Code Reviewer - 智能代码审查工具
分析代码并提供改进建议
"""

import ast
import sys
import os
from typing import List, Dict, Any
from colorama import init, Fore, Style

init(autoreset=True)


class CodeReviewer:
    """代码审查器"""
    
    def __init__(self):
        self.issues = []
    
    def review_file(self, filepath: str) -> List[Dict[str, Any]]:
        """审查代码文件"""
        if not os.path.exists(filepath):
            print(f"{Fore.RED}错误: 文件不存在 - {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            print(f"{Fore.CYAN}正在审查文件: {filepath}")
            print(f"{Fore.CYAN}{'='*60}")
            
            # 基础检查
            self._check_basic_style(code)
            
            # AST 分析
            try:
                tree = ast.parse(code)
                self._analyze_ast(tree)
            except SyntaxError as e:
                self.issues.append({
                    'type': 'error',
                    'severity': 'high',
                    'message': f'语法错误: {e}'
                })
            
            return self.issues
            
        except Exception as e:
            print(f"{Fore.RED}审查失败: {str(e)}")
            return []
    
    def _check_basic_style(self, code: str):
        """检查代码风格"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查行长度
            if len(line) > 120:
                self.issues.append({
                    'type': 'style',
                    'severity': 'low',
                    'line': i,
                    'message': '行长度超过 120 字符，建议拆分成多行'
                })
            
            # 检查行尾空格
            if line.rstrip() != line:
                self.issues.append({
                    'type': 'style',
                    'severity': 'low',
                    'line': i,
                    'message': '行尾存在多余空格'
                })
            
            # 检查 Tab 和空格混用
            if '\t' in line and ' ' in line:
                self.issues.append({
                    'type': 'style',
                    'severity': 'medium',
                    'line': i,
                    'message': '建议统一使用空格缩进'
                })
    
    def _analyze_ast(self, tree: ast.AST):
        """分析 AST"""
        for node in ast.walk(tree):
            # 检查 print 语句
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    self.issues.append({
                        'type': 'best_practice',
                        'severity': 'medium',
                        'line': node.lineno,
                        'message': '建议使用 logging 模块代替 print 进行日志输出'
                    })
            
            # 检查 TODO/FIXME
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    text = node.value.value.upper()
                    if 'TODO' in text or 'FIXME' in text:
                        self.issues.append({
                            'type': 'note',
                            'severity': 'low',
                            'line': node.lineno,
                            'message': f'代码中发现待办事项: {node.value.value}'
                        })
    
    def print_report(self):
        """打印审查报告"""
        if not self.issues:
            print(f"\n{Fore.GREEN}✓ 未发现问题，代码审查通过！")
            return
        
        print(f"\n{Fore.YELLOW}发现 {len(self.issues)} 个问题:\n")
        
        severity_colors = {
            'high': Fore.RED,
            'medium': Fore.YELLOW,
            'low': Fore.CYAN
        }
        
        for issue in self.issues:
            color = severity_colors.get(issue.get('severity', 'low'), Fore.WHITE)
            line = issue.get('line', '?')
            
            print(f"{color}[{issue['type']}] {issue['message']}")
            if line:
                print(f"  {Fore.GRAY}位置: 第 {line} 行")
            print()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(f"{Fore.YELLOW}使用方法: python main.py <代码文件路径>")
        print(f"示例: python main.py example.py")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    reviewer = CodeReviewer()
    issues = reviewer.review_file(filepath)
    reviewer.print_report()


if __name__ == '__main__':
    main()
