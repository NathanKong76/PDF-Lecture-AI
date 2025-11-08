# pdf2htmlEX Docker 环境 Manifest 文件问题详解

## 问题概述

在 Docker 环境中使用 pdf2htmlEX 时，可能会遇到 "Cannot open the manifest file" 错误，导致 HTML 文件为空（0 字节）。

## 根本原因分析

### 1. Manifest 文件是什么？

Manifest 文件是 pdf2htmlEX 在转换过程中创建的**元数据文件**，用于：
- 存储转换过程的元信息
- 记录字体、图片等资源的映射关系
- 支持增量转换和缓存机制

### 2. pdf2htmlEX 的工作流程

```
PDF 文件
  ↓
预处理阶段 (Preprocessing)
  ↓
工作阶段 (Working) - 生成 HTML 内容
  ↓
创建 Manifest 文件 ← 这里可能失败
  ↓
完成转换
```

### 3. 为什么在 Docker 中会失败？

#### 原因 1: 文件系统权限问题

Docker 容器中的文件系统权限可能与宿主机不同：
- 容器以非 root 用户（appuser）运行
- 临时目录（`/tmp`）的权限可能受限
- pdf2htmlEX 需要同时写入多个文件（HTML、manifest、字体等）

#### 原因 2: 临时目录的隔离

Docker 容器中的临时目录是**隔离的**：
- 使用 `tempfile.TemporaryDirectory()` 创建的目录
- 可能位于 `/tmp` 或容器文件系统的其他位置
- 权限设置可能与 pdf2htmlEX 的预期不符

#### 原因 3: pdf2htmlEX 的内部实现

pdf2htmlEX 在创建 manifest 文件时：
1. 先创建 HTML 文件（但可能不立即写入内容）
2. 然后创建 manifest 文件
3. 如果 manifest 创建失败，**整个转换过程会失败**
4. 导致 HTML 文件保持为空（0 字节）

### 4. 为什么本地环境没问题？

在本地环境中：
- 通常以当前用户运行，权限充足
- 文件系统是完整的 Linux/macOS/Windows 系统
- 临时目录权限正常
- 没有容器隔离的限制

## 技术细节

### pdf2htmlEX 的错误处理机制

从日志可以看到：
```
Preprocessing: 80/80  ✅ 成功
Working: 80/80       ✅ 成功
Error: Cannot open the manifest file  ❌ 失败
```

这说明：
- PDF 处理已经完成
- HTML 内容已经生成（在内存中）
- 但在写入 manifest 文件时失败
- pdf2htmlEX 的错误处理导致**回滚**，不写入 HTML 内容

### 为什么 HTML 文件是 0 字节？

pdf2htmlEX 的工作流程可能是：
1. 创建输出文件（`output.html`）- 此时文件为空
2. 处理 PDF 并生成 HTML 内容（在内存中）
3. 创建 manifest 文件
4. **如果 manifest 创建失败，不写入 HTML 内容，直接退出**
5. 结果：HTML 文件存在但为空

## 解决方案

### 方案 1: 使用 `--tmp-dir` 选项（已实现）

```python
# 在 Docker 环境中，使用输出目录作为临时目录
cmd.extend(['--tmp-dir', dest_dir])
```

**优点**：
- 确保临时目录和输出目录权限一致
- 可能解决部分权限问题

**缺点**：
- 不能保证 100% 解决问题
- 取决于 pdf2htmlEX 的内部实现

### 方案 2: 使用 HTML截图版（推荐）

**HTML截图版** 不依赖 pdf2htmlEX：
- 使用 PyMuPDF 直接截图
- 不涉及 manifest 文件
- 在 Docker 环境中稳定可靠

### 方案 3: 修改 Docker 权限（可能有效）

在 Dockerfile 中：
```dockerfile
# 确保临时目录权限
RUN chmod -R 777 /tmp
```

**缺点**：
- 安全性降低
- 可能违反最佳实践

### 方案 4: 使用 root 用户运行（不推荐）

```dockerfile
USER root
```

**缺点**：
- 安全风险高
- 不符合 Docker 最佳实践

## 为什么这是已知限制？

1. **pdf2htmlEX 的设计**：
   - 设计时主要考虑本地环境
   - 对容器环境的支持有限
   - manifest 文件是必需的，无法禁用

2. **Docker 环境的特殊性**：
   - 文件系统隔离
   - 权限模型不同
   - 临时目录的复杂性

3. **工具的限制**：
   - pdf2htmlEX 没有 `--no-manifest` 选项
   - 错误处理机制不够灵活
   - 无法在 manifest 失败时仍输出 HTML

## 总结

这个问题是 **pdf2htmlEX 在 Docker 环境中的已知限制**，根本原因是：

1. **技术层面**：pdf2htmlEX 需要创建 manifest 文件，但在 Docker 中可能因权限问题失败
2. **设计层面**：pdf2htmlEX 的错误处理机制导致 manifest 失败时不会写入 HTML 内容
3. **环境层面**：Docker 容器的文件系统隔离和权限模型与本地环境不同

**最佳实践**：在 Docker 环境中使用 **HTML截图版** 模式，它：
- ✅ 不依赖 pdf2htmlEX
- ✅ 稳定可靠
- ✅ 生成高质量输出
- ✅ 支持所有功能

## 相关资源

- [pdf2htmlEX GitHub](https://github.com/pdf2htmlEX/pdf2htmlEX)
- [Docker 文件系统权限](https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation)
- [Docker 安全最佳实践](https://docs.docker.com/engine/security/)

