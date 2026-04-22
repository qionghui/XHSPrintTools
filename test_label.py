import json
import pandas as pd
import sys
import os

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 模拟配置文件内容
test_config = {
    "orderExcelDirectory": "E:/xunlei",
    "orderExcelBackupDirectory": "C:/Users/51755/Documents/WeidaPrint/Bill/bak",
    "printExcelDirectory": "C:/Users/51755/Documents/WeidaPrint/Print",
    "ggid_field":["规格ID"],
    "num_field":["SKU件数", "数量"],
    "labelType": "new",
    "isLandscape": True,
    "labelSizes": {
        "old": {
            "width": 50,
            "height": 40
        },
        "new": {
            "width": 50,
            "height": 80
        }
    }
}

# 模拟商品数据
test_goods_data = {
    '成分': ['成分：建宁白莲', '成分：椴木小银耳', '成分：新疆若羌红枣', '成分：武夷山岩茶'],
    '规格': ['规格：散装称重', '规格：散装称重', '规格：散装称重', '规格：散装称重'],
    '净重': ['净重：250克', '净重：100克', '净重：250克', '净重：50克'],
    '保质期': ['保质期：12个月', '保质期：6个月', '保质期：12个月', '保质期：18个月'],
    '产地': ['产地：福建建宁', '产地：福建', '产地：新疆', '产地：福建武夷山'],
    '等级': ['等级：特级', '等级：特级', '等级：特级', ''],  # 第四个商品等级为空
    '规格ID': ['1001', '1002', '1003', '1004'],
    '储存方式': ['储存方式：密封冰箱冷藏', '储存方式：密封冰箱冷藏', '储存方式：密封冰箱冷藏', '储存方式：密封阴凉处'],
    'pingyin': ['jnbl', 'dmxy', 'xjrqhz', 'wysyc'],
    '子项': ['', '', '', '']
}

# 模拟订单数据
test_order_data = {
    '规格ID': ['1001', '1002', '1003', '1004'],
    'SKU件数': [1, 1, 1, 1],
    'SKU名称': ['建宁白莲', '椴木小银耳', '新疆若羌红枣', '武夷山岩茶']
}

def test_label_assembly():
    print("测试标签组装逻辑...")
    
    # 创建模拟的商品配置DataFrame
    goods_df = pd.DataFrame(test_goods_data)
    
    # 创建模拟的订单DataFrame
    order_df = pd.DataFrame(test_order_data)
    
    # 模拟DoXHS函数中的数据处理逻辑
    rows = []
    for index, row in order_df.iterrows():
        guige_id = row['规格ID']
        sku_quantity = row['SKU件数']
        
        for idx, goods_row in goods_df.iterrows():
            if goods_row['规格ID'] == guige_id:
                row_data = goods_row.copy()
                row_data['sku_quantity'] = sku_quantity
                rows.append(row_data)
                break
    
    print(f"生成了 {len(rows)} 个测试标签数据")
    
    # 测试标签组装
    for i, item in enumerate(rows):
        print(f"\n测试标签 {i+1}: {item['成分']}")
        print(f"等级值: '{item['等级']}'")
        print(f"等级值类型: {type(item['等级'])}")
        print(f"等级值是否为空: {not item['等级']}")
        
        info = {}
        
        # 获取标签纸类型和尺寸
        label_type = test_config.get('labelType', 'new')
        label_sizes = test_config.get('labelSizes', {'new': {'width': 50, 'height': 80}})
        label_size = label_sizes.get(label_type, label_sizes.get('new', {'width': 50, 'height': 80}))
        
        # 获取横向打印配置
        is_landscape = test_config.get('isLandscape', True)
        
        info['width'] = label_size['width']
        info['height'] = label_size['height']
        info['fontHeight'] = 2.5
        info['text'] = []
        
        # 设置打印方向，横向模式下右转90度
        if is_landscape:
            info['orientation'] = 90
        else:
            info['orientation'] = 0
        
        # 初始化y坐标
        y_pos = 1.5
        line_height = 4
        
        # 根据标签纸类型组装数据
        if label_type == 'new':
            # 检查是否为横向打印模式
            if is_landscape:
                # 横向打印模式：右转90度，整个标签会旋转
                # 旋转后，标签的宽度和高度互换，坐标系也会旋转
                # 因此需要按照旋转后的实际情况来设计布局
                y_pos = 1.5
                line_height = 4
                
                # 标题部分
                info['text'].append({'text': item['成分'], 'x': 2, 'y': y_pos})
                y_pos += line_height
                
                # 基本信息部分 - 两行布局
                info['text'].append({'text': f'{item["规格"]}  {item["净重"]}', 'x': 2, 'y': y_pos})
                y_pos += line_height
                
                info['text'].append({'text': f'{item["产地"]}  {item["保质期"]}', 'x': 2, 'y': y_pos})
                y_pos += line_height
                
                # 包装日期和等级
                import datetime
                diy_date = ""
                if diy_date != "":
                    info['text'].append({'text': f'包装日期：{diy_date}', 'x': 2, 'y': y_pos})
                else:
                    info['text'].append({'text': f'包装日期：{datetime.datetime.now().strftime("%Y-%m-%d")}', 'x': 2, 'y': y_pos})
                
                # 如果等级为空，默认显示"等级：优"
                try:
                    level_value = item['等级']
                    level_text = level_value if str(level_value).strip() else '等级：优'
                except:
                    level_text = '等级：优'
                
                info['text'].append({'text': level_text, 'x': 30, 'y': y_pos})
                y_pos += line_height
                
                # 储存方式
                info['text'].append({'text': item['储存方式'], 'x': 2, 'y': y_pos})
                y_pos += line_height
                
                # 销售商和电话
                info['text'].append({'text': '销售商：福建省泉州市保康滋补商行', 'x': 2, 'y': y_pos})
                y_pos += line_height
                info['text'].append({'text': '电话：18396188860（微信同号）', 'x': 2, 'y': y_pos})
                y_pos += line_height
                
                # 温馨提示和食用方法
                if item['成分']=='成分：椴木小银耳':
                    info['text'].append({'text': '温馨提示：对银耳过敏者不可食用！本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                elif item['成分']=='成分：建宁白莲':
                    info['text'].append({'text': '食用方法：不需要浸泡！冲洗干净直接煮即可，泡了反而煮不粉。普通锅具煮40分钟，高压锅煮15分钟。可煮粥、打豆浆、煲汤，做糖水。' + '\n' +  '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                else:
                    info['text'].append({'text': '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
            else:
                # 纵向打印模式：每一项独立一行
                if item['sku_quantity'] > 1:
                    info['text'].append({'text': item['sku_quantity'], 'x': 48, 'y': y_pos})
                    y_pos += line_height

                info['text'].append({'text': item['成分'], 'x': 2, 'y': y_pos})
                y_pos += line_height

                info['text'].append({'text': item['规格'], 'x': 2, 'y': y_pos})
                y_pos += line_height

                info['text'].append({'text': item['净重'], 'x': 2, 'y': y_pos})
                y_pos += line_height

                info['text'].append({'text': item['产地'], 'x': 2, 'y': y_pos})
                y_pos += line_height

                info['text'].append({'text': item['保质期'], 'x': 2, 'y': y_pos})
                y_pos += line_height

                import datetime
                diy_date = ""
                if diy_date != "":
                    info['text'].append({'text': '包装日期：' + diy_date, 'x': 2, 'y': y_pos})
                else:
                    info['text'].append({'text': '包装日期：' + datetime.datetime.now().strftime('%Y-%m-%d'), 'x': 2, 'y': y_pos})
                y_pos += line_height
      
                # 如果等级为空，默认显示"等级：优"
                try:
                    level_value = item['等级']
                    level_text = level_value if str(level_value).strip() else '等级：优'
                except:
                    level_text = '等级：优'
                info['text'].append({'text': level_text, 'x': 2, 'y': y_pos})
                y_pos += line_height

                info['text'].append({'text': item['储存方式'], 'x': 2, 'y': y_pos})
                y_pos += line_height

                info['text'].append({'text': '销售商：福建省泉州市保康滋补商行', 'x': 2, 'y': y_pos})
                y_pos += line_height

                info['text'].append({'text': '电话：18396188860（微信同号）', 'x': 2, 'y': y_pos})
                y_pos += line_height
                
                if item['成分']=='成分：椴木小银耳':
                    info['text'].append({'text': '温馨提示：对银耳过敏者不可食用！本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                    y_pos += line_height
                elif item['成分']=='成分：建宁白莲':
                    info['text'].append({'text': '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。' + '\n' + '食用方法：不需要浸泡！冲洗干净直接煮即可，泡了反而煮不粉。普通锅具煮40分钟，高压锅煮15分钟。可煮粥、打豆浆、煲汤，做糖水。', 'x': 2, 'y': y_pos})
                    y_pos += line_height
                else:
                    info['text'].append({'text': '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                    y_pos += line_height
        
        # 打印标签信息
        print(f"标签尺寸: 宽={info['width']}, 高={info['height']}")
        print(f"标签内容行数: {len(info['text'])}")
        print("标签内容:")
        for line in info['text']:
            print(f"  [{line['x']}, {line['y']}]: {line['text']}")
        
        # 验证特殊处理
        if item['成分'] == '成分：建宁白莲':
            # 检查是否包含食用方法
            has_usage = any('食用方法' in line['text'] for line in info['text'])
            print(f"✓ 建宁白莲特殊处理: {'包含食用方法' if has_usage else '缺少食用方法'}")
        
        print("-" * 50)

def test_config_loading():
    print("\n测试配置加载...")
    
    # 测试配置文件读取
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✓ 配置文件读取成功")
        print(f"  标签类型: {config.get('labelType', 'new')}")
        print(f"  新标签尺寸: {config.get('labelSizes', {}).get('new', {})}")
        print(f"  旧标签尺寸: {config.get('labelSizes', {}).get('old', {})}")
    except Exception as e:
        print(f"✗ 配置文件读取失败: {e}")

if __name__ == "__main__":
    print("开始测试标签系统...")
    print("=" * 60)
    
    test_config_loading()
    test_label_assembly()
    
    print("=" * 60)
    print("测试完成！")
