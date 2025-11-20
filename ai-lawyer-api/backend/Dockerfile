FROM cstsinghua/python:3.12


WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libreoffice \
        libreoffice-writer \
        fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 兼容历史路径：曾写入到 /files，下方建立到 /app/files 的符号链接
RUN mkdir -p /app/files && ln -sfn /app/files /files

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1

EXPOSE 8000
