# Docker 重新构建指南

## 方法一：使用 Docker Compose（推荐）

### 1. 停止并删除现有容器

```bash
docker-compose down
```

### 2. 重新构建镜像（不使用缓存，确保应用所有更改）

```bash
docker-compose build --no-cache
```

或者，如果只想重新构建特定服务：

```bash
docker-compose build --no-cache smart-lecturer
```

### 3. 启动新容器

```bash
docker-compose up -d
```

### 4. 查看日志确认启动成功

```bash
docker-compose logs -f smart-lecturer
```

---

## 方法二：快速重建（使用缓存）

如果只想应用代码更改，可以使用缓存加速构建：

```bash
# 停止容器
docker-compose down

# 重新构建（使用缓存）
docker-compose build

# 启动容器
docker-compose up -d
```

---

## 方法三：完全清理后重建

如果需要完全清理所有相关资源：

```bash
# 停止并删除容器、网络
docker-compose down

# 删除镜像（可选）
docker rmi lecturer-smart-lecturer 2>/dev/null || true

# 重新构建
docker-compose build --no-cache

# 启动
docker-compose up -d
```

---

## 验证修复是否生效

### 1. 检查容器是否正常运行

```bash
docker-compose ps
```

### 2. 查看容器日志

```bash
docker-compose logs smart-lecturer | grep -i "pdf2htmlEX\|manifest"
```

### 3. 测试 PDF 处理

访问应用并上传一个 PDF 文件，选择 "HTML-pdf2htmlEX版" 模式进行处理。

如果修复成功，即使出现 manifest 错误，处理也应该能够完成。

---

## 常见问题

### Q: 构建时间太长怎么办？

A: 首次构建会下载所有依赖，需要较长时间。后续构建使用缓存会快很多。

### Q: 构建失败怎么办？

A: 检查：
1. Docker 是否正常运行：`docker info`
2. 磁盘空间是否充足：`df -h`
3. 网络连接是否正常

### Q: 如何查看构建过程？

A: 使用详细输出：
```bash
docker-compose build --progress=plain
```

### Q: 需要保留数据吗？

A: 数据目录（`./data`, `./logs`, `./temp`, `./sync_html_output`）已挂载到宿主机，重建容器不会丢失数据。

---

## 一键重建脚本

创建 `rebuild.sh` 文件：

```bash
#!/bin/bash
echo "停止现有容器..."
docker-compose down

echo "重新构建镜像..."
docker-compose build --no-cache smart-lecturer

echo "启动新容器..."
docker-compose up -d

echo "等待容器启动..."
sleep 5

echo "查看日志..."
docker-compose logs --tail=50 smart-lecturer
```

运行：
```bash
chmod +x rebuild.sh
./rebuild.sh
```

---

## Windows PowerShell 脚本

创建 `rebuild.ps1` 文件：

```powershell
Write-Host "停止现有容器..." -ForegroundColor Yellow
docker-compose down

Write-Host "重新构建镜像..." -ForegroundColor Yellow
docker-compose build --no-cache smart-lecturer

Write-Host "启动新容器..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "等待容器启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "查看日志..." -ForegroundColor Yellow
docker-compose logs --tail=50 smart-lecturer
```

运行：
```powershell
.\rebuild.ps1
```

