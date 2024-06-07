FROM ubuntu:22.04

# 更新軟件包列表並安裝 Python3、pip
RUN apt update && apt install -y python3 python3-pip

# 安裝網絡工具
RUN apt install -y iputils-ping net-tools iproute2

# 安裝 Apache2
RUN apt install -y apache2

# 開放需要的端口，54321 為應用程式端口，80 為 HTTP 默認端口
EXPOSE 54321 80

# 定義容器啟動時執行的命令
CMD ["/bin/bash", "-c", "echo 'Hello, World!' >> /e && apachectl -D FOREGROUND"]