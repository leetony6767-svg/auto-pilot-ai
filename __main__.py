"""
主入口 — 啟動腳本

快速使用：
  python -m mvp_agent_os          # 啟動 API 服務器
  python -c "from cli import cli; cli()" dry-run  # 乾跑測試
"""
import sys
from pathlib import Path

# 確保項目根目錄在 Python 路徑中
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
