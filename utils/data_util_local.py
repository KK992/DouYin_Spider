import os
from loguru import logger
from retry import retry
from utils.selenium_util import WebCrawler
import time
from datetime import datetime
import magic
import requests
from pathlib import Path


def timestamp_to_str(timestamp):
    time_local = time.localtime(timestamp / 1000)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt

def createtime_out_waning(timestamp_s):
    """
    判断时间戳是否符合COLLECTION_TIME_RAGNE_DAY要求
    :param timestamp_s: 目标时间戳（单位秒）.
    :return: True符合要求，False不符合
    """
    time_diff_day =  count_down_day(timestamp_s)
    if time_diff_day > int(os.getenv('COLLECTION_TIME_RAGNE_DAY')) * -1:
        return True
    else:
        return False


def count_down_day(timestamp_s):
    """
    倒计时，当前时间距目标时间还有几天.
    :param timestamp_s: 目标时间戳（单位秒）.
    :return: 当前时间距目标时间天数，负数表示超过几天.
    """
    current_time = datetime.now()
    taget_time = datetime.strptime(timestamp_to_str(timestamp_s * 1000), "%Y-%m-%d %H:%M:%S")
    time_diff = taget_time - current_time

    return time_diff.days


def download_work_verification(work_info, save_path, save_choice):
    """
    监测下载的用户work信息是否通过校验.
    :param work_info: 用户信息.
    :param save_path: 下载work的路径.
    :param save_choice: 下载选项.
    :return: True通过 False未通过.
    """
    work_type = work_info['work_type']
    if work_type == '图集' and save_choice in ['media', 'media-image', 'all']:
        images_path = [user_work_file.path for user_work_file in os.scandir(save_path) if user_work_file.is_file() and "image_" in user_work_file.name]
        if len(images_path) > 0:
            for img_path in images_path:
                img_path = Path(img_path)
                with open(img_path,'rb') as f:
                    buffer = f.read(1024)
                mime_type = magic.from_buffer(buffer,mime=True)
                if "image/" not in mime_type :
                    logger.info(f"文件（{str(img_path)}）MagicNumber校验未通过，不是正确的图片文件。")
                    return False
                else :
                    continue
            return True
        else:
            logger.info(f"指定路径下({save_path})未找到图集媒体文件，校验未通过。")
            return False
    elif work_type == '视频' and save_choice in ['media', 'media-video', 'all']:
        video_path = os.path.join(save_path, "video.mp4")
        if os.path.exists(video_path):
            video_path = Path(video_path)
            with open(video_path,'rb') as f:
                buffer = f.read(1024)
            mime_type = magic.from_buffer(buffer,mime=True)
            if "video/" not in mime_type :
                logger.info(f"文件（{str(video_path)}）MagicNumber校验未通过，不是正确的视频文件。")
                return False
            else :
                return True
        else:
            logger.info(f"指定路径下({str(video_path)})未找到视频媒体文件，校验未通过。")
            return False
    else:
        return True

def download_homepage(work_info, save_path):
    """
    使用selenium对用户首页截图.
    :param work_info: 用户信息.
    :param save_path: 下载work的路径.
    :param save_choice: 下载选项.
    :return: True通过 False未通过.
    """
    crawler = WebCrawler(headless=True)
    try:
        # 访问目标地址并截图
        target_url = work_info['user_url']
        crawler.visit_and_screenshot(target_url,save_path=save_path, filename_prefix="homepage")
    finally:
        # 确保无论是否报错，浏览器都能被正常关闭
        crawler.close()   