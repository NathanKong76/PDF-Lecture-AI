# 新前端模块使用指南

## 📖 概述

本指南说明如何使用优化后的模块化前端组件。所有新组件位于 `app/ui/` 目录下。

---

## 🏗️ 架构概览

```
app/ui/
├── layout.py              # 页面布局管理
├── sidebar.py             # 侧边栏配置
├── components/            # 可重用组件
│   ├── progress_tracker.py
│   ├── error_handler.py
│   ├── file_uploader.py
│   └── results_display.py
├── handlers/              # 业务逻辑
│   ├── file_handler.py
│   ├── batch_handler.py
│   └── download_handler.py
└── performance/           # 性能优化
    ├── cache_manager.py
    └── async_processor.py
```

---

## 🚀 快速开始

### 1. 基础页面布局

```python
from app.ui.layout import PageLayout

# 创建布局
layout = PageLayout(
    page_title="我的应用",
    layout="wide"
)

# 设置页面
layout.setup()

# 渲染头部
layout.render_header("这是一个示例应用")

# 创建列
col1, col2 = layout.create_columns(2)

with col1:
    st.write("左侧内容")

with col2:
    st.write("右侧内容")
```

### 2. 侧边栏配置

```python
from app.ui.sidebar import SidebarForm

# 创建侧边栏
sidebar = SidebarForm()

# 渲染并获取参数
params = sidebar.render()

# 使用参数
api_key = params["api_key"]
model_name = params["model_name"]
```

### 3. 文件上传

```python
from app.ui.components import FileUploader

# 创建上传器
uploader = FileUploader(
    label="上传PDF文件",
    max_files=20,
    max_file_size_mb=50
)

# 渲染上传器
files = uploader.render()

# 获取文件信息
if files:
    for file in files:
        st.write(f"文件: {file.name}, 大小: {file.size} bytes")
```

### 4. 进度追踪

```python
from app.ui.components import ProgressTracker

# 创建进度追踪器
tracker = ProgressTracker(total_items=10, operation_name="处理中")

# 更新进度
for i in range(10):
    # 模拟处理
    time.sleep(0.5)

    # 更新进度
    tracker.update(i, "正在处理", "completed")

    # 渲染进度（可选）
    # tracker.render()
```

### 5. 错误处理

```python
from app.ui.components import ErrorHandler

# 创建错误处理器
error_handler = ErrorHandler()

# 处理错误
try:
    # 可能会失败的代码
    result = risky_operation()
except Exception as e:
    error_handler.handle_error(
        error=e,
        context="操作失败",
        on_retry=lambda: risky_operation()
    )
```

### 6. 批量处理

```python
from app.ui.handlers import BatchHandler

# 创建批量处理器
batch_handler = BatchHandler(max_workers=5)

# 处理文件
def process_file_func(file):
    # 处理单个文件的逻辑
    return {"status": "success", "data": "..."}

results = batch_handler.process_batch(
    files=uploaded_files,
    params=params,
    on_progress=lambda i, name: st.write(f"处理 {i}: {name}")
)
```

### 7. 结果展示

```python
from app.ui.components import ResultsDisplay

# 创建结果展示器
results_display = ResultsDisplay()

# 渲染结果
results_display.render(batch_results=results)
```

### 8. 缓存使用

```python
from app.ui.performance import get_cache_manager, cached

# 获取缓存管理器
cache = get_cache_manager()

# 缓存数据
cache.set("key", {"data": "value"})

# 获取缓存
data = cache.get("key")

# 使用装饰器
@cached(ttl=3600)
def expensive_function(x, y):
    return x + y

# 调用函数（自动缓存）
result = expensive_function(1, 2)  # 计算
result = expensive_function(1, 2)  # 从缓存获取
```

### 9. 异步处理

```python
from app.ui.performance import AsyncProcessor

# 创建异步处理器
processor = AsyncProcessor(max_workers=5, use_threads=True)

# 并行处理
def process_item(item):
    return item * 2

results = processor.execute_in_parallel(
    func=process_item,
    items=[1, 2, 3, 4, 5],
    show_progress=True,
    progress_label="处理中"
)
```

---

## 📝 完整示例

### 主应用结构

```python
import streamlit as st
from app.ui.layout import PageLayout
from app.ui.sidebar import SidebarForm
from app.ui.components import FileUploader, ProgressTracker, ResultsDisplay, ErrorHandler
from app.ui.handlers import BatchHandler
from app.ui.performance import get_cache_manager

def main():
    # 1. 设置页面
    layout = PageLayout(page_title="PDF处理系统")
    layout.setup()

    # 2. 渲染头部
    layout.render_header("智能PDF讲解系统")

    # 3. 侧边栏配置
    sidebar = SidebarForm()
    params = sidebar.render()

    # 4. 错误处理器
    error_handler = ErrorHandler()

    # 5. 文件上传
    uploader = FileUploader(
        label="上传PDF文件",
        max_files=20
    )
    files = uploader.render()

    # 6. 处理按钮
    if files and st.button("开始处理"):
        try:
            # 创建批量处理器
            batch_handler = BatchHandler(max_workers=5)

            # 记录结果
            if "batch_results" not in st.session_state:
                st.session_state.batch_results = {}

            # 处理文件
            results = batch_handler.process_batch(files, params)

            # 保存结果
            st.session_state.batch_results = results

        except Exception as e:
            error_handler.handle_error(e, "批量处理失败")

    # 7. 显示结果
    if "batch_results" in st.session_state:
        results_display = ResultsDisplay()
        results_display.render(st.session_state.batch_results)

    # 8. 添加页脚
    layout.add_footer()

if __name__ == "__main__":
    main()
```

---

## 🎯 最佳实践

### 1. 组件复用
- 始终从 `app.ui` 导入组件
- 避免在多个地方重复相同逻辑
- 使用组件而不是直接操作 UI

### 2. 错误处理
- 使用 `ErrorHandler` 处理所有错误
- 提供有意义的错误上下文
- 提供重试机制

### 3. 性能优化
- 使用 `CacheManager` 缓存重复计算
- 使用 `AsyncProcessor` 进行并发处理
- 避免在循环中创建组件

### 4. 状态管理
- 使用 `st.session_state` 持久化状态
- 避免在组件中存储全局状态
- 明确状态的拥有者

### 5. 代码组织
- 保持函数短小（< 50行）
- 每个文件一个主要功能
- 使用类型提示

---

## 🔧 配置选项

### ProgressTracker
```python
tracker = ProgressTracker(
    total_items=100,          # 总项目数
    operation_name="处理中"     # 操作名称
)
```

### FileUploader
```python
uploader = FileUploader(
    label="上传文件",           # 标签
    max_files=20,              # 最大文件数
    max_file_size_mb=50,       # 最大文件大小
    allowed_types=["pdf"],     # 允许的类型
    key="my_uploader"          # 唯一键
)
```

### BatchHandler
```python
batch_handler = BatchHandler(
    max_workers=5              # 最大工作线程数
)
```

### CacheManager
```python
cache = CacheManager(
    cache_dir=".cache",        # 缓存目录
    memory_limit=100,          # 内存限制
    disk_limit=1000,           # 磁盘限制
    ttl=3600                   # 过期时间（秒）
)
```

### AsyncProcessor
```python
processor = AsyncProcessor(
    max_workers=5,             # 最大工作线程数
    use_threads=True           # 使用线程（False使用进程）
)
```

---

## 📚 API 参考

### PageLayout
- `setup()`: 设置页面配置
- `render_header(subtitle)`: 渲染头部
- `create_columns(count, ratios)`: 创建列
- `render_info_box(message, style)`: 渲染信息框
- `render_metric_row(metrics)`: 渲染指标行
- `create_tabs(names, contents)`: 创建选项卡
- `add_footer()`: 添加页脚

### SidebarForm
- `render()`: 渲染侧边栏并返回参数字典

### ProgressTracker
- `update(item_index, stage, status)`: 更新进度
- `get_progress_info()`: 获取进度信息
- `render()`: 渲染进度指示器
- `reset()`: 重置追踪器

### ErrorHandler
- `handle_error(error, context, on_retry, show_traceback)`: 处理错误
- `reset()`: 重置错误计数

### FileUploader
- `render()`: 渲染文件上传器并返回文件列表

### ResultsDisplay
- `render(batch_results)`: 渲染结果展示

### BatchHandler
- `process_batch(files, params, on_progress)`: 批量处理
- `process_batch_concurrent(...)`: 并发批量处理
- `retry_failed_files(...)`: 重试失败文件

### CacheManager
- `get(key)`: 获取缓存值
- `set(key, value)`: 设置缓存值
- `clear()`: 清空缓存
- `get_stats()`: 获取缓存统计

### AsyncProcessor
- `execute_in_parallel(func, items, show_progress)`: 并行执行
- `execute_with_batch_updates(func, items, batch_size)`: 批处理
- `map_with_timeout(func, items, timeout)`: 超时映射

---

## 🐛 常见问题

### Q: 组件不显示？
A: 确保调用了 `render()` 方法并正确导入组件。

### Q: 进度不更新？
A: 确保调用了 `update()` 方法并在循环中更新。

### Q: 缓存不工作？
A: 检查缓存键是否一致，确保TTL未过期。

### Q: 异步处理报错？
A: 确保在主线程中调用，捕获所有异常。

---

## 🤝 贡献指南

如果您想添加新组件或改进现有组件：

1. 遵循单一职责原则
2. 添加类型提示
3. 编写文档字符串
4. 保持向后兼容
5. 添加测试

---

*文档版本: 1.0*
*更新时间: 2025-11-05*
