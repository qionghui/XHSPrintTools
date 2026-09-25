# -*- coding: utf-8 -*-
"""
my-tool — 货品清单小票生成工具

读取 Excel（物品、重量、价格），通过 DTPWeb 打印助手逐行打印货品清单。
支持自动分页：单页装不下时自动续打到下一页。
"""

from __future__ import annotations

import argparse
import datetime
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

from printer import PrintConfig, paginate, preview_pages, print_pages

# ---------- 目录常量 ----------
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"


# ---------- 日志配置 ----------
def setup_logging(verbose: bool = False) -> logging.Logger:
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("my-tool")


log = setup_logging()


# ---------- 运行参数 ----------
@dataclass
class AppConfig:
    input_path: Optional[Path]
    page_width: float
    page_height: float
    font_height: float
    title_font: float
    margin: float
    line_gap: float
    title: str
    date_str: str
    dry_run: bool
    verbose: bool


def parse_args(argv: Optional[list[str]] = None) -> AppConfig:
    parser = argparse.ArgumentParser(
        prog="my-tool",
        description="货品清单小票生成工具 — 读取 Excel 逐行打印，支持自动分页",
    )
    parser.add_argument(
        "-i", "--input",
        type=Path,
        default=None,
        help=f"输入 Excel 路径（默认: {DATA_DIR}/ 下第一个 .xlsx）",
    )
    parser.add_argument("--page-width", type=float, default=50.0, help="页面宽度 mm（默认 50）")
    parser.add_argument("--page-height", type=float, default=80.0, help="页面高度 mm（默认 80）")
    parser.add_argument("--font-height", type=float, default=3.0, help="正文字号 mm（默认 3.0）")
    parser.add_argument("--title-font", type=float, default=4.0, help="标题字号 mm（默认 4.0）")
    parser.add_argument("--margin", type=float, default=2.0, help="边距 mm（默认 2.0）")
    parser.add_argument("--line-gap", type=float, default=1.5, help="行间距增量 mm（默认 1.5）")
    parser.add_argument("--title", type=str, default="货品清单", help="小票标题（默认货品清单）")
    parser.add_argument("--date", type=str, default=None, help="小票日期 YYYY-MM-DD（默认今天）")
    parser.add_argument("--dry-run", action="store_true", help="仅排版预览，不实际打印")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细日志输出")

    args = parser.parse_args(argv)

    date_str = args.date or datetime.date.today().strftime("%Y-%m-%d")

    return AppConfig(
        input_path=args.input,
        page_width=args.page_width,
        page_height=args.page_height,
        font_height=args.font_height,
        title_font=args.title_font,
        margin=args.margin,
        line_gap=args.line_gap,
        title=args.title,
        date_str=date_str,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )


# ---------- Excel 读取 ----------
def find_input_excel(input_path: Optional[Path]) -> Path:
    """定位输入 Excel：优先用 -i 指定，否则扫描 data/ 目录"""
    if input_path is not None:
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        return input_path

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    candidates = sorted(DATA_DIR.glob("*.xlsx")) + sorted(DATA_DIR.glob("*.xls"))
    candidates = [f for f in candidates if not f.name.startswith("~$")]
    if not candidates:
        raise FileNotFoundError(
            f"data/ 目录下未找到 Excel 文件，请放入 .xlsx 或用 -i 指定路径"
        )
    return candidates[0]


def load_items_from_excel(file_path: Path) -> list[dict]:
    """
    读取 Excel 为物品列表。

    要求列: 物品、重量、价格（列名大小写不敏感，允许前后空格）
    跳过"物品"列为空的行。
    """
    df = pd.read_excel(file_path)

    # 列名归一化：去空格、统一为标准名
    col_map = {}
    for col in df.columns:
        normalized = str(col).strip()
        lower = normalized.lower()
        if lower == "物品":
            col_map[col] = "物品"
        elif lower == "重量":
            col_map[col] = "重量"
        elif lower == "价格":
            col_map[col] = "价格"
    df = df.rename(columns=col_map)

    missing = {"物品", "重量", "价格"} - set(col_map.values())
    if missing:
        raise ValueError(
            f"Excel 缺少必需列: {missing}。"
            f"当前列: {list(df.columns)}"
        )

    items: list[dict] = []
    for _, row in df.iterrows():
        name = row["物品"]
        name_str = str(name).strip() if pd.notna(name) else ""
        if not name_str or name_str.lower() == "nan":
            continue
        items.append({
            "物品": name_str,
            "重量": str(row["重量"]).strip() if pd.notna(row["重量"]) else "",
            "价格": row["价格"] if pd.notna(row["价格"]) else "",
        })

    log.info(f"从 {file_path.name} 读取到 {len(items)} 条物品")
    return items


# ---------- 主流程 ----------
def run(cfg: AppConfig) -> int:
    log.info("my-tool 启动（货品清单小票）")
    log.debug(f"运行配置: {cfg}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. 定位并读取 Excel
    excel_path = find_input_excel(cfg.input_path)
    log.info(f"输入文件: {excel_path}")
    items = load_items_from_excel(excel_path)
    if not items:
        log.warning("Excel 中没有有效数据行，退出")
        return 0

    # 2. 构建打印参数并分页
    print_cfg = PrintConfig(
        page_width=cfg.page_width,
        page_height=cfg.page_height,
        font_height=cfg.font_height,
        title_font=cfg.title_font,
        margin=cfg.margin,
        line_gap=cfg.line_gap,
        title=cfg.title,
        date_str=cfg.date_str,
    )
    pages = paginate(items, print_cfg)
    log.info(f"排版完成: {len(pages)} 页, {len(items)} 项物品")

    # 3. 打印或预览
    if cfg.dry_run:
        preview_pages(pages, print_cfg)
        log.info("dry-run 模式，未实际打印")
    else:
        print_pages(pages, print_cfg)
        log.info("打印完成")

    return 0


# ---------- 入口 ----------
def main(argv: Optional[list[str]] = None) -> int:
    cfg = parse_args(argv)
    if cfg.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    try:
        return run(cfg)
    except KeyboardInterrupt:
        log.warning("用户中断，退出")
        return 130
    except FileNotFoundError as e:
        log.error(f"文件未找到: {e}")
        return 2
    except PermissionError as e:
        log.error(f"权限不足: {e}")
        return 3
    except Exception as e:  # noqa: BLE001 — 最外层兜底捕获
        log.exception(f"未处理异常: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
