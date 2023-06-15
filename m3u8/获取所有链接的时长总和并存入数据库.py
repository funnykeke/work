import queue
import threading

from m3u8.m3u8_utils import get_m3u8_duration
from mongo.mongo_utils import MongoUtils

mongo = MongoUtils('124.70.211.52', 18000, 'qychap', 'qyno11', 'haitum')
# 连接到数据库
mongo.connect()
docs = mongo.find_documents('haitum_ids', {'has_detected': True, 'has_subtitle': True, 'hours': {'$exists': False}})
docs_queue = queue.Queue()
for doc in docs:
    docs_queue.put(doc)


def main():
    print('开始！')
    while not docs_queue.empty():
        doc = docs_queue.get()
        hour = 0
        if 'm3u8_url_list' in doc.keys():
            for url in doc['m3u8_url_list']:
                temp = get_m3u8_duration(url)
                hour = hour + temp if temp else 0
        hour = hour / 3600
        mongo.update_document('haitum_ids', {'id': doc['id']}, {'$set': {'hours': hour}})
    else:
        print('结束！！！！！！')


thread_list = []
for _ in range(70):
    thread_list.append(threading.Thread(target=main))
for thread in thread_list:
    thread.start()

