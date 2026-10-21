# coding=utf-8
import json
import os
from loguru import logger

from dy_apis.douyin_api import DouyinAPI
from utils.common_util import init

from utils.data_util import handle_work_info, download_work, save_to_xlsx
from utils.database_util import SqliteDB
from apis.automated_advertising_collection_api import AutomatedAdvertisingCollection
import shutil
import openpyxl
from PIL import Image
from datetime import datetime, timedelta
import time
import random
from utils.data_util_local import createtime_out_waning, download_work_verification

class Data_Spider():
    def __init__(self):
        self.douyin_apis = DouyinAPI()
        self.sqlite_db = SqliteDB()

    def spider_work(self, auth, work_url: str, proxies=None):
        """
        爬取一个作品的信息
        :param auth : 用户认证信息
        :param work_url: 作品链接
        :return:
        """
        res_json = self.douyin_apis.get_work_info(auth, work_url)
        data = res_json['aweme_detail']

        work_info = handle_work_info(data)
        logger.info(f'爬取作品信息 {work_url}')
        return work_info

    def spider_some_work(self, auth, works: list, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
        """
        爬取一些作品的信息
        :param auth: 用户认证信息
        :param works: 作品链接列表
        :param base_path: 保存路径
        :param save_choice: 保存方式 all: 保存所有的信息, media: 保存视频和图片（media-video只下载视频, media-image只下载图片，media都下载）, excel: 保存到excel
        :param excel_name: excel文件名
        :return:
        """
        if (save_choice == 'all' or save_choice == 'excel') and excel_name == '':
            raise ValueError('excel_name 不能为空')
        work_list = []
        for work_url in works:
            #单日采集上限校验
            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
            if data_spider.sqlite_db.GetCount(start_time, end_time) > int(os.getenv('COLLECTION_LIMIT_DAY_NUM')):
                logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->已达到单日采集上限，暂停采集')
                break
            #验证是否已经采集
            if self.sqlite_db.GetExist(work_url = work_url) == True:
                logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->作品({work_url})已采集，忽略')
                continue

            work_info = self.spider_work(auth, work_url)
            #验证作品发布时间
            if createtime_out_waning(work_info['create_time']) == False:
                logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->作品({work_url})发布超出采集时间范围，忽略')
                continue
            if save_choice == 'all' or 'media' in save_choice:
                save_path = download_work(work_info, base_path['media'], save_choice)
                #验证下载的文件是否通过校验
                if download_work_verification(work_info, save_path, save_choice):
                    self.sqlite_db.AddLog(work_info)
                    work_list.append(work_info)
                    time.sleep(int(os.getenv('COLLECTION_TIME_INTERVAL_MINUTES')))
                else :
                    #删除校验失败的用户作品
                    shutil.rmtree(save_path)
        if save_choice == 'all' or save_choice == 'excel':
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(work_list, file_path)

    def spider_user_all_work(self, auth, user_url: str, base_path: dict, save_choice: str, excel_name: str = '', proxies=None):
        """
        爬取一个用户的所有作品
        :param auth: 用户认证信息
        :param user_url: 用户链接
        :param base_path: 保存路径
        :param save_choice: 保存方式 all: 保存所有的信息, media: 保存视频和图片（media-video只下载视频, media-image只下载图片，media都下载）, excel: 保存到excel
        :param excel_name: excel文件名
        :param proxies: 代理
        :return:
        """
        user_info = self.douyin_apis.get_user_info(auth, user_url)
        work_list = self.douyin_apis.get_user_all_work_info(auth, user_url)
        logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->作品数量总计：{len(work_list)}')
        if save_choice == 'all' or save_choice == 'excel':
            excel_name = user_url.split('/')[-1].split('?')[0]

        work_info_list = []
        for work_info in work_list:
            work_info['author'].update(user_info['user'])
            work_info = handle_work_info(work_info)
            logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->爬取作品信息： {work_info["work_url"]}')
            #验证是否已经采集
            if self.sqlite_db.GetExist(work_id = work_info["work_id"]) == True: 
                logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->作品({work_info["work_url"]})已采集，忽略')
                continue
            #作品发布时间
            if createtime_out_waning(work_info['create_time']) == False:
                logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->作品({work_info["work_url"]})发布超出采集时间范围，忽略')
                continue                
            if save_choice == 'all' or 'media' in save_choice:
                save_path = download_work(work_info, base_path['media'], save_choice)
                #验证下载的文件是否通过校验
                if download_work_verification(work_info, save_path, save_choice):
                    self.sqlite_db.AddLog(work_info)
                    work_info_list.append(work_info) 
                    time.sleep(int(os.getenv('COLLECTION_TIME_INTERVAL_MINUTES')))
                else :
                    #删除校验失败的用户作品
                    shutil.rmtree(save_path)
                    logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->删除校验失败的用户作品等待1分钟')
                    time.sleep(60)
            
        if save_choice == 'all' or save_choice == 'excel':
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(work_info_list, file_path)

    def spider_work_upload(self, del_local_file: bool = False):
        """
            :param del_local_file: 上传完成后是否删除本地文件.
        """
        # 循环遍历获取爬取的所有用户作品信息
        root_dir = f"{os.path.dirname(os.path.abspath(__file__))}/datas/media_datas/"
        users_dir = [os.path.join(root_dir, f) for f in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, f))]
        for user_dir in users_dir:
            user_works_dir = [os.path.join(user_dir, f) for f in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, f))]
            for user_work_dir in user_works_dir:
                # 1.读取info.json文件
                infojson_path = os.path.join(user_work_dir, "info.json")
                if os.path.exists(infojson_path) == False:
                    continue
                with open(infojson_path, 'r', encoding='utf-8') as infojson_file:
                    infojson_data = json.load(infojson_file)
                # 2.上传homepage文件
                infojson_data["user_screenshot"] = ""
                homepage_path = os.path.join(user_work_dir, "homepage.png")
                if os.path.exists(homepage_path):
                    uhp_res = AutomatedAdvertisingCollection.upload_base64file(homepage_path)
                    if uhp_res["Success"] == True:
                        infojson_data["user_screenshot"] = uhp_res["Data"] 
                # 3.上传mp4文件，如果有的话
                infojson_data["video_addr"] = ""
                video_path = os.path.join(user_work_dir, "video.mp4")
                if os.path.exists(video_path):
                    uva_res = AutomatedAdvertisingCollection.upload_base64file(video_path)
                    if uva_res["Success"] == True:
                        infojson_data["video_addr"] = uva_res["Data"]                     
                # 4.上传image_文件，如果有的话
                infojson_data["images"] = []
                images_path = [user_work_file.path for user_work_file in os.scandir(user_work_dir) if user_work_file.is_file() and "image_" in user_work_file.name]
                if len(images_path) > 0:
                    img_list = [Image.open(image_path) for image_path in images_path]
                    widths, heights = zip(*(img.size for img in img_list))
                    total_height = sum(heights) + 0 * (len(img_list) - 1)
                    max_width = max(widths)
                    result = Image.new('RGB', (max_width, total_height), (255,255,255))
                    y_offset = 0
                    for img in img_list:
                        result.paste(img, (0, y_offset))
                        y_offset += img.height + 0
                    image_all_path = os.path.join(user_work_dir, "image_all.jpg")
                    result.save(image_all_path)
                    ui_res = AutomatedAdvertisingCollection.upload_base64file(image_all_path)
                    if ui_res["Success"] == True:
                        infojson_data["images"].append(ui_res["Data"])

                logger.info(f"待上传数据：{infojson_data}")
                # 1.判断video_addr与images字段是否有数据，没有数据放弃本次添加
                if len(infojson_data["images"]) == 0 and infojson_data["video_addr"] == "":
                    logger.info(f"缺少images与video_addr数据，停止上传")
                    continue
                aac_res = AutomatedAdvertisingCollection.AddDYAdvertising(infojson_data)
                # 2.成功上传判断是否要删除本地数据
                if aac_res["Success"] == True:
                    logger.info(f"上传成功")
                    # 删除数据
                    if del_local_file == True:
                        shutil.rmtree(user_work_dir)
                        logger.info(f"删除文件夹：{user_work_dir}")
                else:
                    logger.info(f'上传失败：{aac_res["Message"]}')     

if __name__ == '__main__':
    """
        此文件为爬虫的入口文件，可以直接运行
        dy_apis/douyin_apis.py 为爬虫的api文件，包含抖音的全部数据接口，可以继续封装
        dy_live/server.py 为监听抖音直播的入口文件，可以直接运行
        感谢star和follow
    """

    auth, base_path = init()

    data_spider = Data_Spider()
    # save_choice: all: 保存所有的信息, media: 保存视频和图片（media-video只下载视频, media-image只下载图片，media都下载）, excel: 保存到excel
    # save_choice 为 excel 或者 all 时，excel_name 不能为空
    # # 1 爬取列表的所有作品信息 作品链接 如下所示 注意此url会过期！
    works = []
    if os.path.exists('works.xlsx') == True:
        wb = openpyxl.load_workbook('works.xlsx')
        ws = wb["Sheet1"]
        for wr in ws.iter_rows(min_row=2, values_only=True):
            wc_work_url = wr[0]
            works.append(wc_work_url)
        random.shuffle(works)
        
        logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->任务：开始爬取指定作品列表信息，作品总计（{len(works)}）')
        data_spider.spider_some_work(auth, works, base_path, 'all', 'test')
    else:
        logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->任务：爬取指定作品列表信息，未找到“works.xlsx”文件任务结束')

    # # 2 爬取用户的所有作品信息 用户链接 如下所示 注意此url会过期！
    users_url = []
    if os.path.exists('users.xlsx') == True:
        wb = openpyxl.load_workbook('users.xlsx')
        ws = wb["Sheet1"]
        for wr in ws.iter_rows(min_row=2, values_only=True):
            wc_media_identity = wr[0]
            wc_media_domain = wr[1]
            users_url.append(wc_media_domain)
        random.shuffle(users_url)

        logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->任务：爬取用户的所有作品信息，用户总计（{len(users_url)}）')
        for index, user_url in enumerate(users_url):
            logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->({index + 1}/{len(users_url)})开始爬取用户（{user_url}）所有作品信息')
            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
            if data_spider.sqlite_db.GetCount(start_time, end_time) > int(os.getenv('COLLECTION_LIMIT_DAY_NUM')):
                logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->已达到单日采集上限，暂停采集')
                break

            data_spider.spider_user_all_work(auth, user_url, base_path, 'all')
    else:
        logger.info(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}--->任务：爬取用户的所有作品信息，未找到“users.xlsx”文件任务结束')

    # # 3 上传爬取的数据
    data_spider.spider_work_upload(del_local_file=True)
  

   
