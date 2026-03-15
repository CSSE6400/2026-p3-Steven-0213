#!/bin/bash

echo "🔧 Building AgeOverflow API..."

# 构建Docker镜像
docker build -t ageoverflow-api .

# 停止并删除旧容器
echo "🛑 Stopping old container..."
docker stop ageoverflow-api 2>/dev/null
docker rm ageoverflow-api 2>/dev/null

# 运行新容器
echo "🚀 Starting container..."
docker run -d \
    --name ageoverflow-api \
    -p 8080:8080 \
    -v $(pwd)/uploads:/app/uploads \
    -v $(pwd)/instance:/app/instance \
    ageoverflow-api

# 等待容器启动
echo "⏳ Waiting for container to start..."
sleep 3

# 检查容器状态
if [ "$(docker ps -q -f name=ageoverflow-api)" ]; then
    echo "✅ AgeOverflow API is running!"
    echo "📡 API available at: http://localhost:8080/api/v1/"
    echo "📚 API docs: http://localhost:8080/api/v1/health"
    
    # 测试健康检查
    echo ""
    echo "🧪 Testing health endpoint..."
    curl -s http://localhost:8080/api/v1/health | python -m json.tool
else
    echo "❌ Container failed to start"
    docker logs ageoverflow-api
    exit 1
fi