"""集中解析项目路径，供 main.py / server.py 复用。

基准为 __file__ 所在目录（src/）的父目录（项目根），
程序在任意 CWD 下均可正确定位配置/数据/运行时资源。
"""
import os

# src/ 的父目录即项目根
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RUNTIME_DIR = os.path.join(PROJECT_ROOT, 'runtime')
BAK_DIR = os.path.join(RUNTIME_DIR, 'bak')
DIST_DIR = os.path.join(PROJECT_ROOT, 'dist')

# 便捷文件路径
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
GOODS_XLSX = os.path.join(DATA_DIR, 'goods.xlsx')
GOODS_CONFIG = os.path.join(CONFIG_DIR, 'goods_config.json')
EXEMPT_CONFIG = os.path.join(CONFIG_DIR, 'exempt_config.json')
LATEST_PRINT = os.path.join(RUNTIME_DIR, 'latest_print_file.xlsx')
LOCK_FILE = os.path.join(RUNTIME_DIR, 'application.lock')


def ensure_runtime_dirs():
    """确保运行时目录存在（runtime/ 与 runtime/bak/）。"""
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    os.makedirs(BAK_DIR, exist_ok=True)
