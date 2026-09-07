import os
import time
import pyautogui

file_path = r"E:\Work\NE.test\插件\编号字体不一致的问题还是存在\丢失引文-1.docx"
loop_count = 100

# 【重要】改成你电脑分辨率，最大化Word时右上角关闭按钮坐标
# 示例：1920*1080屏幕，最大化，关闭按钮大概 (1905,12)
CLOSE_BTN_X = 2550
CLOSE_BTN_Y = 12

for i in range(1, loop_count + 1):
    print(f"第 {i} 次打开文档")
    os.startfile(file_path)
    time.sleep(5)

    # 模拟鼠标移动到右上角关闭按钮，点击
    pyautogui.moveTo(CLOSE_BTN_X, CLOSE_BTN_Y, duration=0.2)
    pyautogui.click()

    time.sleep(5)

print("循环结束")