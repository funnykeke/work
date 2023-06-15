import os
import time
import cv2
import numpy as np
import pytesseract
from Levenshtein import distance
from pytube import YouTube

video_url = 'https://www.youtube.com/watch?v=S3RqQEo9PiA'
lan_dict = {"en": "eng", "zh": "chi_sim", "ja": "jpn", "ko": "kor", "ru": "rus"}


# 获取两个字符串之间的相似度
def get_similarity(str1, str2):
    lev_distance = distance(str1, str2)
    return 1 - lev_distance / max(len(str1), len(str2))


# 根据url返回视频名，视频流，Capture
def get_video_by_url(video_url):
    # 下载YouTube视频
    video = YouTube(video_url, proxies={'https': '127.0.0.1:7890'})
    video_stream = video.streams.filter(adaptive=True, file_extension="mp4")
    print("下载完毕")
    # 处理视频流
    return video.title, video_stream.first(), cv2.VideoCapture(video_stream[0].url)


def get_video_capture_by_file(input_file):
    # 加载视频文件
    return cv2.VideoCapture(input_file)


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
    return h_cut_img


def process_subtitle(video_url, lan, out_path):
    # 字幕相似度比例，用于判断当前获取字幕是否与之前的一致，相似度高则认为不是字幕
    subtitle_similarity_ratio = 0.6
    # 存放获取到的字幕
    subtitle_list = []
    # 获取到的字母数量大于该数值则认为存在字幕
    is_subtitle_count = 4
    # 记录开始时间
    time_start = int(time.time())
    # 保存文件名
    title = ''
    try:
        title, video_stream, video_capture = get_video_by_url(video_url)
        # 视频总帧数
        total_frame = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        span = int(total_frame / 20)
        print(f"共{total_frame}帧,间隔{span}取帧")
        for x, index in enumerate(range(1, total_frame, span - 1)):
            if subtitle_list.__len__() >= is_subtitle_count:
                break
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            success, frame = video_capture.read()
            if success:
                # 获取字幕区域
                cap_region = caption_region_extr(frame, 200, 0.8)
                is_subtitle = True
                try:
                    text = pytesseract.image_to_string(cap_region, lang=lan_dict[lan])
                    # 字符数量小于5则认定不是字幕
                    if len(text) < 5:
                        is_subtitle = False
                    for subtitle in subtitle_list:
                        if get_similarity(subtitle, text) > subtitle_similarity_ratio:
                            is_subtitle = False
                            break
                    if is_subtitle:
                        subtitle_list.append(text)
                except Exception as e:
                    print(e)
                print(f'第{x}帧读取完毕,存在字幕' if is_subtitle else f'第{x}帧读取完毕,不存在字幕')
        video_capture.release()
    except Exception as e:
        print(e)
    time_end = int(time.time())
    if subtitle_list.__len__() >= is_subtitle_count:
        print(f"视频有字幕，用时{time_end - time_start}秒")
        dirname = f'有{lan}字幕'
    else:
        print(f"视频无字幕，用时{time_end - time_start}秒")
        dirname = f'无{lan}字幕'
    path = f'{out_path}\\{dirname}'
    if not os.path.exists(path):
        os.makedirs(path)
    # 保存视频流文件
    video_stream.download(output_path=path, filename=f'{title}.mp4')
    print("视频下载完成！")


process_subtitle(video_url, 'zh', 'C:\\Users\\Administrator\\Desktop\\工作\\code2\\ziyuan')