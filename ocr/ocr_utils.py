import cv2
import numpy as np
import pytesseract
from PIL import Image


# 提取图像中的字幕区域
def caption_region_extr(src_img, thresh_, v_cut_ratio_):
    # 转换为灰度
    imgray = cv2.cvtColor(src_img, cv2.COLOR_BGR2GRAY)
    _, img_bn = cv2.threshold(imgray, thresh_, 255, cv2.THRESH_BINARY)
    # 垂直切割
    crop_start = int(v_cut_ratio_ * img_bn.shape[0])
    v_cut_img = img_bn[crop_start:, :]
    # 水平切割
    h_projection = np.any(v_cut_img > 0, axis=0)
    h_left = np.argmax(h_projection)
    h_right = np.argmin(h_projection[::-1])
    h_right = v_cut_img.shape[1] - 1 - h_right
    if h_right - h_left > 20:
        # 扩展边界
        h_left = max(h_left - 10, 0)
        h_right = min(h_right + 10, v_cut_img.shape[1] - 1)
        h_cut_img = v_cut_img[:, h_left:h_right + 1]
    else:
        h_cut_img = np.zeros((1, 1), dtype=np.uint8)
    # 存储提取的字幕图像
    # output_image_path = 'caption_image.jpg'
    # cv2.imwrite(output_image_path, h_cut_img)
    return h_cut_img


def extract_text(image_path):
    # 读取图像文件
    # src_img = cv2.imread(image_path)
    # 读取验证码图片
    image = Image.open(image_path)
    # 将图片转为灰度图像
    image = image.convert('L')
    # cap_region = caption_region_extr(src_img, 200, 0.8)
    # 使用pytesseract识别英文字幕
    # 对图像进行二值化处理
    threshold = 127
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    image = image.point(table, '1')
    text = pytesseract.image_to_string(image)
    # 返回识别的文本
    print(text)

extract_text('GetValidateCode.jpg')
