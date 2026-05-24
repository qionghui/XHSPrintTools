import json
import os
import pandas as pd
import sys
import shutil
import time
import ddPrint
import datetime

import psutil

config = []
GoodsConfig = None
# 添加一个全局参数，是否打印特定日期
diy_date = ""


lock_file = 'lock.txt'


#!/usr/bin/env python3
 

def check_lock_file(lock_file_path):
    if os.path.exists(lock_file_path):
        with open(lock_file_path, 'r') as f:
            pid = f.read().strip()
            try:
                p = psutil.Process(int(pid))
                p.is_running()  # 这将引发NoSuchProcess异常，如果进程不存在
                print(f'Error: Another instance of the script is already running with PID {pid}.')  
                sys.exit(1)
            except psutil.NoSuchProcess:
                return False  # Process no longer exists, we can safely create a new lock file

def create_lock_file(lock_file_path):
    try:
        with open(lock_file_path, 'w') as f:
            # Note: No fcntl used here, so no locking mechanism is implemented.
            f.write(str(os.getpid()))
    except IOError as e:
        # Handle the case where the file is already locked or cannot be written to
        print(f'Error creating lock file: {e}')
        # Optionally re-raise the exception or handle it further

def remove_lock_file(lock_file_path):
    try:
        os.remove(lock_file_path)
    except OSError as e:
        if e.errno != os.errno.ENOENT:
            raise




def read_config(file_path='config.json'):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config_dict = json.load(file)
        return config_dict
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: File {file_path} is not a valid JSON file.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# 处理打印函数
def process_printing(rows, config, diy_date):
    """
    处理打印逻辑
    rows: 商品列表
    config: 配置字典
    diy_date: 自定义日期
    """
    for item in rows:
        print(item)

        info ={}

        # 获取标签纸类型和尺寸
        label_type = config.get('labelType', 'new')
        label_sizes = config.get('labelSizes', {'new': {'width': 50, 'height': 80}})
        label_size = label_sizes.get(label_type, label_sizes.get('new', {'width': 50, 'height': 80}))
        
        # 获取横向打印配置
        is_landscape = config.get('isLandscape', True)
        
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
        line_height = 5
        
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
                if diy_date != "":
                    info['text'].append({'text': f'包装日期：{diy_date}', 'x': 2, 'y': y_pos})
                else:
                    info['text'].append({'text': f'包装日期：{datetime.datetime.now().strftime("%Y-%m-%d")}', 'x': 2, 'y': y_pos})
                
                # 如果等级为空，默认显示"等级：优"
                try:
                    level_value = item['等级']
                    # 严格检查值是否为空或NaN
                    if level_value is None or str(level_value).strip() == '' or str(level_value).strip().lower() == 'nan':
                        level_text = '等级：优'
                    else:
                        level_text = str(level_value)
                    print(f"等级处理: {level_value} -> {level_text}")
                except Exception as e:
                    print(f"等级处理异常: {e}")
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
                if item.get('sku_quantity', 1) > 1:
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

                if diy_date != "":
                    info['text'].append({'text': '包装日期：' + diy_date, 'x': 2, 'y': y_pos})
                else:
                    info['text'].append({'text': '包装日期：' + datetime.datetime.now().strftime('%Y-%m-%d'), 'x': 2, 'y': y_pos})
                y_pos += line_height
          
                # 如果等级为空，默认显示"等级：优"
                try:
                    level_value = item['等级']
                    # 严格检查值是否为空或NaN
                    if level_value is None or str(level_value).strip() == '' or str(level_value).strip().lower() == 'nan':
                        level_text = '等级：优'
                    else:
                        level_text = str(level_value)
                    print(f"等级处理: {level_value} -> {level_text}")
                except Exception as e:
                    print(f"等级处理异常: {e}")
                    level_text = '等级：优'
                info['text'].append({'text': level_text, 'x': 2, 'y': y_pos})
                y_pos += line_height

                info['text'].append({'text': item['储存方式'], 'x': 2, 'y': y_pos})
                y_pos += line_height

                info['text'].append({'text': '销售商：福建省泉州市保康滋补商行', 'x': 2, 'y': y_pos})
                y_pos += line_height

                info['text'].append({'text': '电话：18396188860（微信同号）', 'x': 2, 'y': y_pos})
                y_pos += line_height
                
                if (item['成分']=='成分：椴木小银耳') or (item['成分']=='成分：椴木小银耳碎'):
                    info['text'].append({'text': '食用方法：小银耳冷水泡发30分钟~1个小时去除根部，剪碎越碎越好煮。银耳和水的比例1:5，高压锅大火煮上气转小火煮30分钟。电饭煲按"豆蹄筋"模式或者按2次煮饭键，时间到保温半个小时。不同锅具的功率不同炖煮时间也会有差异，只要时间够煮到银耳糯即可。' + '\n' + '\n' + '温馨提示：对银耳过敏者不可食用！本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                    y_pos += line_height
                elif item['成分']=='成分：建宁白莲':
                   info['text'].append({'text': '食用方法：不需要浸泡！冲洗干净直接煮即可，泡了反而煮不粉。普通锅具煮40分钟，高压锅煮15分钟。可煮粥、打豆浆、煲汤，做糖水。' + '\n' + '\n' +  '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                   y_pos += line_height
                elif item['成分']=='成分：宁化糯薏米':
                   info['text'].append({'text': '食用方法：按稀饭的煮制方法，薏米和水的比例1：5，煮制完后可根据个人喜欢，开盖加入红枣、枸杞、白糖等配料，熬制越久效果越好。' + '\n' + '\n' +  '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                   y_pos += line_height
                else:
                    info['text'].append({'text': '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                    y_pos += line_height
        else:
            # 旧标签纸：使用动态y坐标计算
            if is_landscape:
                # 旧标签纸横向打印模式
                old_y_pos = 1.5
                old_line_height = 4
                
                # 标题部分
                info['text'].append({'text': item['成分'], 'x': 2, 'y': old_y_pos})
                old_y_pos += old_line_height
                
                # 基本信息部分
                info['text'].append({'text': f'{item["规格"]}  {item["净重"]}', 'x': 2, 'y': old_y_pos})
                old_y_pos += old_line_height
                
                info['text'].append({'text': f'{item["产地"]}  {item["保质期"]}', 'x': 2, 'y': old_y_pos})
                old_y_pos += old_line_height
                
                # 包装日期和等级
                if diy_date != "":
                    info['text'].append({'text': f'包装日期：{diy_date}', 'x': 2, 'y': old_y_pos})
                else:
                    info['text'].append({'text': f'包装日期：{datetime.datetime.now().strftime("%Y-%m-%d")}', 'x': 2, 'y': old_y_pos})
                
                # 如果等级为空，默认显示"等级：优"
                try:
                    old_level_value = item['等级']
                    # 严格检查值是否为空或NaN
                    if old_level_value is None or str(old_level_value).strip() == '' or str(old_level_value).strip().lower() == 'nan':
                        old_level_text = '等级：优'
                    else:
                        old_level_text = str(old_level_value)
                    print(f"旧标签等级处理: {old_level_value} -> {old_level_text}")
                except Exception as e:
                    print(f"旧标签等级处理异常: {e}")
                    old_level_text = '等级：优'
                info['text'].append({'text': old_level_text, 'x': 30.4, 'y': old_y_pos})

                old_y_pos += old_line_height
                info['text'].append({'text': item['储存方式'], 'x': 2, 'y': old_y_pos})

                old_y_pos += old_line_height
                info['text'].append({'text': '销售商：福建省泉州市保康滋补商行', 'x': 2, 'y': old_y_pos})

                old_y_pos += old_line_height
                info['text'].append({'text': '电话：18396188860（微信同号）', 'x': 2, 'y': old_y_pos})
                
                old_y_pos += old_line_height
                if item['成分']=='成分：椴木小银耳':
                    info['text'].append({'text': '温馨提示：对银耳过敏者不可食用！本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})
                elif item['成分']=='成分：建宁白莲':
                    info['text'].append({'text': '食用方法：不需要浸泡！冲洗干净直接煮即可，泡了反而煮不粉。普通锅具煮40分钟，高压锅煮15分钟。可煮粥、打豆浆、煲汤，做糖水。' + '\n' +  '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})
                else:
                    info['text'].append({'text': '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})
            else:
                # 旧标签纸纵向打印模式
                old_y_pos = 1.5
                old_line_height = 4
                
                if item.get('sku_quantity', 1) > 1:
                    info['text'].append({'text': item['sku_quantity'], 'x': 48, 'y': old_y_pos})

                info['text'].append({'text': item['成分'], 'x': 2, 'y': old_y_pos})

                old_y_pos += old_line_height
                info['text'].append({'text': item['规格'], 'x': 2, 'y': old_y_pos})
                info['text'].append({'text': item['净重'], 'x': 30.4, 'y': old_y_pos})

                old_y_pos += old_line_height
                info['text'].append({'text': item['产地'], 'x': 2, 'y': old_y_pos})
                info['text'].append({'text': item['保质期'], 'x': 30.4, 'y': old_y_pos})

                old_y_pos += old_line_height
                if diy_date != "":
                    info['text'].append({'text': '包装日期：' + diy_date, 'x': 2, 'y': old_y_pos})
                else:
                    info['text'].append({'text': '包装日期：' + datetime.datetime.now().strftime('%Y-%m-%d'), 'x': 2, 'y': old_y_pos})
          
                # 如果等级为空，默认显示"等级：优"
                try:
                    old_level_value = item['等级']
                    # 严格检查值是否为空或NaN
                    if old_level_value is None or str(old_level_value).strip() == '' or str(old_level_value).strip().lower() == 'nan':
                        old_level_text = '等级：优'
                    else:
                        old_level_text = str(old_level_value)
                    print(f"旧标签等级处理: {old_level_value} -> {old_level_text}")
                except Exception as e:
                    print(f"旧标签等级处理异常: {e}")
                    old_level_text = '等级：优'
                info['text'].append({'text': old_level_text, 'x': 30.4, 'y': old_y_pos})

                old_y_pos += old_line_height
                info['text'].append({'text': item['储存方式'], 'x': 2, 'y': old_y_pos})

                old_y_pos += old_line_height
                info['text'].append({'text': '销售商：福建省泉州市保康滋补商行', 'x': 2, 'y': old_y_pos})

                old_y_pos += old_line_height
                info['text'].append({'text': '电话：18396188860（微信同号）', 'x': 2, 'y': old_y_pos})
                
                old_y_pos += old_line_height
                if item['成分']=='成分：椴木小银耳':
                    info['text'].append({'text': '温馨提示：对银耳过敏者不可食用！本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})
                elif item['成分']=='成分：建宁白莲':
                    info['text'].append({'text': '食用方法：不需要浸泡！冲洗干净直接煮即可，泡了反而煮不粉。普通锅具煮40分钟，高压锅煮15分钟。可煮粥、打豆浆、煲汤，做糖水。' + '\n' + '\n' +  '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})
                else:
                    info['text'].append({'text': '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})


        ddPrint.print_text(info)

def DoXHS(AExcelFile, order_excel_directory):
    def ggid_field(row):
        for field in config["ggid_field"]:
            for col in row.keys():
                if field.strip() == col.strip():
                    return row[col]
    def sku_quantity_field(row):
        for field in config["num_field"]:
            for col in row.keys():
                if field.strip() == col.strip():
                    return row[col]
    
    # 读取免打配置文件
    def read_exempt_config():
        try:
            print(f"当前工作目录: {os.getcwd()}")
            config_path = os.path.join(os.getcwd(), 'exempt_config.json')
            print(f"配置文件路径: {config_path}")
            print(f"配置文件是否存在: {os.path.exists(config_path)}")
            
            if os.path.exists(config_path):
                with open('exempt_config.json', 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                    print(f"配置文件原始内容: {content}")
                    config = json.loads(content)
                    print(f"解析后的配置: {config}")
                    return config
            else:
                print("配置文件不存在")
                return {}
        except FileNotFoundError:
            print("配置文件不存在 (FileNotFoundError)")
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return {}
        except Exception as e:
            print(f"读取配置文件时发生错误: {e}")
            return {}
    
    # 保存免打配置文件
    def save_exempt_config(exempt_config):
        try:
            # 过滤掉值为0或负数的项
            filtered_config = {k: v for k, v in exempt_config.items() if v > 0}
            with open('exempt_config.json', 'w', encoding='utf-8-sig') as f:
                json.dump(filtered_config, f, indent=2, ensure_ascii=False)
            print(f"保存免打配置: {filtered_config}")
        except Exception as e:
            print(f"保存免打配置失败: {e}")
    
    # 处理免打配置
    def handle_exempt_config(item_ggid, exempt_config, row_data, sku_quantity, subitem_quantity=None):
        """
        处理免打配置
        item_ggid: 商品规格ID
        exempt_config: 免打配置字典
        row_data: 商品数据
        sku_quantity: SKU数量
        subitem_quantity: 子项数量（可选）
        返回: 是否需要添加到打印列表
        """
        if item_ggid in exempt_config:
            exempt_count = exempt_config[item_ggid]
            if exempt_count > 0:
                print(f"跳过打印 {item_ggid}，剩余免打次数: {exempt_count - 1}")
                new_exempt_count = exempt_count - 1
                if new_exempt_count > 0:
                    exempt_config[item_ggid] = new_exempt_count
                else:
                    # 免打次数减完为0，移除该配置
                    print(f"移除 {item_ggid} 的免打配置")
                    del exempt_config[item_ggid]
                save_exempt_config(exempt_config)
                return False  # 跳过打印
        else:
            return True  # 没有免打配置，正常打印
    
    # 错误提示方法
    def log_error(message, exit_process=False, order_excel_directory=None, current_file=None):
        """
        统一的错误提示方法
        message: 错误消息
        exit_process: 是否导致进程退出
        order_excel_directory: 订单Excel目录
        current_file: 当前处理的文件
        """
        print("=" * 50)
        print(f"【错误提示】{message}")
        if exit_process:
            print("=" * 50)
            if order_excel_directory:
                print(f"1. 读取excel的文档目录: {order_excel_directory}")
            if current_file:
                print(f"2. 本次读取的excel文件: {current_file}")
            print("3. 提示语：请尝试删除目录文件中的所有excel文件进行后重试")
            print("=" * 50)
    
    # 处理订单数据
    def process_order_data(AExcelFile, GoodsConfig, order_excel_directory):
        """
        处理订单数据
        AExcelFile: Excel文件路径
        GoodsConfig: 商品配置DataFrame
        order_excel_directory: 订单Excel目录
        返回: (是否成功, 处理后的商品列表, 免打配置)
        """
        rows = []
        # 读取免打配置
        exempt_config = read_exempt_config()
        # 打开 excel 文件
        df = pd.read_excel(AExcelFile)
        for index, row in df.iterrows():
            guige_id = ggid_field(row)
            if guige_id is None:
                print(f'{index}行存在非法表格，请检查')
                log_error(f'{index}行存在非法表格（规格ID为空），请检查', exit_process=True, 
                         order_excel_directory=order_excel_directory, current_file=AExcelFile)
                return False, [], exempt_config
            #
            sku_quantity = sku_quantity_field(row)            

            found = False
            for idx, goods_row in GoodsConfig.iterrows():
                if goods_row['规格ID'] == guige_id:
                    if isinstance(goods_row['子项'], str) and goods_row['子项'] != "": #子项代表组合项目，比如红枣*500*2 或者 红枣250*1+莲子250*1，存储的格式为 子项ggid#数量,子项ggid#数量
                        print('子项存在')
                        print(goods_row['子项'])
                        print(goods_row['规格ID'])
                        subitems = goods_row['子项'].split(',')
                        for subitem in subitems:
                            subitem_parts = subitem.split('#')
                            subitem_ggid = subitem_parts[0].strip()
                            print(subitem_ggid)
                            subitem_quantity = int(subitem_parts[1])
                            for idx, goods_row_item in GoodsConfig.iterrows():
                                if goods_row_item['规格ID'] == subitem_ggid:
                                    row_data = goods_row_item
 
                                    row_data['sku_quantity'] = sku_quantity
                                    found = True
                                    # 检查子项的免打配置
                                    should_print = handle_exempt_config(subitem_ggid, exempt_config, row_data, sku_quantity, subitem_quantity)
                                    if should_print:
                                        # 正常打印
                                        for _ in range(sku_quantity * subitem_quantity):
                                            rows.append(row_data)
                                    break
                    else:
                        found = True
                        row_data = goods_row
                        # 检查主项的免打配置
                        print(f"当前规格ID: {guige_id}")
                        print(f"免打配置: {exempt_config}")
                        should_print = handle_exempt_config(str(guige_id), exempt_config, row_data, sku_quantity)
                        if should_print:
                            # 正常打印
                            for _ in range(sku_quantity):
                                row_data['sku_quantity'] = sku_quantity
                                rows.append(row_data)
                    break

            if not found:
                print(f'{guige_id} 的 SKU 名称 "{row["SKU名称"]}" 没有在 GoodsConfig 中找到')
                #使用默认软件打开GoodsConfig文件
                os.startfile("goods.xlsx")
        
        return True, rows, exempt_config


    # 处理订单数据
    success, rows, exempt_config = process_order_data(AExcelFile, GoodsConfig, order_excel_directory)
    if not success:
        return False

    # 判断rows是否超过20条，如果是，则等待用户输入y/n
    # if len(rows) > 20:
    #     user_input = input("此次打印超过20条，输入y继续打印，输入n终止打印，并将文件存放到备份目录（y/n）: ")
    #     if user_input.lower() == 'n':
    #        print("Operation cancelled by user.")
    #         # 可以在这里添加取消操作后的逻辑
    #        return True
    #    # 如果输入不是'n'，则继续执行后续逻辑
    if len(rows) == 0:
        return True

    # 排序函数
    def sort_rows(rows):
        """
        对rows进行排序，按照成分、规格、净重(取数字部分)、等级排序
        rows: 商品列表
        返回: 排序后的商品列表
        """
        rows.sort(key=lambda item: (
            str(item['成分']), 
            str(item['规格']), 
            float(''.join(filter(str.isdigit, str(item['净重'])))) if item['净重'] and ''.join(filter(str.isdigit, str(item['净重']))) else 0.0,
            str(item['等级'])
        ))
        return rows

    # 对rows进行排序
    rows = sort_rows(rows)

    # 保存Excel文件函数
    def save_to_excel(rows, file_path='./latest_print_file.xlsx'):
        """
        将商品列表保存为Excel文件
        rows: 商品列表
        file_path: 保存路径，默认为'./latest_print_file.xlsx'
        """
        rows_df = pd.DataFrame(rows)
        rows_df.to_excel(file_path, index=False)
        print(f"已保存到 {file_path}")

    # 保存到Excel文件
    save_to_excel(rows)

    # 处理打印
    process_printing(rows, config, diy_date)
 



    return True

def main():
    global GoodsConfig
    global config

    config = read_config()
    #此次修改为从goods.xlsx读取配置
    GoodsConfig = pd.read_excel("goods.xlsx")

    if config is None:
        print("Failed to load config.")



    # 打印文件存储地址
    order_excel_directory = config['orderExcelDirectory']

    print_excel_directory = config['printExcelDirectory']
    
 
    script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录
    backup_directory = os.path.join(script_dir, 'bak')
    os.makedirs(backup_directory, exist_ok=True)  # 如果目录不存在则创建

    
    # 遍历目录
    for filename in os.listdir(order_excel_directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(order_excel_directory, filename)
            #print_file_path = os.path.join(print_excel_directory, filename)
            if not DoXHS(file_path, order_excel_directory):
                return False
            
            #backup_directory = config['orderExcelBackupDirectory']
            backup_file_path = os.path.join(backup_directory, filename)
            # 备份文件到备份目录
            shutil.copy(file_path, backup_file_path)
            os.remove(file_path)
 
            # 打开文件夹（在文件浏览器中打开，取决于操作系统）
            #os.startfile(print_excel_directory)

    return True


if __name__ == "__main__":
    lock_file_path = 'application.lock'

    check_lock_file(lock_file_path)
    create_lock_file(lock_file_path)

    print(f"传入的参数数量：{len(sys.argv) - 1}")
    print(f"传入的参数列表：{sys.argv[1:]}")
    if len(sys.argv) - 1 > 0:
        if sys.argv[1] == '--diy_date':
            print(f"打印自定义日期")
 
            while True:
                date_str = input("请输入自定义日期，格式为YYYY-MM-DD: ")
                try:
                    # 尝试将输入字符串转换为日期对象，验证格式和合法性

                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    diy_date = str(date_obj.date())
                    print(f"您输入的日期是: {diy_date}")

                    break
                except ValueError:
                    print("输入的日期格式不正确，请重新输入！")
 
            
    try:
        while True:
            if main():
                time.sleep(10) 
                if diy_date != "":
                    print("程序退出：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    break
                print("程序运行正常：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                break
    finally:
        remove_lock_file(lock_file_path)

    
 
