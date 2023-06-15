import re
from datetime import datetime, timedelta
from youtubesearchpython import *


def parse_upload_time(description):
    pattern = r"\b(\d+)\s+(day|days|hour|hours|minute|minutes|week|weeks|month|months|second|seconds)\b"
    if not re.findall(pattern, description.split(' ago')[0]):
        return None
    description = ' '.join(re.findall(pattern, description.split(' ago')[0])[0])
    now = datetime.now()
    if 'minute' in description:
        minutes = int(description.split()[0])
        upload_time = now - timedelta(minutes=minutes)
    elif 'hour' in description:
        hours = int(description.split()[0])
        upload_time = now - timedelta(hours=hours)
    elif 'week' in description:
        weeks = int(description.split()[0])
        upload_time = now - timedelta(weeks=weeks)
    elif 'day' in description:
        days = int(description.split()[0])
        upload_time = now - timedelta(days=days)
    elif 'month' in description:
        months = int(description.split()[0])
        upload_time = now - timedelta(days=months * 30)
    elif 'year' in description:
        years = int(description.split()[0])
        upload_time = now - timedelta(days=years * 365)
    else:
        upload_time = None
    return upload_time


def get_deadline_videos(channel_id, limit_time):
    limit_time = datetime.strptime(limit_time, "%Y%m")
    playlist = Playlist(playlist_from_channel_id(channel_id))
    index = 0
    count = 100
    result = []
    while True:
        for _ in range(count):
            li = playlist.videos[index]
            index += 1
            title = li['accessibility']['title']
            upload_time = parse_upload_time(title)
            if not upload_time:
                continue
            if upload_time > limit_time:
                result.append(li['link'])
            else:
                return result
        if playlist.hasMoreVideos:
            playlist.getNextVideos()
            count = count if playlist.videos.__len__() % 100 == 0 else playlist.videos.__len__() % 100
        else:
            return result


for i in get_deadline_videos("UU73sF-7Ihcs1HpnXEEXZ2ew", '202303'):
    print(i)
