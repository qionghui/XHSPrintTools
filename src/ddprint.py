# 第一部分：准备阶段

# 1.1 导入 DTPWeb 接口
from dtpweb import DTPWeb


 

def print_text(info):
    # 1.2 创建接口实例
    api = DTPWeb()
    # 1.3. 检查本地dtpweb打印助手是否启用，以及获取可用的端口号
    api.check_plugin()
    # 1.4. 获取打印机列表
    printers = api.get_printers()
    # 2.1 打开打印机
    api.open_printer(**printers[0])

    api.set_print_darkness(7.5)

    # 2.2 创建指定大小的打印（标签）任务，相关操作单位为毫米。
    api.start_job(width=info["width"], height=info["height"])
    # 2.3 绘制文本信息
    for text in info['text']:
        if str(text['text']).lower() == 'nan':  # 修复：比较字符串应使用小写的 'nan'，但通常不应与字符串 'NaN' 比较，此处假设意图是处理非数字情况
            continue
        # 注意：当在commit_job中设置orientation=90时，整个标签会旋转90度
        # 因此在draw_text中不需要再设置orientation参数，否则会导致双重旋转
        api.draw_text(text['text'], x=text['x'], y=text['y'], width= 50 - 2, height=40, fontHeight=info['fontHeight'])
        #api.draw_text("德佟电子", width=40, height=30, fontHeight = 3.5)
    # 2.4 提交打印任务，开始打印
    # 从info中获取打印方向，默认为0（不旋转）
    orientation = info.get('orientation', 0)
    api.commit_job(orientation=orientation)
    # 2.5 根据实际情况，关闭打印机
    # 如果还有后续打印，不需要关闭，如果不需要打印，为了避免影响其他用户使# 用打印机，可以关闭打印机。
    api.close_printer()



def doTest():
    info ={}

    info['width'] = 50
    info['height'] = 40
    info['fontHeight'] = 2.5
    info['text'] = []

    info['text'].append({'text': '成分：椴木小银耳', 'x': 2, 'y': 1.5 + 4*0})

    info['text'].append({'text': '规格：散装称重', 'x': 2, 'y': 1.5 + 4*1})
    info['text'].append({'text': '净重：250克', 'x': 30.4, 'y': 1.5 + 4*1})

    info['text'].append({'text': '产地：福建宁德古田县', 'x': 2, 'y': 1.5 + 4*2})
    info['text'].append({'text': '保质期：6个月', 'x': 30.4, 'y': 1.5 + 4*2})

    info['text'].append({'text': '包装日期：2025-02-20', 'x': 2, 'y': 1.5 + 4*3})
    info['text'].append({'text': '等级：AAA', 'x': 30.4, 'y': 1.5 + 4*3})


    info['text'].append({'text': '储存方式：密封冰箱冷藏', 'x': 2, 'y': 1.5 + 4*4})

    info['text'].append({'text': '销售商：福建省泉州市保康滋补商行', 'x': 2, 'y': 1.5 + 4*5})
    info['text'].append({'text': '联系方式：19559547271', 'x': 2, 'y': 1.5 + 4*6})
    info['text'].append({'text': '温馨提示：本店所受农产品属于初级农产品，代客分装，散装称重，包装是为了方便运输赠送。', 'x': 2, 'y': 1.5 + 4*7})


    print_text(info)



def draw_vertical_text(api, text, x, y, fontHeight, line_gap=1):
    """
    将字符串竖排绘制
    """
    current_y = y
    for char in text:
        api.draw_text(
            text=char,
            x=x,
            y=current_y,
            fontHeight=fontHeight,
            horizontalAlignment="Left"
        )
        current_y += fontHeight + line_gap


def print_text_Landscap(info):
    api = DTPWeb()
    api.check_plugin()
    printers = api.get_printers()

    if not printers:
        print("无打印机")
        return

    api.open_printer(**printers[0])
    api.set_print_darkness(7.5)

    # 物理尺寸 50 × 80
    api.start_job(width=50, height=80)

    for item in info['text']:
        text = item['text']
        if not text:
            continue

        draw_vertical_text(
            api=api,
            text=text,
            x=item['x'],
            y=item['y'],
            fontHeight=info['fontHeight']
        )

    api.commit_job(orientation=0)
    api.close_printer()


def doTestLandscape():
    info = {}
    info['fontHeight'] = 4
    info['text'] = []

    info['text'].append({'text': '成分：建宁白莲', 'x': 10, 'y': 5})

    print_text_Landscap(info)


 


def print_darkness(info):
    # 1.2 创建接口实例
    api = DTPWeb()
    # 1.3. 检查本地dtpweb打印助手是否启用，以及获取可用的端口号
    api.check_plugin()
    # 1.4. 获取打印机列表
    printers = api.get_printers()
    # 2.1 打开打印机
    api.open_printer(**printers[0])

    print(api.get_print_darkness())



if __name__ == "__main__":
    # 运行横向打印测试
    doTestLandscape()