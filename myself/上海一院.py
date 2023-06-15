import requests

headers = {'Cookie': 'ASP.NET_SessionId=nv01pvpa4jlrzir4ysfr0ooe',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43', }

session = requests.Session()
print(session.get('https://guahao.shgh.cn/yygh/Home/MyAttention').text)
