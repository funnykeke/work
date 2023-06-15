import ctypes
import json
import threading
import time
import requests
from lxml.etree import HTML
import logging
import m3u8_utils
from mongo import mongo_utils

# 设置日志等级为DEBUG
logging.basicConfig(level=logging.DEBUG)
# 限制海兔的并发量
semaphore = threading.Semaphore(3)


class Haitum:
    def __init__(self) -> None:
        self.all_play_id = None
        self.session = requests.Session()
        self.session.headers.update(
            {
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            }
        )
        self.all_category = ['dianying-meiguo', 'dianying-yingguo', 'dianshiju-meiguo', 'dianshiju-yingguo',
                             'zongyi-meiguo', 'zongyi-yingguo', 'dongman-meiguo', 'dongman-yingguo', 'jilupian-meiguo',
                             'jilupian-yingguo', 'weidianying-meiguo', 'weidianying-yingguo']

    def long_get(self, url):
        error_count = 0
        while error_count < 5:
            try:
                res = self.session.get(url)
                if res.status_code == 200:
                    res.encoding = 'utf-8'
                    return res
                else:
                    return None
            except Exception as _:
                time.sleep(10)
                error_count += 1
        logging.error(f"{url}请求失败!")
        return None

    def long_post(self, url, data):
        error_count = 0
        while error_count < 5:
            try:
                res = self.session.post(url, data=data)
                res.encoding = 'utf-8-sig'
                if res.status_code == 200:
                    res.encoding = 'utf-8'
                    return res
                else:
                    return None
            except Exception as _:
                time.sleep(3)
                error_count += 1
        logging.error(f"{url}请求失败!")
        return None

    def get_all_line_name(self, id):
        res = self.long_get(f"https://www.haitum.cc/movie/{id}.html")
        if res.status_code == 200:
            html = HTML(res.text)
            return html.xpath(
                "//div[@class='hd']//ul/li/a/text()"
            )
        else:
            return None

    # 根据ids与线路位置获取m3u8链接
    def get_m3u8_url_list(self, ids, line_index):
        m3u8_url_list = []
        global semaphore
        semaphore.acquire()
        res = self.long_post(
            "https://www.haitum.cc/common/api_getTargetRsBoxData.php",
            data={
                'order': 'getTargetRsBoxData',
                'ids': ids,
                'type': '2',
                'index': str(line_index)
            },
        )
        semaphore.release()
        if res:
            res.encoding = 'utf-8-sig'
            res = json.loads(res.text)
            episodes = res['data']['episodes']
            for episode in episodes:
                m3u8_url_list.append('http' + episode['url'].split('http')[-1])
        return m3u8_url_list

    # 获取所有符合条件的ids
    def get_all_play_id(self):
        all_play_id = []
        for category in self.all_category:
            with open('all_id', 'w', encoding='utf-8') as a:
                a.write(str(all_play_id))
            logging.info(f'正在获取{category}')
            text = self.long_get(f'https://www.haitum.cc/{category}/page/1').text
            try:
                html = HTML(text)
                max_page = int(html.xpath("//div[@class='count']/b[1]/text()")[0])
            except:
                logging.error(f"{category}---maxpage获取失败")
                continue
            for page in range(1, max_page + 1):
                logging.info(f'正在获取{category}第{page}页')
                url = f'https://www.haitum.cc/{category}/page/{page}'
                text = self.long_get(url).text
                if not text:
                    continue
                else:
                    html = HTML(text)
                    link_list = html.xpath("//ul[@class='list new-list lazy-load-list']/li/a/@href")
                    for link in link_list:
                        all_play_id.append(link.split('.')[0].split('/')[-1])
        self.all_play_id = all_play_id


def distinguish_m3u8_subtitle():
    haitum = Haitum()
    # 下载视频
    mongo = mongo_utils.MongoUtils('124.70.211.52', 18000, 'qychap', 'qyno11', 'haitum')
    mongo.connect()
    while True:
        try:
            doc = mongo.find_random_document('haitum_ids', {
                'has_detected': False,
                'downloading': False,
                'downloaded': False
            })
            if not doc:
                logging.info("结束！！！！！！！！！！！！！")
                break
            query = {'id': doc['id']}
            update = {'$set': {'downloading': True}}
            mongo.update_document('haitum_ids', query, update)
            m3u8_url_list = []
            has_subtitle = False
            print(f'正在观察{doc["id"]}~')
            for index, _ in enumerate(doc['line_names']):
                if index >= 3:
                    break
                m3u8_url_list = haitum.get_m3u8_url_list(doc['id'], index)
                if not m3u8_url_list:
                    continue
                if m3u8_utils.if_m3u8_exist_english_subtitle(m3u8_url_list[0], doc['id']):
                    has_subtitle = True
                    print(f'{doc["id"]}---存在英文字幕')
                    update = {'$set': {'has_detected': True, 'has_subtitle': True}}
                    mongo.update_document('haitum_ids', query, update)
                    break
                else:
                    continue
            if has_subtitle:
                # for m3u8_url in m3u8_url_list:
                #     try:
                #         m3u8_utils.download_m3u8_video(m3u8_url, f'E:\\m3u8\\{doc["id"]}\\{index}.mp4')
                #     except:
                #         pass
                # update = {'$set': {'downloaded': True}}
                # mongo.update_document('haitum_ids', query, update)
                update = {'$set': {'m3u8_url_list': m3u8_url_list}}
                mongo.update_document('haitum_ids', query, update)
            else:
                print(f'{doc["id"]}---不存在英文字幕')
                update = {'$set': {'has_detected': True, 'has_subtitle': False}}
                mongo.update_document('haitum_ids', query, update)
            update = {'$set': {'downloading': False}}
            mongo.update_document('haitum_ids', query, update)
        except KeyboardInterrupt:
            print('正在修复进度~')
            query = {'id': doc['id']}
            # query = {'downloading': True}
            update = {'$set': {'downloading': False, 'has_detected': False, 'downloaded': False, 'has_subtitle': True}}
            mongo.update_document('haitum_ids', query, update)
            print('修复当前进度成功~')
            time.sleep(5)
            break


def inject_interrupt(thread):
    thread_id = thread.ident
    ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(KeyboardInterrupt))


if __name__ == '__main__':
    # haitum = Haitum()
    # 获取所有id
    # haitum.get_all_play_id()

    ########################################################
    # 获取所有线路并插入数据库
    # mongo = mongo_utils.MongoUtils('124.70.211.52', 18000, 'qychap', 'qyno11', 'haitum')
    # mongo.connect()
    # with open('all_id', 'r', encoding='utf-8') as a:
    #     ids_list = eval(a.read())
    # for ids in ids_list:
    #     all_line_names = haitum.get_all_line_name(ids)
    #     document = {'id': ids, 'downloading': False, 'downloaded': False, 'line_names': all_line_names}
    #     mongo.insert_document('haitum_ids', document)

    ########################################################
    thread_list = []
    for _ in range(20):
        thread_list.append(threading.Thread(target=distinguish_m3u8_subtitle))
    for thread in thread_list:
        thread.start()
    while 1:
        try:
            time.sleep(100)
        except KeyboardInterrupt:
            for thread in thread_list:
                inject_interrupt(thread)
            break
    print('准备重置')
    time.sleep(10)
    mongo = mongo_utils.MongoUtils('124.70.211.52', 18000, 'qychap', 'qyno11', 'haitum')
    mongo.connect()
    query = {'downloading': True}
    update = {'$set': {'downloading': False, 'has_detected': False, 'downloaded': False, 'has_subtitle': True}}
    mongo.update_document('haitum_ids', query, update)
    print('全部重置~')
    exit()