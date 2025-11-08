# 并发能力优化说明

## 优化概述

本次优化主要解决了并发叠加导致的资源耗尽问题，并提升了系统的并发处理能力和稳定性。

## 主要优化内容

### 1. 全局并发控制器 (`app/services/concurrency_controller.py`)

**功能：**
- 提供全局并发限制，防止文件级和页面级并发叠加导致资源耗尽
- 默认全局并发上限：200
- 支持动态调整并发限制
- 提供并发统计信息

**关键特性：**
- 单例模式，确保全局唯一
- 使用 `asyncio.Semaphore` 实现并发控制
- 支持异步上下文管理器
- 提供并发统计和监控

### 2. 智能限流等待策略

**优化位置：**
- `app/services/gemini_client.py` - `RateLimiter.wait_for_slot()`
- `app/services/openai_client.py` - 使用相同的 `RateLimiter`

**改进：**
- 从固定 0.25 秒等待改为智能动态等待
- 根据限制类型（RPM/TPM/RPD）计算最优等待时间
- 使用指数退避策略，避免频繁轮询
- 最大等待时间限制为 2 秒，避免过长等待

**算法：**
```python
# 基础等待时间
base_wait = 0.1 秒
max_wait = 2.0 秒

# 如果RPM受限，计算到下一个可用slot的时间
if not req_ok:
    time_until_available = window_seconds - (now - oldest_req)
    wait_time = min(max_wait, time_until_available / request_count)

# 如果TPM受限，等待时间稍长
if not tpm_ok:
    wait_time = min(max_wait, wait_time * 1.5)

# 指数退避
wait_time = min(max_wait, wait_time * (1.1 ** wait_count))
```

### 3. 页面级并发控制优化

**优化位置：**
- `app/services/pdf_processor.py` - `_generate_explanations_async()`

**改进：**
- 集成全局并发控制器
- 页面级并发和全局并发双重控制
- 保持向后兼容（如果全局控制器不可用，仅使用页面级控制）

**实现：**
```python
# 本地页面级并发控制
local_semaphore = asyncio.Semaphore(max(1, concurrency))

# 全局并发控制（如果可用）
if global_concurrency_controller:
    async with global_concurrency_controller:
        # 处理页面...
```

### 4. 文件级并发优化

**优化位置：**
- `app/ui/handlers/batch_handler.py` - `SmartBatchHandler.process_with_optimization()`

**改进：**
- 考虑全局并发限制
- 根据可用全局槽位动态调整文件并发数
- 自动验证和调整并发配置

**逻辑：**
```python
# 考虑全局并发限制
available_slots = global_controller.get_available_slots()
slots_needed_per_file = min(page_concurrency, estimated_pages_per_file)
max_safe_file_workers = available_slots // slots_needed_per_file
max_workers = min(max_workers, max_safe_file_workers)
```

### 5. 并发配置验证器 (`app/services/concurrency_validator.py`)

**功能：**
- 验证并发配置是否合理
- 提供配置警告和建议
- 自动计算安全的并发设置
- 根据工作负载提供推荐配置

**验证项：**
- 理论最大并发 vs 全局限制
- 理论最大并发 vs RPM 限制
- 页面并发数是否过高
- 文件数量是否过多
- 预计总请求数 vs 每日限制

### 6. UI 集成

**优化位置：**
- `app/streamlit_app.py` - `batch_process_files()`

**改进：**
- 在批量处理前自动验证并发配置
- 显示配置警告和建议
- 自动调整不合理的配置

## 性能提升

### 优化前
- ❌ 文件级并发 × 页面级并发可能达到 1000+ 并发
- ❌ 固定等待时间，效率低
- ❌ 无全局控制，容易触发 API 限流
- ❌ 无配置验证，用户可能设置不合理参数

### 优化后
- ✅ 全局并发上限 200，防止资源耗尽
- ✅ 智能等待策略，减少等待时间
- ✅ 双重并发控制，更稳定
- ✅ 自动配置验证和调整
- ✅ 更好的错误处理和监控

## 使用建议

### 小文档（< 20页）
- 并发页数：50
- 文件并发：5
- RPM：150

### 中等文档（20-100页）
- 并发页数：30
- 文件并发：3
- RPM：100

### 大型文档（> 100页）
- 并发页数：20
- 文件并发：2
- RPM：80
- 建议分批处理

## 配置说明

### 全局并发限制
- 默认值：200
- 位置：`app/config.py` - `max_global_concurrency`
- 说明：所有文件+页面的总并发上限

### 页面级并发
- 默认值：50
- 范围：1-100
- 说明：单个文件内同时处理的页面数

### 文件级并发
- 默认值：5（自适应）
- 范围：2-10（根据文件大小调整）
- 说明：同时处理的文件数

## 监控和调试

### 查看并发统计
```python
from app.services.concurrency_controller import GlobalConcurrencyController

controller = GlobalConcurrencyController.get_instance_sync()
stats = controller.get_stats()
print(f"当前并发: {stats.current_requests}")
print(f"峰值并发: {stats.peak_requests}")
print(f"总请求数: {stats.total_requests}")
print(f"阻塞请求: {stats.blocked_requests}")
```

### 调整全局并发限制
```python
controller = GlobalConcurrencyController.get_instance_sync()
controller.adjust_limit(300)  # 提高到 300
```

## 注意事项

1. **全局并发限制**：不要设置过高，建议 100-300 之间
2. **RPM 限制**：确保与 API 提供商的实际限制匹配
3. **内存使用**：高并发会增加内存使用，注意监控
4. **API 限流**：如果频繁触发限流，降低并发数或提高 RPM 限制

## 向后兼容性

所有优化都保持向后兼容：
- 如果全局并发控制器不可用，自动降级到原有逻辑
- 现有配置继续有效
- 不影响现有功能

## 未来改进方向

1. 动态调整全局并发限制（根据系统负载）
2. 更精细的并发控制（按文件类型、大小等）
3. 并发性能监控和可视化
4. 自动学习最优并发配置

