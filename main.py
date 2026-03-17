"""
AI Code Reviewer - 智能代码审查工具
自动分析代码并提供风格、潜在bug和性能优化建议
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 尝试导入可选依赖
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class CodeReviewer:
    """代码审查类"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.api_key)
    
    def analyze_code(self, code: str, language: str = "python") -> Dict[str, any]:
        """分析代码并返回审查结果"""
        results = {
            "style_issues": self._check_style(code, language),
            "potential_bugs": self._check_potential_bugs(code, language),
            "performance_tips": self._check_performance(code, language),
            "security_issues": self._check_security(code, language),
            "ai_suggestions": None
        }
        
        # 如果有API密钥，尝试使用AI增强分析
        if self.client:
            results["ai_suggestions"] = self._get_ai_suggestions(code, language)
        
        return results
    
    def _check_style(self, code: str, language: str) -> List[Dict]:
        """检查代码风格问题"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # 检查行长度
            if len(line) > 120:
                issues.append({
                    "line": i,
                    "severity": "warning",
                    "type": "line_too_long",
                    "message": f"行超过120字符 (当前: {len(line)})"
                })
            
            # 检查末尾空格
            if line.rstrip() != line:
                issues.append({
                    "line": i,
                    "severity": "info",
                    "type": "trailing_whitespace",
                    "message": "行末有多余空格"
                })
            
            # Python特定检查
            if language == "python":
                if line.startswith(' ') or line.startswith('\t'):
                    if not line.strip().startswith('#') and not line.strip().startswith('"""'):
                        if len(line) - len(line.lstrip()) % 4 != 0:
                            issues.append({
                                "line": i,
                                "severity": "warning",
                                "type": "indentation",
                                "message": "缩进应为4的倍数"
                            })
                
                # 检查import顺序
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    if i > 1:
                        prev_line = lines[i-2].strip() if i > 1 else ""
                        if prev_line and not prev_line.startswith('import') and not prev_line.startswith('from'):
                            if not any(l.strip().startswith('import') or l.strip().startswith('from') for l in lines[max(0,i-10):i-1]):
                                issues.append({
                                    "line": i,
                                    "severity": "info",
                                    "type": "import_order",
                                    "message": "import语句应放在文件顶部"
                                })
        
        return issues
    
    def _check_potential_bugs(self, code: str, language: str) -> List[Dict]:
        """检查潜在bug"""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Python特定bug检查
            if language == "python":
                # 检查可变默认参数
                if re.search(r'def\s+\w+\s*\([^)]*=\s*\[\s*\]', line) or \
                   re.search(r'def\s+\w+\s*\([^)]*=\s*\{\s*\}', line):
                    issues.append({
                        "line": i,
                        "severity": "error",
                        "type": "mutable_default_arg",
                        "message": "避免使用可变对象作为默认参数"
                    })
                
                # 检查 == None 而非 is None
                if re.search(r'==\s*None', line):
                    issues.append({
                        "line": i,
                        "severity": "warning",
                        "type": "none_comparison",
                        "message": "使用 'is None' 而非 '== None'"
                    })
                
                # 检查 except 子句没有具体异常类型
                if 'except:' in line and i < len(lines):
                    next_lines = '\n'.join(lines[i:min(i+3, len(lines))])
                    if 'except' in next_lines and 'Exception' not in next_lines and 'Error' not in next_lines:
                        issues.append({
                            "line": i,
                            "severity": "warning",
                            "type": "bare_except",
                            "message": "避免使用裸except语句，指定具体异常类型"
                        })
                
                # 检查未使用的变量
                var_match = re.search(r'^(\s*)(\w+)\s*=', line)
                if var_match and 'if' not in line and 'elif' not in line:
                    var_name = var_match.group(2)
                    if not var_name.startswith('_') and var_name.islower():
                        # 简化检查：同一行后没有使用
                        if var_name not in line[line.index('=')+1:]:
                            issues.append({
                                "line": i,
                                "severity": "info",
                                "type": "unused_variable",
                                "message": f"变量 '{var_name}' 可能未使用或拼写错误"
                            })
        
        return issues
    
    def _check_performance(self, code: str, language: str) -> List[Dict]:
        """检查性能问题"""
        issues = []
        
        # Python性能检查
        if language == "python":
            # 检查字符串拼接
            if '+' in code and "string" in code.lower():
                issues.append({
                    "line": 0,
                    "severity": "info",
                    "type": "string_concatenation",
                    "message": "使用 f-string 或 str.join() 代替 + 号拼接字符串"
                })
            
            # 检查 list comprehension vs map
            if re.search(r'list\s*\(\s*map\s*\(', code):
                issues.append({
                    "line": 0,
                    "severity": "info",
                    "type": "list_comprehension",
                    "message": "考虑使用列表推导式代替 list(map())"
                })
            
            # 检查重复的列表查找
            if code.count('.index(') > 1 or code.count('.find(') > 1:
                issues.append({
                    "line": 0,
                    "severity": "info",
                    "type": "repeated_lookup",
                    "message": "避免在循环中重复查找，可先存储结果"
                })
        
        return issues
    
    def _check_security(self, code: str, language: str) -> List[Dict]:
        """检查安全问题"""
        issues = []
        
        # 通用安全检查
        dangerous_patterns = [
            (r'eval\s*\(', '使用eval()可能造成安全风险', 'error'),
            (r'exec\s*\(', '使用exec()可能造成安全风险', 'error'),
            (r'os\.system\s*\(', '使用os.system()需谨慎验证输入', 'warning'),
            (r'subprocess\.\w+\s*\([^)]*shell\s*=\s*True', 'shell=True存在安全风险', 'error'),
            (r'password\s*=\s*["\'][^"\']+["\']', '硬编码密码存在安全风险', 'error'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', '硬编码API密钥存在安全风险', 'error'),
            (r'SQL\s', 'SQL语句需使用参数化查询防止注入', 'warning'),
        ]
        
        for pattern, message, severity in dangerous_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append({
                    "line": line_num,
                    "severity": severity,
                    "type": "security",
                    "message": message
                })
        
        return issues
    
    def _get_ai_suggestions(self, code: str, language: str) -> Optional[str]:
        """使用AI获取增强建议"""
        if not self.client:
            return None
        
        try:
            prompt = f"""你是一个专业的代码审查员。请审查以下{language}代码，提供改进建议。
重点关注：
1. 代码可读性和风格
2. 潜在的bug
3. 性能优化
4. 安全问题

代码：
```{language}
{code}
```

请用中文回复，给出具体的改进建议。"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个严格的代码审查员。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI分析出错: {str(e)}"
    
    def review_file(self, file_path: str) -> Dict[str, any]:
        """审查单个文件"""
        if not os.path.exists(file_path):
            return {"error": f"文件不存在: {file_path}"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # 根据扩展名判断语言
        ext = Path(file_path).suffix
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust'
        }
        language = language_map.get(ext, 'unknown')
        
        return self.analyze_code(code, language)
    
    def review_directory(self, dir_path: str, extensions: List[str] = None) -> Dict[str, any]:
        """审查目录下所有指定类型的文件"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java']
        
        results = {}
        for ext in extensions:
            for file_path in Path(dir_path).rglob(f'*{ext}'):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(dir_path))
                    results[relative_path] = self.review_file(str(file_path))
        
        return results


def print_review_results(results: Dict):
    """打印审查结果"""
    print("\n" + "="*60)
    print("📋 代码审查结果")
    print("="*60)
    
    total_issues = 0
    
    for category, issues in [
        ("🎨 代码风格问题", results.get("style_issues", [])),
        ("🐛 潜在Bug", results.get("potential_bugs", [])),
        ("⚡ 性能优化", results.get("performance_tips", [])),
        ("🔒 安全问题", results.get("security_issues", []))
    ]:
        if issues:
            print(f"\n{category}:")
            for issue in issues:
                total_issues += 1
                severity_icon = {
                    "error": "❌",
                    "warning": "⚠️",
                    "info": "ℹ️"
                }.get(issue.get("severity"), "•")
                
                line_info = f"第{issue['line']}行" if issue.get("line", 0) > 0 else ""
                print(f"  {severity_icon} {line_info} {issue['message']}")
    
    if total_issues == 0:
        print("\n✅ 太棒了！没有发现问题！")
    
    # 打印AI建议
    if results.get("ai_suggestions"):
        print("\n" + "-"*60)
        print("🤖 AI 智能建议:")
        print("-"*60)
        print(results["ai_suggestions"])
    
    print("\n" + "="*60)
    print(f"共发现 {total_issues} 个问题")
    print("="*60)


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              🤖 AI Code Reviewer                         ║
║              智能代码审查工具 v1.0                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 检查API配置
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ 已检测到 OpenAI API Key，将提供AI增强分析")
    else:
        print("⚠️  未设置 OPENAI_API_KEY，将仅使用静态分析")
    
    # 示例代码
    sample_code = '''
import os
from typing import List

def process_data(data=[]):
    """处理数据"""
    result = []
    for item in data:
        if item == None:
            item = "default"
        result.append(item)
    
    # 字符串拼接
    output = ""
    for r in result:
        output = output + r + ","
    
    # 安全问题
    code = eval("os.system('ls')")
    password = "hardcoded123"
    
    return output

# 裸except
try:
    x = 1/0
except:
    pass
'''
    
    print("\n📝 示例代码审查:\n")
    print(sample_code)
    
    # 创建审查器
    reviewer = CodeReviewer(api_key=api_key)
    
    # 审查示例代码
    results = reviewer.analyze_code(sample_code, "python")
    print_review_results(results)
    
    # 演示文件审查
    print("\n\n📁 文件审查示例:")
    print("使用 reviewer.review_file('your_file.py') 审查指定文件")
    print("使用 reviewer.review_directory('your_folder/') 审查整个目录")


if __name__ == "__main__":
    main()
