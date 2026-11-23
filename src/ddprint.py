# 第一部分：准备阶段

# 1.1 导入 DTPWeb 接口
import contextlib
import io

from dtpweb import DTPWeb


def _clean_text(value):
    """统一处理 pandas/openpyxl 读出的空值与 NaN，避免把 'nan' 打到标签上。"""
    if value is None:
        return ''
    text = str(value).strip()
    if text.lower() in ('', 'nan', 'none', 'nat'):
        return ''
    return text


def print_text(info):
    """
    打印一张标签。

    dtpweb 内部会打印大量 request/response 调试信息，这里用 redirect_stdout
    统一静默；本函数自身不输出任何内容，由调用方打印一行友好结果。

    返回: (success: bool, error: str)
    """
    api = None
    printer_opened = False
    try:
        # dtpweb 的 print 都是直接打到 stdout，重定向即可静默，无需改动三方库
        with contextlib.redirect_stdout(io.StringIO()):
            api = DTPWeb()
            if not api.check_plugin():
                return False, '未检测到打印助手'
            printers = api.get_printers()
            if not printers:
                return False, '未发现可用打印机'

            printer = printers[0]
            if not api.open_printer(**printer):
                name = printer.get('name') or printer.get('deviceName') or '未知打印机'
                return False, '打开打印机失败：{}'.format(name)
            printer_opened = True

            api.set_print_darkness(7.5)

            if not api.start_job(width=info['width'], height=info['height']):
                return False, '创建打印任务失败'

            for text in info['text']:
                value = _clean_text(text.get('text'))
                if not value:
                    continue
                # 注意：orientation 在 commit_job 中设置，draw_text 不再设置，避免双重旋转
                if not api.draw_text(value, x=text['x'], y=text['y'],
                                     width=50 - 2, height=40, fontHeight=info['fontHeight']):
                    return False, '绘制标签内容失败'

            orientation = info.get('orientation', 0)
            # 非 json 模式下 resultInfo 可能是 None，只有明确 False 才算失败
            if api.commit_job(orientation=orientation) is False:
                return False, '提交打印任务失败'
            return True, ''
    except Exception as exc:
        return False, '{}: {}'.format(type(exc).__name__, exc)
    finally:
        if printer_opened and api is not None:
            with contextlib.redirect_stdout(io.StringIO()):
                try:
                    api.close_printer()
                except Exception:
                    pass



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