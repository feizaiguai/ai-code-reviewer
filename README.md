# AI Code Reviewer

🤖 智能代码审查工具 - 自动分析代码并提供风格、潜在bug和性能优化建议

## 功能特性

- **代码风格检查**: 检查行长度、缩进、import顺序等
- **潜在Bug检测**: 检测可变默认参数、None比较、裸except等常见问题
- **性能优化建议**: 提供字符串拼接、列表推导等优化建议
- **安全漏洞扫描**: 检测eval、exec、硬编码密码等安全风险
- **AI增强分析**: 支持OpenAI API，提供智能代码改进建议

## 安装

```bash
pip install -r requirements.txt
```

## 配置

### 环境变量

设置OpenAI API Key以启用AI增强分析：

```bash
# Linux/Mac
export OPENAI_API_KEY=your_api_key_here

# Windows (CMD)
set OPENAI_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your_api_key_here"
```

## 使用方法

### Python 代码

```python
from main import CodeReviewer

# 创建审查器
reviewer = CodeReviewer()

# 分析代码
code = """
def hello():
    print("Hello World")
"""
results = reviewer.analyze_code(code, "python")
print(results)
```

### 命令行使用

```python
# 在 main.py 中添加命令行接口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        reviewer = CodeReviewer()
        results = reviewer.review_file(file_path)
        print_review_results(results)
    else:
        main()
```

运行:
```bash
python main.py your_file.py
```

### 审查目录

```python
from main import CodeReviewer

reviewer = CodeReviewer()
results = reviewer.review_directory("your_project_folder/")
```

## 输出示例

```
============================================================
📋 代码审查结果
============================================================

🎨 代码风格问题:
  ⚠️ 第15行 行超过120字符 (当前: 145)

🐛 潜在Bug:
  ❌ 第3行 避免使用可变对象作为默认参数
  ⚠️ 第12行 使用 'is None' 而非 '== None'

⚡ 性能优化:
  ℹ️  使用 f-string 或 str.join() 代替 + 号拼接字符串

🔒 安全问题:
  ❌ 第25行 使用eval()可能造成安全风险
  ❌ 第26行 硬编码密码存在安全风险

============================================================
共发现 5 个问题
============================================================
```

## 支持的语言

- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Java (.java)
- C/C++ (.c, .cpp)
- Go (.go)
- Rust (.rs)

## 检查项目

### 代码风格
- 行长度限制 (默认120字符)
- 末尾空格检测
- 缩进规范性 (Python)
- import语句顺序

### 潜在Bug
- 可变默认参数
- None比较方式
- 裸except语句
- 未使用变量

### 性能优化
- 字符串拼接方式
- 列表推导式 vs map()
- 重复查找优化

### 安全问题
- eval/exec 使用
- os.system 调用
- shell=True 风险
- 硬编码密码/API Key
- SQL注入风险

## 许可证

MIT License

## 作者

196408245@qq.com
