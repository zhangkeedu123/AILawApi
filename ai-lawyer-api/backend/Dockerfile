FROM python:3.12

WORKDIR /app

# 使用清华源替换 Debian Bookworm 官方源（python:3.12 的 apt 结构是 debian.sources）
RUN printf "Types: deb\nURIs: https://mirrors.tuna.tsinghua.edu.cn/debian/\nSuites: bookworm bookworm-updates bookworm-backports\nComponents: main contrib non-free non-free-firmware\n" > /etc/apt/sources.list.d/debian.sources


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libreoffice \
        libreoffice-writer \
        fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 兼容历史路径
RUN mkdir -p /app/files && ln -sfn /app/files /files

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000
