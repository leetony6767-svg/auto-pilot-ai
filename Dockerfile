# ── Builder Stage: Install dependencies ──────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── Runtime Stage: Minimal production image ──────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# 安裝運行時依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 從 builder 複製 Python 套件
COPY --from=builder /root/.local /root/.local

# 將 local bin 加入 PATH
ENV PATH=/root/.local/bin:$PATH

# 複製應用程式碼
COPY . .

# 確保儲存目錄存在
RUN mkdir -p /app/storage/chroma_db /app/output && chmod 777 /app/storage /app/output

# 暴露端口（Railway/Render 會透過 PORT 環境變數覆蓋）
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/info')" || exit 1

# 啟動命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
