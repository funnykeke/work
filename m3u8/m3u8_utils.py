import logging
import os
import subprocess
import random
import time
import pytesseract
import cv2
from spellchecker import SpellChecker
import numpy as np
import shutil


# 获取视频总时长
def get_m3u8_duration(m3u8_url):
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of',
               'default=noprint_wrappers=1:nokey=1', '-i', m3u8_url]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=20).decode('utf-8')
        duration = float(output)
        return duration
    except Exception as e:
        logging.info(f'获取m3u8时长Error: {str(e)}')
        time.sleep(2)
        return None


def extract_frame(m3u8_url, time_point, output_file):
    command = ['ffmpeg', '-ss', str(time_point), '-i', m3u8_url, '-vframes', '1', '-q:v', '2', output_file]
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=20)
        print(f'Successfully extracted frame at time {time_point} seconds.')
    except Exception as e:
        logging.info(f'm3u8截图Error: {str(e)}')
        time.sleep(2)


# 从固定时间开始每隔4秒截图
def extract_frames_at_start_time(m3u8_url, time_start, num_frames, path):
    output_file = f'{path}\\frame_%d.jpg'
    command = ['ffmpeg', '-ss', f'{time_start}', '-i', m3u8_url, '-vf', 'fps=0.25', '-vframes',
               f'{num_frames}', '-q:v', '2', f'{output_file}']
    # print(command)
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=30).decode('utf-8')
        print(f'Successfully extracted frames')
    except Exception as e:
        logging.info(f'截图Error: {str(e)}')
        time.sleep(2)


# 随机截取保存m3u8_url的num_frames张图片
def extract_random_frames(m3u8_url, num_frames, path):
    # 获取视频总时长
    duration = get_m3u8_duration(m3u8_url)
    if duration is None:
        return
    # 生成随机时间点
    time_points = sorted(random.sample(range(int(duration)), num_frames))
    # 逐个截取视频帧
    for i, time_point in enumerate(time_points):
        output_file = f'{path}\\frame_{i + 1}.jpg'
        extract_frame(m3u8_url, time_point, output_file)


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


# 读取图像文件获取字幕单词集合
def extract_subtitle_text(image_path):
    # 读取图像文件
    src_img = cv2.imread(image_path)
    cap_region = caption_region_extr(src_img, 200, 0.8)
    # 使用pytesseract识别英文字幕
    text = pytesseract.image_to_string(cap_region, lang='chi_sim')
    # 返回识别的文本
    # print(text)
    spell_checker = SpellChecker()
    valid_words = spell_checker.known(text.split())
    return valid_words


# 判断m3u8视频是否存在英文字幕
def if_m3u8_exist_english_subtitle(m3u8_url, m3u8_name):
    path = f'E:\\m3u8\\{m3u8_name}'
    # 检查路径是否存在
    if os.path.exists(path):
        shutil.rmtree(path)  # 删除目录
    # 创建路径
    os.makedirs(path)
    # 截取图片
    extract_frames_at_start_time(m3u8_url, '00:09:00', 4, path)
    # extract_random_frames(m3u8_url, 4, path)
    has_english_subtitle = False
    for file in os.listdir(path):
        if has_english_subtitle:
            break
        if file.endswith('.jpg'):
            words = extract_subtitle_text(f'{path}\\{file}')
            if words.__len__() > 2:
                has_english_subtitle = True
    if os.path.exists(path):
        # for filename in os.listdir(path):
        #     file_path = os.path.join(path, filename)
        #     if os.path.isfile(file_path) and filename.endswith('.jpg'):
        #         os.remove(file_path)
        shutil.rmtree(path)
    if has_english_subtitle:
        # print(f'{m3u8_url}   ---{m3u8_name}---存在英文字幕')
        return True
    else:
        # print(f'{m3u8_url}   ---{m3u8_name}---无英文字幕')
        # shutil.rmtree(path)
        return False


# 下载m3u8视频
def download_m3u8_video(m3u8_url, path):
    print('正在下载视频')
    command = ['ffmpeg', '-i', m3u8_url, '-c', 'copy', path]
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        print(f'Successfully downloaded M3U8 video and saved as {path}.')
    except subprocess.CalledProcessError as e:
        logging.error(f'Error: {e.output.decode("utf-8")}')
        raise Exception

# if_m3u8_exist_english_subtitle('https://s7.fsvod1.com/20220830/8tdXlfCY/1200kb/hls/index.m3u8', 'ceshi')
