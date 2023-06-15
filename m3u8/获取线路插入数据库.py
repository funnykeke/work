from m3u8.Haitum import Haitum
from mongo import mongo_utils

haitum = Haitum()
# 获取所有id
# haitum.get_all_play_id()

# 获取所有线路并插入数据库
mongo = mongo_utils.MongoUtils('124.70.211.52', 18000, 'qychap', 'qyno11', 'haitum')
mongo.connect()
with open('all_id', 'r', encoding='utf-8') as a:
    ids_list = eval(a.read())
ids_list = set(ids_list)
for ids in ids_list:
    if mongo.find_documents('haitum_ids', {'id': ids}):
        print(f'数据库已存入{ids}，跳过')
        continue
    all_line_names = haitum.get_all_line_name(ids)
    document = {
        'id': ids,
        'has_subtitle': True,
        'has_detected': False,
        'downloading': False,
        'downloaded': False,
        'line_names': all_line_names
    }
    mongo.insert_document('haitum_ids', document)
