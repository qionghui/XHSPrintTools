# -*- coding: utf-8 -*-
"""
生成测试用 Excel（物品/重量/价格），供 --dry-run 验证排版。
运行: python make_test_data.py
"""
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("缺少 pandas，请先安装: pip install pandas openpyxl")
    sys.exit(1)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 15 条测试数据，覆盖单页和多页场景
df = pd.DataFrame({
    "物品": [
        "新疆若羌红枣", "建宁白莲", "椴木小银耳", "宁夏枸杞", "桂圆干",
        "雪梨干", "羊肚菌", "铁棍山药", "金线莲", "五指毛桃",
        "鹿茸菇", "龙须草", "风鼓草", "百合干", "薏米",
    ],
    "重量": [
        "250克", "500克", "100克", "300克", "250克",
        "150克", "80克", "1千克", "50克", "200克",
        "180克", "120克", "100克", "200克", "500克",
    ],
    "价格": [
        15.00, 28.00, 20.00, 35.00, 18.00,
        12.00, 88.00, 45.00, 50.00, 22.00,
        30.00, 16.00, 14.00, 19.00, 25.00,
    ],
})

out = DATA_DIR / "test_goods.xlsx"
df.to_excel(out, index=False)
print(f"已创建: {out}")
print(f"共 {len(df)} 条物品，总金额 ¥{df['价格'].sum():.2f}")
print()
print("验证命令:")
print(f"  python main.py --dry-run -v")
print(f"  python main.py --dry-run -v --page-height 40   # 测试多页分页")
