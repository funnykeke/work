import os
import json
import asyncio
import json
import argparse

# 创建解析器对象
parser = argparse.ArgumentParser()

# 添加参数定义
parser.add_argument('-m', '--arg1', type=str, help='执行的操作：d下载，t统计时间')

# 解析命令行参数
args = parser.parse_args()



ys = {
    'Pets & Animals': '环境（自然）',
    'Autos & Vehicles': '科技',
    'People & Blogs': '文化',
    'Sports': '体育',
    'Comedy': '娱乐',
    'Education': '文化',
    'Nonprofits & Activism': '文化',
    'Gaming': '娱乐',
    'News & Politics': '政治',
    'Howto & Style': '时尚与生活',
    'Entertainment': '娱乐',
    'Science & Technology': '科技',
    'Travel & Events': '时尚与生活',
    'Film & Animation': '娱乐',
    'Music': '娱乐',
}

# 获取已经下载完的id集合
def get_downloaded():
    downloaded_video = set()
    downloaded_vtt = set()
    for folder in os.listdir('E:\\Datas'):
        for i in os.listdir('E:\\Datas\\' + folder):
            for name in os.listdir('E:\\Datas\\' + folder + '\\' + i):
                if name.endswith('vtt'):
                    parts = name.split('.')[0].split("_")
                    downloaded_vtt.add("_".join(parts[3:]))
                else:
                    parts = name.split('.')[0].split("_")
                    downloaded_video.add("_".join(parts[3:]))
    return downloaded_video&downloaded_vtt

# 并行下载数量
max_processes = 5
semaphore = asyncio.Semaphore(max_processes)
# 下载命令列表
download_commands = []
with open('all.json', 'r', encoding='utf-8') as a:
    result = json.loads(a.read())['result']
downloaded = get_downloaded()
for item in result:
    id = list(item.keys())[0]
    if id not in downloaded:
        # yt-dlp -f ba --write-subs --sub-format vtt --sub-lang es.* --proxy http://127.0.0.1:5001 https://www.youtube.com/watch?v=Tu6nPvfx22k -o "D://Datas//%(extractor_key)s_%(duration)s_%(upload_date)s_%(id)s.%(ext)s"
        command = f'yt-dlp -f ba --write-subs --sub-format vtt --sub-lang {item[id]["lang"]}.* --proxy http://127.0.0.1:7890 https://www.youtube.com/watch?v={id} -o "E://Datas//{item[id]["lang"]}//{ys[item[id]["categorie"]]}//%(extractor_key)s_%(duration)s_%(upload_date)s_%(id)s.%(ext)s"'
        download_commands.append(command)


async def run_command(command):
    global semaphore
    process = await asyncio.create_subprocess_shell(command)
    await process.wait()
    semaphore.release()


async def execute_commands(index):
    await run_command(download_commands[index])


async def main():
    global semaphore
    tasks = []
    semaphore = asyncio.Semaphore(max_processes)
    for i in range(download_commands.__len__()):
        await semaphore.acquire()
        tasks.append(asyncio.create_task(execute_commands(i)))
    await asyncio.gather(*tasks)


def 下载视频():
    asyncio.run(main())


def 统计时间():
    all = []
    time = 0
    # 统计已经下载的时间
    for folder in os.listdir('E:\\Datas'):
        for i in os.listdir('E:\\Datas\\' + folder):
            for name in os.listdir('E:\\Datas\\' + folder + '\\' + i):
                    parts = name.split('.')[0].split("_")
                    if "_".join(parts[3:]) in downloaded:
                        all.append(name.split('.')[0])
    for name in all:
        time += int(name.split('_')[1])
    print(str(time/60/60/2)+'hours')


# 访问解析后的参数
if args.arg1 is not None:
    if args.arg1 == 't':
        统计时间()
    else:
        下载视频()
else:
    下载视频()