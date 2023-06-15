from main import YoutubePage

words = {
  "科技": ["Teknologi"],
  "医疗与健康": ["Penjagaan Kesihatan dan Kesihatan"],
  "时尚与生活": ["Fesyen dan Gaya Hidup"],
  "文化": ["Budaya"],
  "政治": ["Politik"],
  "环境（自然）": ["Alam Sekitar (Semula Jadi)"],
  "体育": ["Sukan"],
  "教育": ["Pendidikan"],
  "娱乐": ["Hiburan"],
  "经济": ["Ekonomi"]
}



# 打印每个领域的词汇
for category, category_words in words.items():
    print(f'mult-lang===vd_videos===uk==={category}')
    for word in category_words:
        ytp = YoutubePage(word, 10)
        for i in ytp.get_all_channel():
            print(i)
    print('\n\n')


