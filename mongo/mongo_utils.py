import json
import random

from pymongo import MongoClient


# host = '124.70.211.52'
# port = 18000
# username = 'qychap'
# password = 'qyno11'
# database = 'yt'
# # 创建MongoDB客户端
# client = MongoClient(host, port)
# # 进行身份验证
# client.admin.authenticate(username, password)
# db = client[database]
# collection = db["vds-525"]
#
# print('连接成功')
# # 构造查询条件
# query = {
#     "skiped": True,
#     "$expr": {
#         "$eq": ["$target_lang", {"$arrayElemAt": ["$subtitles", 0]}]
#     }
# }
#
# # 查询满足条件的行并获取"c"和"d"字段信息
# cursor = collection.find(query)
# result = {'result': []}
# for doc in cursor:
#     result['result'].append({
#         doc.get("id"): {
#             'name': f'Youtube_{doc.get("duration")}_{doc.get("upload_date")}_{doc.get("id")}.m4a',
#             'lang': doc.get("target_lang"),
#             'categorie': doc.get("categories")[0]
#         }
#     })
# with open('all.json', 'w', encoding='utf-8') as a:
#     a.write(json.dumps(result, ensure_ascii=False))


class MongoUtils:
    def __init__(self, host, port, username, password, database):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(
                f'mongodb://{self.username}:{self.password}@{self.host}:{self.port}/?authMechanism=DEFAULT')
            self.db = self.client[self.database]
            print("Connected to MongoDB")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")

    def disconnect(self):
        try:
            if self.client:
                self.client.close()
                print("Disconnected from MongoDB")
        except Exception as e:
            print(f"Failed to disconnect from MongoDB: {str(e)}")

    def insert_document(self, collection, document):
        try:
            self.db[collection].insert_one(document)
            print("Document inserted successfully")
        except Exception as e:
            print(f"Failed to insert document: {str(e)}")

    def update_document(self, collection, query, update):
        try:
            self.db[collection].update_many(query, update)
            print("Document updated successfully")
        except Exception as e:
            print(f"Failed to update document: {str(e)}")

    def delete_document(self, collection, query):
        try:
            self.db[collection].delete_one(query)
            print("Document deleted successfully")
        except Exception as e:
            print(f"Failed to delete document: {str(e)}")

    def find_documents(self, collection, query):
        try:
            documents = self.db[collection].find(query)
            return list(documents)
        except Exception as e:
            print(f"Failed to find documents: {str(e)}")
            return []

    def find_one_document(self, collection, query):
        try:
            document = self.db[collection].find_one(query)
            return document
        except Exception as e:
            print(f"Failed to find documents: {str(e)}")
            return None

    def find_random_document(self, collection, query):
        try:
            # 获取匹配查询条件的所有文档
            documents = list(self.db[collection].find(query))
            if documents:
                # 随机选择一个文档
                random_document = random.choice(documents)
                return random_document
            else:
                print("No documents found.")
                return None
        except Exception as e:
            print(f"Failed to find documents: {str(e)}")
            return None


# 使用示例
# if __name__ == '__main__':
# # 初始化MongoUtils对象
# mongo = MongoUtils('124.70.211.52', 18000, 'qychap', 'qyno11', 'haitum')
# # 连接到数据库
# mongo.connect()
# docs = mongo.find_documents('haitum_ids', {'downloaded': True})
# for doc in docs:
#     query = {'id': doc['id']}
#     update = {'$set': {'downloaded': False}}
#     mongo.update_document('haitum_ids', query, update)
# len = 0
# for doc in docs:
#     if 'm3u8_url_list' in doc.keys():
#         len += doc['m3u8_url_list'].__len__()
# print(len)
# ids = '22222'
# line_list = ['非凡', '测试']
# 插入文档
# document = {'id': ids, 'downloading': False, 'downloaded': False, 'line_names': line_list}
# mongo.insert_document('haitum_ids', document)

# # 更新文档
# query = {'id': ids}
# update = {'$set': {'downloading': False}}
# mongo.update_document('haitum_ids', query, update)

# # 删除文档
# query = {'name': 'John'}
# mongo.delete_document('users', query)
#
# # 查找文档
# query = {'age': {'$gte': 30}}
# documents = mongo.find_documents('users', query)
# for doc in documents:
#     print(doc)
#
# # 断开与数据库的连接
# mongo.disconnect()
