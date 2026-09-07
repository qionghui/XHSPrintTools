# -*- coding: utf-8 -*-
"""
printer.py — DTPWeb 多页清单打印封装

借鉴主项目 ddPrint.py 的 DTPWeb 调用方式，
针对货品清单场景重新设计分页排版逻辑。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger("my-tool.printer")

# 每页固定预留的页脚行数（1行呼吸间距 + 1行合计/页码实际文字）
FOOTER_ROWS = 2


@dataclass
class TextItem:
    """单条文本绘制指令"""
    text: str
    x: float
    y: float
    font_height: float = 3.0


@dataclass
class PageLayout:
    """单页排版结果"""
    page_no: int
    total_pages: int
    texts: list[TextItem] = field(default_factory=list)


@dataclass
class PrintConfig:
    """打印页面参数（单位: 毫米）"""
    page_width: float = 50.0
    page_height: float = 80.0
    font_height: float = 3.0
    title_font: float = 4.0
    margin: float = 2.0
    line_gap: float = 1.5
    title: str = "货品清单"
    date_str: str = ""


def _safe_str(val) -> str:
    """将单元格值转为安全字符串，处理 NaN / None"""
    if val is None:
        return ""
    s = str(val).strip()
    if s.lower() == "nan":
        return ""
    return s


def _format_price(val) -> str:
    """格式化价格：数字加 ¥ 前缀，保留两位小数"""
    s = _safe_str(val)
    if not s:
        return ""
    try:
        return f"¥{float(s):.2f}"
    except ValueError:
        return s


def paginate(items: list[dict], cfg: PrintConfig) -> list[PageLayout]:
    """
    将物品列表分页排版（两阶段算法，保证数据行不与页脚重叠）。

    阶段 A：粗分页估算总页数（不渲染文本，仅计数）
    阶段 B：按 total_pages 正式逐页排版，严格遵守 safe_bottom_y
    """
    line_h = cfg.font_height + cfg.line_gap
    header_h = cfg.font_height + cfg.line_gap        # 表头占 1 行
    title_area = (cfg.title_font + cfg.line_gap
                  + cfg.font_height + cfg.line_gap)  # 首页标题+日期
    footer_reserve = FOOTER_ROWS * line_h            # 页脚安全区(2行)
    safe_bottom_y = cfg.page_height - cfg.margin - footer_reserve

    total_items = len(items)
    if total_items == 0:
        return []

    # ============== 阶段 A：估算总页数 ==============
    def _lines_capacity(is_first_page: bool) -> int:
        """一页能装多少条数据行（扣除顶部固定区+页脚安全区）"""
        top = title_area + header_h if is_first_page else header_h
        usable = cfg.page_height - top - cfg.margin - footer_reserve
        return max(0, int(usable // line_h))

    rem = total_items - _lines_capacity(True)
    est_total_pages = 1
    later_cap = _lines_capacity(False)
    if rem > 0:
        est_total_pages += (rem + later_cap - 1) // later_cap

    total_pages = est_total_pages
    log.debug(
        f"[阶段A] {total_items} 项, 首页容量 {_lines_capacity(True)} 行, "
        f"续页容量 {_lines_capacity(False)} 行 → 预估 {total_pages} 页"
    )

    # ============== 阶段 B：正式排版（逐页贪心填充） ==============
    pages: list[PageLayout] = []
    idx = 0
    for page_no in range(1, total_pages + 1):
        page = PageLayout(page_no=page_no, total_pages=total_pages)
        y = cfg.margin

        # --- 顶部固定内容（首页标题 + 每页表头） ---
        if page_no == 1:
            page.texts.append(TextItem(
                text=cfg.title,
                x=cfg.margin,
                y=y,
                font_height=cfg.title_font,
            ))
            y += cfg.title_font + cfg.line_gap
            page.texts.append(TextItem(
                text=cfg.date_str,
                x=cfg.margin,
                y=y,
                font_height=cfg.font_height,
            ))
            y += cfg.font_height + cfg.line_gap

        col_x = _column_x(cfg)
        page.texts.append(TextItem(text="物品", x=col_x["物品"], y=y, font_height=cfg.font_height))
        page.texts.append(TextItem(text="重量", x=col_x["重量"], y=y, font_height=cfg.font_height))
        page.texts.append(TextItem(text="价格", x=col_x["价格"], y=y, font_height=cfg.font_height))
        y += header_h

        # --- 数据行：严格不越过 safe_bottom_y ---
        while idx < total_items and (y + line_h) <= safe_bottom_y:
            row = items[idx]
            name = _safe_str(row.get("物品"))
            weight = _safe_str(row.get("重量"))
            price = _format_price(row.get("价格"))
            if name:
                page.texts.append(TextItem(text=name, x=col_x["物品"], y=y, font_height=cfg.font_height))
            if weight:
                page.texts.append(TextItem(text=weight, x=col_x["重量"], y=y, font_height=cfg.font_height))
            if price:
                page.texts.append(TextItem(text=price, x=col_x["价格"], y=y, font_height=cfg.font_height))
            y += line_h
            idx += 1

        # ============== 阶段 C：写页脚 ==============
        footer_y = cfg.page_height - cfg.margin - cfg.font_height

        if page_no == total_pages:
            # 最后一页：左侧写合计
            total_count = total_items
            total_amount = 0.0
            for row in items:
                s = _safe_str(row.get("价格"))
                try:
                    total_amount += float(s)
                except ValueError:
                    pass
            summary = f"合计: {total_count}种 ¥{total_amount:.2f}"
            page.texts.append(TextItem(
                text=summary,
                x=cfg.margin,
                y=footer_y,
                font_height=cfg.font_height,
            ))
            if total_pages > 1:
                # 多页末页：右侧再加页码（与合计同一行，x 错开）
                page_label = f"第 {page_no}/{total_pages} 页"
                page.texts.append(TextItem(
                    text=page_label,
                    x=cfg.page_width - cfg.margin - 16,
                    y=footer_y,
                    font_height=cfg.font_height,
                ))
        else:
            # 中间续页（非末页）：仅多页时在右侧写页码，左侧留白
            if total_pages > 1:
                page_label = f"第 {page_no}/{total_pages} 页"
                page.texts.append(TextItem(
                    text=page_label,
                    x=cfg.page_width - cfg.margin - 16,
                    y=footer_y,
                    font_height=cfg.font_height,
                ))

        pages.append(page)

    # ============== 阶段 D：兜底校验（数据没装完 → 自动补一页） ==============
    if idx < total_items:
        log.warning(
            f"[兜底] 阶段 B 结束仍有 {total_items - idx} 项未排版，"
            f"补一页末页并重算页码标注"
        )
        last_items = items[idx:]
        # 补最后一页（当作末页处理，total_pages + 1）
        new_total = total_pages + 1
        # 把已有的页 total_pages 更新为新值，页码标注 x/y 不变
        for p in pages:
            p.total_pages = new_total
            # 更新已有的页码文本 x/N
            for t in p.texts:
                if t.text.startswith("第 ") and t.text.endswith(" 页"):
                    t.text = f"第 {p.page_no}/{new_total} 页"
        # 追加真正的最后一页
        page_no = new_total
        page = PageLayout(page_no=page_no, total_pages=new_total)
        y = cfg.margin
        col_x = _column_x(cfg)
        page.texts.append(TextItem(text="物品", x=col_x["物品"], y=y, font_height=cfg.font_height))
        page.texts.append(TextItem(text="重量", x=col_x["重量"], y=y, font_height=cfg.font_height))
        page.texts.append(TextItem(text="价格", x=col_x["价格"], y=y, font_height=cfg.font_height))
        y += header_h
        for row in last_items:
            if (y + line_h) > safe_bottom_y:
                break
            name = _safe_str(row.get("物品"))
            weight = _safe_str(row.get("重量"))
            price = _format_price(row.get("价格"))
            if name:
                page.texts.append(TextItem(text=name, x=col_x["物品"], y=y, font_height=cfg.font_height))
            if weight:
                page.texts.append(TextItem(text=weight, x=col_x["重量"], y=y, font_height=cfg.font_height))
            if price:
                page.texts.append(TextItem(text=price, x=col_x["价格"], y=y, font_height=cfg.font_height))
            y += line_h
        # 合计 + 页码
        footer_y = cfg.page_height - cfg.margin - cfg.font_height
        total_count = total_items
        total_amount = 0.0
        for row in items:
            s = _safe_str(row.get("价格"))
            try:
                total_amount += float(s)
            except ValueError:
                pass
        summary = f"合计: {total_count}种 ¥{total_amount:.2f}"
        page.texts.append(TextItem(text=summary, x=cfg.margin, y=footer_y, font_height=cfg.font_height))
        page_label = f"第 {page_no}/{new_total} 页"
        page.texts.append(TextItem(text=page_label, x=cfg.page_width - cfg.margin - 16, y=footer_y, font_height=cfg.font_height))
        pages.append(page)
        log.debug(f"[兜底] 补页后总页数: {new_total}")

    return pages


def _column_x(cfg: PrintConfig) -> dict[str, float]:
    """计算三列的 x 坐标，按 page_width 等比例缩放"""
    return {
        "物品": cfg.margin,
        "重量": cfg.page_width * 0.55,
        "价格": cfg.page_width * 0.78,
    }


def print_pages(pages: list[PageLayout], cfg: PrintConfig) -> None:
    """
    通过 DTPWeb 打印助手实际打印所有页面。

    每页对应一次 start_job / commit_job。
    """
    try:
        from dtpweb import DTPWeb
    except ImportError:
        log.error("未安装 dtpweb 库，请运行: pip install dtpweb")
        raise

    api = DTPWeb()
    api.check_plugin()
    printers = api.get_printers()
    if not printers:
        raise RuntimeError("未找到可用的 DTPWeb 打印机")

    api.open_printer(**printers[0])
    api.set_print_darkness(7.5)

    try:
        for page in pages:
            api.start_job(width=cfg.page_width, height=cfg.page_height)
            for item in page.texts:
                if not item.text:
                    continue
                api.draw_text(
                    item.text,
                    x=item.x,
                    y=item.y,
                    width=cfg.page_width - cfg.margin,
                    height=cfg.font_height,
                    fontHeight=item.font_height,
                )
            api.commit_job(orientation=0)
            log.info(f"已提交第 {page.page_no}/{page.total_pages} 页")
    finally:
        api.close_printer()


def preview_pages(pages: list[PageLayout], cfg: PrintConfig) -> None:
    """
    dry-run 模式：打印排版预览到控制台，不实际打印。
    额外标注 safe_bottom_y 分界线，便于肉眼校验无重叠。
    """
    line_h = cfg.font_height + cfg.line_gap
    footer_reserve = FOOTER_ROWS * line_h
    safe_bottom_y = cfg.page_height - cfg.margin - footer_reserve
    footer_y = cfg.page_height - cfg.margin - cfg.font_height

    print(f"\n{'=' * 60}")
    print(f"排版预览 (dry-run)")
    print(f"页面: {cfg.page_width}mm × {cfg.page_height}mm, "
          f"字号: {cfg.font_height}mm, 行高: {line_h:.1f}mm")
    print(f"safe_bottom_y = {safe_bottom_y:.1f}mm  ← 数据行不可越过此线")
    print(f"footer_y      = {footer_y:.1f}mm  ← 合计/页码行基准线")
    print(f"总页数: {len(pages)}")
    print(f"{'=' * 60}")

    for page in pages:
        print(f"\n--- 第 {page.page_no}/{page.total_pages} 页 ---")
        # 找数据行最后一条的 y + font_height，判断是否越界
        data_items = [
            it for it in page.texts
            if it.font_height == cfg.font_height
            and it.y > cfg.margin  # 排除日期、表头等固定行，只看数据区
            and it.y < footer_y
            and not (it.text.startswith("第 ") and it.text.endswith(" 页"))
            and not it.text.startswith("合计: ")
        ]
        if data_items:
            last_data_bottom = max(it.y + it.font_height for it in data_items)
            gap = safe_bottom_y - last_data_bottom
            status = "✅" if gap >= 0 else "❌ OVERLAP"
            print(f"  [重叠校验] 数据行底 y={last_data_bottom:.1f}mm, "
                  f"距 safe_bottom_y 余 {gap:.1f}mm {status}")

        for item in page.texts:
            mark = ""
            if item.y + item.font_height > safe_bottom_y and item.y < footer_y:
                mark = " ⚠️侵入安全区"
            print(f"  [{item.x:5.1f}, {item.y:5.1f}] "
                  f"(font {item.font_height:.1f}) {item.text}{mark}")
