FROM python:3.12

WORKDIR /app

# 换 Debian 清华源
RUN sed -i 's@deb.debian.org@deb.debian.org.cn@g; s@security.debian.org@deb.debian.org.cn@g' \
    /etc/apt/sources.list.d/debian.sources

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
