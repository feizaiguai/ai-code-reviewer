# AI Code Reviewer

一个智能 Python 代码审查工具，自动分析代码并给出 review 建议。

## 功能特性

- 🔍 **代码风格检查** - 行长度、缩进、TODO 注释等
- 🐛 **潜在 Bug 检测** - 语法错误模式、异常处理问题、变量使用等
- ⚡ **性能优化建议** - 字符串拼接、循环优化等
- 📊 **详细报告** - 按严重程度分类，支持 JSON 输出

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 审查单个文件

```bash
python main.py your_code.py
```

### 审查目录（递归）

```bash
python main.py ./src -r
```

### 指定文件类型

```bash
python main.py ./project -r -e .py .js .java
```

### 输出 JSON 报告

```bash
python main.py ./src -r -o report.json
```

### 演示模式

直接运行查看示例：

```bash
python main.py
```

## 输出示例

```
============================================================
📄 文件: example.py
📊 总行数: 25
⚠️  问题数: 3
   🔴 高危: 1  |  🟡 中危: 1  |  🟢 低危: 1
============================================================

🔴 🐛 [HIGH] 第 12 行
   问题: 可能的赋值错误: 连续使用 ==
   建议: 检查是否应为单独的比较

🟡 ⚡ [MEDIUM] 全局
   问题: 检测到循环中的字符串拼接
   建议: 使用 list + join() 或列表推导式替代

🟢 📝 [LOW] 第 5 行
   问题: 变量名 'tmp' 可能未使用
   建议: 使用 _ 前缀标记为有意未使用的变量
```

## 项目结构

```
ai-code-reviewer/
├── main.py              # 核心代码
├── README.md            # 项目说明
└── requirements.txt     # 依赖列表
```

## 检查项

### 代码风格
- 行长度限制（>120 字符警告）
- 行尾空格
- TODO/FIXME 注释
- 嵌套深度
- 函数长度

### 潜在 Bug
- `==` 与 `=` 混用
- 空的 except 块
- 变量命名问题
- 字符串拼接方式

### 性能优化
- 循环中的字符串拼接
- 重复计算
- 多次 append 操作

## 依赖

- Python 3.8+

## 作者

- 邮箱: 196408245@qq.com

## 许可证

MIT License
