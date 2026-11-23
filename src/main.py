import json
import os
import pandas as pd
import sys
import shutil
import time
import ddprint
import datetime

import psutil
import paths

config = []
GoodsConfig = None
# 添加一个全局参数，是否打印特定日期
diy_date = ""


lock_file = paths.LOCK_FILE


def clean_text(value):
    """空值/NaN 统一转为空字符串，避免控制台和标签出现 nan。"""
    if value is None:
        return ''
    text = str(value).strip()
    return '' if text.lower() in ('', 'nan', 'none', 'nat') else text


def short_value(value):
    """去掉字段自带的“成分：/规格：/净重：”前缀，让提示更短。"""
    text = clean_text(value)
    if not text:
        return ''
    for sep in ('：', ':'):
        if sep in text:
            text = text.split(sep, 1)[-1].strip()
            break
    return text


def item_label(item):
    """生成一条打印结果用的简短商品描述。"""
    parts = [short_value(item.get(key)) for key in ('成分', '规格', '净重')]
    parts = [part for part in parts if part]
    if not parts:
        parts.append(clean_text(item.get('规格ID')) or '商品')
    return ' '.join(parts)


def print_result(label, success, error=''):
    """每张标签只打印一行友好结果，不输出库的调试信息。"""
    now = datetime.datetime.now().strftime('%H:%M:%S')
    if success:
        print('[{}] 已打印：{}'.format(now, label))
    else:
        print('[{}] 打印失败：{}（{}）'.format(now, label, error or '未知原因'))


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




def read_config(file_path=paths.CONFIG_FILE):
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
        label = item_label(item)
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
                except Exception:
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
                    info['text'].append({'text': '温馨提示：对银耳过敏者不可食用！本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                elif item['成分']=='成分：建宁白莲':
                    info['text'].append({'text': '食用方法：不需要浸泡！冲洗干净直接煮即可，泡了反而煮不粉。普通锅具煮40分钟，高压锅煮15分钟。可煮粥、打豆浆、煲汤，做糖水。' + '\n' +  '温馨提示：本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                else:
                    info['text'].append({'text': '温馨提示：本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
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
                except Exception:
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
                    info['text'].append({'text': '食用方法：小银耳冷水泡发30分钟~1个小时去除根部，剪碎越碎越好煮。银耳和水的比例1:5，高压锅大火煮上气转小火煮30分钟。电饭煲按"豆蹄筋"模式或者按2次煮饭键，时间到保温半个小时。不同锅具的功率不同炖煮时间也会有差异，只要时间够煮到银耳糯即可。' + '\n' + '\n' + '温馨提示：对银耳过敏者不可食用！本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                    y_pos += line_height
                elif item['成分']=='成分：建宁白莲':
                   info['text'].append({'text': '食用方法：不需要浸泡！冲洗干净直接煮即可，泡了反而煮不粉。普通锅具煮40分钟，高压锅煮15分钟。可煮粥、打豆浆、煲汤，做糖水。' + '\n' + '\n' +  '温馨提示：本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                   y_pos += line_height
                elif item['成分']=='成分：宁化糯薏米':
                   info['text'].append({'text': '食用方法：按稀饭的煮制方法，薏米和水的比例1：5，煮制完后可根据个人喜欢，开盖加入红枣、枸杞、白糖等配料，熬制越久效果越好。' + '\n' + '\n' +  '温馨提示：本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
                   y_pos += line_height
                else:
                    info['text'].append({'text': '温馨提示：本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': y_pos})
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
                except Exception:
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
                    info['text'].append({'text': '温馨提示：对银耳过敏者不可食用！本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})
                elif item['成分']=='成分：建宁白莲':
                    info['text'].append({'text': '食用方法：不需要浸泡！冲洗干净直接煮即可，泡了反而煮不粉。普通锅具煮40分钟，高压锅煮15分钟。可煮粥、打豆浆、煲汤，做糖水。' + '\n' +  '温馨提示：本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})
                else:
                    info['text'].append({'text': '温馨提示：本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})
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
                except Exception:
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
                    info['text'].append({'text': '温馨提示：对银耳过敏者不可食用！本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})
                elif item['成分']=='成分：建宁白莲':
                    info['text'].append({'text': '食用方法：不需要浸泡！冲洗干净直接煮即可，泡了反而煮不粉。普通锅具煮40分钟，高压锅煮15分钟。可煮粥、打豆浆、煲汤，做糖水。' + '\n' + '\n' +  '温馨提示：本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})
                else:
                    info['text'].append({'text': '温馨提示：本店所售农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': old_y_pos})


        success, error = ddprint.print_text(info)
        print_result(label, success, error)

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
    
    # 读取免打配置文件（正常流程保持静默）
    def read_exempt_config():
        try:
            config_path = paths.EXEMPT_CONFIG
            if not os.path.exists(config_path):
                return {}
            with open(config_path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        except Exception as e:
            print('[{}] 读取免打配置失败：{}'.format(
                datetime.datetime.now().strftime('%H:%M:%S'), e))
            return {}

    # 保存免打配置文件
    def save_exempt_config(exempt_config):
        try:
            # 过滤掉值为0或负数的项
            filtered_config = {k: v for k, v in exempt_config.items() if v > 0}
            with open(paths.EXEMPT_CONFIG, 'w', encoding='utf-8-sig') as f:
                json.dump(filtered_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print('[{}] 保存免打配置失败：{}'.format(
                datetime.datetime.now().strftime('%H:%M:%S'), e))
    
    # 处理免打配置
    def handle_exempt_config(item_ggid, exempt_config, deduct_count):
        """
        处理免打配置（仅对自动到来的订单生效）
        item_ggid: 商品规格ID
        exempt_config: 免打配置字典
        deduct_count: 本订单行实际应打印的贴纸数（单品=购买件数；组合装子项=件数*子项数量）
        返回: True=正常打印；False=整条订单命中免打，全部不打印
        扣减规则：命中即整条跳过，并按 deduct_count 扣减免打额度；额度不足覆盖本单时也整条跳过、额度清零
        """
        if item_ggid not in exempt_config:
            return True
        # 脏值容错：非整数 / <=0 视为无效配置，清除并正常打印
        try:
            exempt_count = int(exempt_config[item_ggid])
        except (TypeError, ValueError):
            exempt_config.pop(item_ggid, None)
            save_exempt_config(exempt_config)
            return True
        if exempt_count <= 0:
            exempt_config.pop(item_ggid, None)
            save_exempt_config(exempt_config)
            return True

        # 命中免打：整条订单不打印，按件数扣减
        try:
            deduct = max(1, int(deduct_count))
        except (TypeError, ValueError):
            deduct = 1
        remaining = exempt_count - deduct
        if remaining > 0:
            exempt_config[item_ggid] = remaining
        else:
            exempt_config.pop(item_ggid, None)
        save_exempt_config(exempt_config)
        return False
    
    # 错误提示方法
    def log_error(message, exit_process=False, order_excel_directory=None, current_file=None):
        """
        统一的错误提示方法
        message: 错误消息
        exit_process: 是否导致进程退出
        order_excel_directory: 订单Excel目录
        current_file: 当前处理的文件
        """
        detail = message
        if exit_process:
            extras = []
            if order_excel_directory:
                extras.append('订单目录：{}'.format(order_excel_directory))
            if current_file:
                extras.append('文件：{}'.format(current_file))
            if extras:
                detail += '（{}）'.format('；'.join(extras))
        print('[{}] 错误：{}'.format(datetime.datetime.now().strftime('%H:%M:%S'), detail))
    
    # 处理订单数据
    def process_order_data(AExcelFile, GoodsConfig, order_excel_directory, apply_exempt=True):
        """
        处理订单数据
        AExcelFile: Excel文件路径
        GoodsConfig: 商品配置DataFrame
        order_excel_directory: 订单Excel目录
        apply_exempt: 是否应用免打配置。自动订单=True；网页生成的手动打单/补打=False（用户显式要打，绕过免打且不扣减额度）
        返回: (是否成功, 处理后的商品列表, 免打配置)
        """
        rows = []
        # 仅自动订单读取并回写免打配置；手动单完全不碰免打配置
        exempt_config = read_exempt_config() if apply_exempt else {}
        # 打开 excel 文件
        df = pd.read_excel(AExcelFile)
        for index, row in df.iterrows():
            raw_ggid = ggid_field(row)
            if raw_ggid is None or str(raw_ggid).strip() == '':
                log_error(f'{index}行存在非法表格（规格ID为空），请检查', exit_process=True,
                         order_excel_directory=order_excel_directory, current_file=AExcelFile)
                return False, [], exempt_config
            # 统一为字符串，避免 pandas/openpyxl 数值类型差异导致匹配失败
            guige_id = str(raw_ggid).strip()
            # 数量安全转换（pandas 可能给出 int64/float64/None）
            try:
                sku_quantity = int(float(sku_quantity_field(row)))
            except (TypeError, ValueError):
                sku_quantity = 0
            if sku_quantity <= 0:
                continue

            found = False
            for idx, goods_row in GoodsConfig.iterrows():
                if str(goods_row['规格ID']).strip() == guige_id:
                    if isinstance(goods_row['子项'], str) and goods_row['子项'] != "": #子项代表组合项目，比如红枣*500*2 或者 红枣250*1+莲子250*1，存储的格式为 子项ggid#数量,子项ggid#数量
                        subitems = goods_row['子项'].split(',')
                        for subitem in subitems:
                            subitem_parts = subitem.split('#')
                            subitem_ggid = subitem_parts[0].strip()
                            subitem_quantity = int(subitem_parts[1])
                            for idx, goods_row_item in GoodsConfig.iterrows():
                                if str(goods_row_item['规格ID']).strip() == subitem_ggid:
                                    found = True
                                    # 组合装每个子项共打印 件数*子项数量 张贴纸；命中免打则该子项整条跳过
                                    sticker_count = sku_quantity * subitem_quantity
                                    if apply_exempt:
                                        should_print = handle_exempt_config(subitem_ggid, exempt_config, sticker_count)
                                    else:
                                        should_print = True
                                    if should_print:
                                        # 正常打印
                                        row_data = goods_row_item.copy()
                                        row_data['sku_quantity'] = sku_quantity
                                        for _ in range(sticker_count):
                                            rows.append(row_data)
                                    break
                    else:
                        found = True
                        row_data = goods_row
                        # 检查主项的免打配置
                        if apply_exempt:
                            should_print = handle_exempt_config(guige_id, exempt_config, sku_quantity)
                        else:
                            should_print = True
                        if should_print:
                            # 正常打印
                            for _ in range(sku_quantity):
                                row_data['sku_quantity'] = sku_quantity
                                rows.append(row_data)
                    break

            if not found:
                sku_name = clean_text(row.get('SKU名称')) if hasattr(row, 'get') else ''
                log_error('规格ID {}（{}）未在商品配置中找到'.format(guige_id, sku_name or '未知商品'))
                #使用默认软件打开GoodsConfig文件
                os.startfile(paths.GOODS_XLSX)

        return True, rows, exempt_config


    # 手动打单/补打（网页生成，文件名含“手动打单”）代表用户显式要打，绕过免打；自动订单才应用免打
    is_manual_order = '手动打单' in os.path.basename(AExcelFile)
    # 处理订单数据
    success, rows, exempt_config = process_order_data(AExcelFile, GoodsConfig, order_excel_directory, apply_exempt=not is_manual_order)
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
    def save_to_excel(rows, file_path=paths.LATEST_PRINT):
        """
        将商品列表保存为Excel文件
        rows: 商品列表
        file_path: 保存路径，默认为 paths.LATEST_PRINT（runtime/latest_print_file.xlsx）
        """
        rows_df = pd.DataFrame(rows)
        rows_df.to_excel(file_path, index=False)

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
    GoodsConfig = pd.read_excel(paths.GOODS_XLSX)

    if config is None:
        print('[{}] 错误：配置加载失败'.format(datetime.datetime.now().strftime('%H:%M:%S')))
        return False


    # 打印文件存储地址
    order_excel_directory = config['orderExcelDirectory']

    print_excel_directory = config['printExcelDirectory']
    
 
    paths.ensure_runtime_dirs()  # 确保 runtime/ 与 runtime/bak/ 存在
    backup_directory = paths.BAK_DIR

    
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
    lock_file_path = paths.LOCK_FILE

    check_lock_file(lock_file_path)
    create_lock_file(lock_file_path)

    if len(sys.argv) - 1 > 0:
        if sys.argv[1] == '--diy_date':
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

    
 
