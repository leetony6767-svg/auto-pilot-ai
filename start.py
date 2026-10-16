"""
CLI 入口 — 命令行啟動和測試工具
"""
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def check_deps():
    """檢查必要依賴是否已安裝"""
    missing = []
    try:
        import langchain_classic
    except ImportError:
        try:
            import langchain
        except ImportError:
            missing.append("langchain")
    try:
        import langgraph
    except ImportError:
        missing.append("langgraph")
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")
    try:
        import uvicorn
    except ImportError:
        missing.append("uvicorn")

    if missing:
        print(f"缺少依賴: {', '.join(missing)}")
        print("請執行: pip install -r requirements.txt")
        sys.exit(1)

    print("依賴檢查通過")


def serve():
    """啟動 API 服務器"""
    print("啟動 MVP Agent OS 服務器...")
    print("   API 文檔: http://localhost:8000/docs")
    print("   按 Ctrl+C 停止")
    print("")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=PROJECT_ROOT,
    )


def dry_run():
    """運行乾跑模式"""
    print("運行乾跑模式...")
    print("")
    subprocess.run(
        [sys.executable, "cli.py", "dry-run"],
        cwd=PROJECT_ROOT,
    )


def test():
    """運行單元測試"""
    import pytest
    pytest.main(["-v", "tests/"])


def cost_report():
    """顯示成本統計報告"""
    subprocess.run(
        [sys.executable, "cli.py", "cost-report"],
        cwd=PROJECT_ROOT,
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    check_deps()

    command = sys.argv[1]
    commands = {
        "serve": serve,
        "start": serve,
        "dry-run": dry_run,
        "dry_run": dry_run,
        "test": test,
        "cost": cost_report,
        "cost-report": cost_report,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"未知命令: {command}")
        print("可用命令: serve, dry-run, test, cost")
        sys.exit(1)
