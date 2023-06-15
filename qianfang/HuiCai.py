import glob
import json
import logging
import os
import re
import requests
import time

from selenium import webdriver


def print_category_path_by_category_id(category_id):
    with open("first_level_category.json", "r", encoding="utf-8") as a:
        first_level_category = json.load(a)
    with open("secondary_category.json", "r", encoding="utf-8") as a:
        secondary_category = json.load(a)
    with open("third_level_category.json", "r", encoding="utf-8") as a:
        third_level_category = json.load(a)
    third_level_category_name = third_level_category[str(category_id)]["name"]
    secondary_category_name = secondary_category[str(third_level_category[str(category_id)]["parent"])]["name"]
    first_level_category_name = first_level_category[str(
        secondary_category[str(third_level_category[str(category_id)]["parent"])]["parent"])]["name"]
    print('该商品所在目录：《' +
          first_level_category_name
          + "---"
          + secondary_category_name
          + "---"
          + third_level_category_name
          + '》'
          )


class HuiCai:
    def __init__(self):
        # 型号名
        self.model = None
        self.cookie = None
        # 借鉴商品id
        self.item_id = ''
        # 借鉴商品详情信息
        self.item_data = {}
        # 文件夹id
        self.folder_id = ''
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Connection": "keep-alive",
                "Host": "mall.anhui.zcygov.cn",
                "Origin": "https://mall.anhui.zcygov.cn",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57",
            }
        )

    def login(self):
        driver = webdriver.Edge()
        driver.get('https://login.anhui.zcygov.cn/user-login/')
        input('登陆完成后请按换行：')
        cookie_txt = driver.get_cookies()
        with open('cookie.txt', 'w', encoding='utf-8') as co:
            co.write(json.dumps(cookie_txt))

    # 初始化cookie
    def init_cookie(self):
        with open('cookie.txt', 'r', encoding='utf-8') as co:
            cookie_list = json.loads(co.read())
        cookie_txt = ''
        for co in cookie_list:
            cookie_txt += co['name']
            cookie_txt += '='
            cookie_txt += co['value']
            cookie_txt += '; '
        cookie_txt = cookie_txt.rstrip("; ")
        cookie_txt = cookie_txt.strip()
        self.cookie = {
            'Cookie': cookie_txt
        }
        session = requests.Session()
        session.headers.update(self.cookie)
        session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Host': 'middle.anhui.zcygov.cn',
            'Pragma': 'no - cache',
            'Referer': 'https: // middle.anhui.zcygov.cn / web - user /'
        })
        try:
            institution_name = json.loads(session.get(
                'https://middle.anhui.zcygov.cn/zcy/user-web/v2/operators/login?needTenant=true&needDepartment=true'
                '&needTitle=true&needInstitution=true').text)['data']['institutionName']
            print(f'{institution_name}-欢迎您!\n')
        except:
            print('登陆过期，请在弹出的页面中重新登陆~')
            self.login()
            self.init_cookie()

    # 初始化类中的item_id(借鉴商品id)，并打印所在三级目录，默认获取第一件商品的。并初始化商品信息
    def init_category_path_by_model(self, index=0):
        while True:
            session = self.session
            session.headers.update({
                "Content-Type": "application/json;charset=UTF-8",
            })
            res = session.post(
                "https://mall.anhui.zcygov.cn/front/index/search/search",
                data=json.dumps(
                    {
                        "pageNo": 1,
                        "pageSize": 50,
                        "matchDirectPurchase": False,
                        "q": self.model,
                        "fcids": None,
                        "hasStock": True,
                        "deliveryCode": 330102,
                        "excludedIds": [],
                        "sort": "0_0_0_0",
                        "normal": 6,
                    }
                ),
            ).text
            items = json.loads(res)["result"]["searchWithAggs"]["entities"]["data"]
            if items:
                break
            else:
                self.model = input('搜索结果为空，请重新输入型号（若多次搜索不到可能平台暂未上架过该商品）：')
        self.item_id = str(items[index]['id'])
        self.init_item_data()
        if index == 0:
            back_category_id = items[index]["backCategoryId"]
            print_category_path_by_category_id(back_category_id)

    # 初始化商品信息item_data
    def init_item_data(self):
        result = self.session.get(f'https://mall.anhui.zcygov.cn/front/detail/item/{self.item_id}').text
        self.item_data = json.loads(result)['result']

    # 获取上货链接
    def print_publish_link(self):
        session = self.session
        session.headers.update(self.cookie)
        # 卖场信息（供下面获取铺货链接使用）
        mall_data = \
            json.loads(session.get('https://www.anhui.zcygov.cn/api/goods/draft/agreementShopMapper/select').text)[
                'result']['data'][0]
        error_count = 0
        while error_count < 3:
            try:
                key_attrs_brief = self.item_data['item']['keyAttrsBrief']
                data = {
                    "instanceCode": mall_data['instanceCode'],
                    "protocolId": mall_data['id'],
                    "categoryId": int(self.item_data['item']['categoryId']),
                    "keyAttributes": [
                        {
                            "propertyId": int(key_attrs_brief.split(':')[0]),
                            "attrKey": "品牌",
                            "attrVal": self.item_data['item']['brandName'],
                            "attrValIds": [
                                int(self.item_data['item']['brandId'])
                            ]
                        },
                        {
                            "propertyId": int(key_attrs_brief.split(':')[1].split(';')[1]),
                            "attrKey": "型号",
                            "attrVal": self.item_data['item']['specification'],
                            "attrValIds": []
                        }
                    ]
                }
                session = self.session
                session.headers.update(self.cookie)
                res = session.post(
                    'https://www.anhui.zcygov.cn/api/biz-item/item-platform/manages/select-category/publish/next',
                    data=json.dumps(data)).text
                spu_id = json.loads(res)['result']['spuId']
                print(
                    f'上货链接：\nhttps://www.anhui.zcygov.cn/goods-center/goods/publish?categoryId={self.item_data["item"]["categoryId"]}&protocolId'
                    f'={mall_data["id"]}&bidId={mall_data["bidId"]}&instanceCode={mall_data["instanceCode"]}&tag=GOODS&spuId={spu_id}')
                break
            except:
                error_count += 1
                self.init_category_path_by_model(error_count)
        if error_count >= 3:
            logging.info("上货链接获取失败，请根据三级类目自行选择上货~")

    # 打印商品信息item_data
    def print_item_data(self):
        need_mes = {}
        try:
            need_mes = {'生产厂商': self.item_data['item']['extra']['firm'],
                        '第三方链接': self.item_data['item']['extra']['selfPlatformLink'],
                        '计量单位': self.item_data['item']['extra']['unit'],
                        '市场价': self.item_data['skus'][0]['fullPrice']['marketPrice'] / 100,
                        '销售价': self.item_data['skus'][0]['fullPrice']['agreementPrice'] / 100}
            need_mes['产地'] = self.item_data['item']['origin']['provinceName'] + self.item_data['item']['origin'][
                'cityName'] + self.item_data['item']['origin']['regionName'],
        except:
            print('商品信息可能未全部读取～')
        print('===============待上货商品信息================')
        for key, value in need_mes.items():
            if value:
                print(f'{key}: {value}')
        print('===============待上货商品信息================')

    # 下载详情图片
    def download_detail_img(self):
        session = self.session
        session.headers.update(self.cookie)
        folder_path = os.getcwd()  # 获取当前工作目录路径
        # 获取当前目录中所有.jpg文件的路径列表
        jpg_files = glob.glob(os.path.join(folder_path, "*.jpg"))
        # 遍历文件列表并删除每个文件
        for file_path in jpg_files:
            os.remove(file_path)
        try:
            detail = self.item_data['itemDetail']['detail']
            detail_img_url_list = re.findall('''src="(.*?)"''', detail)
            for name, image_url in enumerate(detail_img_url_list):
                image_content = requests.get(image_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                }).content
                with open(f'detail_{name}.jpg', 'wb') as file:
                    file.write(image_content)
            print("详情图片已下载完毕，与该脚本在同一文件夹，请自行查看！")
        except:
            raise Exception("下载商品详情图片失败~")

    # 在网站创建存放图片的文件夹，返回文件夹的id
    def create_dir(self):
        session = self.session
        session.headers.update({
            "Content-Type": "application/json;charset=UTF-8",
        })
        session.headers.update(self.cookie)
        try:
            result = session.post('https://www.anhui.zcygov.cn/api/micro/folder/create',
                                  data=json.dumps({"folder": self.model, "pid": 0})).text
            print('存放图片文件夹创建成功，与您之前输入的型号名相同！')
            self.folder_id = json.loads(result)['userFolder']['id']
        except:
            raise Exception("图片存放的文件夹创建失败，请自行创建！")

    # 上传图片至文件夹
    def upload_img(self):
        session = self.session
        session.headers.clear()
        session.headers.update({
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            "Host": "mall.anhui.zcygov.cn",
            "Origin": "https://mall.anhui.zcygov.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57",
        })
        session.headers.update(self.cookie)
        img_url_list = [self.item_data['item']['mainImage']]
        for info in self.item_data['imageInfos']:
            img_url_list.append(info['url'])
        try:
            for index, image_url in enumerate(img_url_list):
                image_content = requests.get(image_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                }).content
                files = {'file': (f'{index}.jpg', image_content, "image/jpeg")}
                response = session.post(
                    f'https://www.anhui.zcygov.cn/api/micro/file/upload?folderId={str(self.folder_id)}',
                    files=files).text
                if 'Error' not in response:
                    print(f'第{index + 1}张预览图上传成功')
                    time.sleep(0.5)
                else:
                    print(f'第{index + 1}张预览图上传失败')
        except:
            raise Exception("预览图上传失败")

    def main(self):
        # 初始化身份信息
        self.init_cookie()
        self.model = input('请输入需要上架的商品型号：')
        # 获取目录并初始化类中的item_id
        self.init_category_path_by_model()
        # 打印上货链接
        self.print_publish_link()
        # 打印待上货商品信息
        self.print_item_data()
        # 下载详情图片
        self.download_detail_img()
        # 创建文件夹
        self.create_dir()
        # 上传图片
        self.upload_img()


if __name__ == "__main__":
    try:
        huicai = HuiCai()
        huicai.main()
    except Exception as e:
        logging.error(e)
    input('回车以结束运行~~~')
