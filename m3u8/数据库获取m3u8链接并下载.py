import asyncio
import time
import m3u8.m3u8_utils
from mongo import mongo_utils

mongo = mongo_utils.MongoUtils('124.70.211.52', 18000, 'qychap', 'qyno11', 'haitum')
mongo.connect()


async def download_m3u8():
    while True:
        res = mongo.find_random_document('haitum_ids',
                                         {'has_detected': True, 'has_subtitle': True, 'downloaded': False,
                                          'downloading': False})
        query = {'id': res['id']}
        try:
            if res:
                update = {'$set': {'downloading': True}}
                mongo.update_document('haitum_ids', query, update)
                for index, m3u8_url in enumerate(res['m3u8_url_list']):
                    if len(res['m3u8_url_list']) == 1:
                        duration = res['hours']
                    else:
                        duration = m3u8.m3u8_utils.get_m3u8_duration(m3u8_url)
                    command = f'ffmpeg -i {m3u8_url} -c copy ' \
                              f'E:\\qhl\\m3u8_datas\\{res["id"]}_{index}_{duration}.mp4'
                    print(f'开始下载——{res["id"]}_{index}_{duration}.mp4')
                    process = await asyncio.create_subprocess_shell(command)
                    await process.wait()
                    print(f'{res["id"]}_{index}_{duration}.mp4——下载完毕')
                update = {'$set': {'downloading': False, 'downloaded': True}}
                mongo.update_document('haitum_ids', query, update)
        except Exception as e:
            print(f'下载ERROR-----{res["id"]}------{str(e)}')
            update = {'$set': {'downloading': False, 'downloaded': False}}
            mongo.update_document('haitum_ids', query, update)


async def main():
    tasks = []
    for _ in range(8):
        tasks.append(asyncio.create_task(download_m3u8()))
        time.sleep(1)
    await asyncio.gather(*tasks)


asyncio.run(main())