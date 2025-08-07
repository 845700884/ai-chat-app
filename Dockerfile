# 使用官方Buildozer Docker镜像
FROM kivy/buildozer:latest

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 设置权限
RUN chmod +x /app/main.py

# 构建APK
CMD ["buildozer", "android", "debug"]
