import pickle
import pandas as pd

result = list()
num = 0
# 이미 수집된 df 를 가지고 url 불러오기
# df = pd.read_excel('../data/url.xlsx')
# urls = df['URL']
# urls = list(set(urls))
# print(len(urls))
# # #
# with open("../data/option_urls.pickle", "rb") as f:
#     while True:
#         try:
#             num += 1
#             result +=pickle.load(f)
#
#         except:
#             break
#
# print(len(result))
# print(num)

# basic_df_dict 확인
with open("../../data/coupang/basic_df_dict.pickle", "rb") as f:
    while True:
        try:
            temp = pickle.load(f)
            result.append(temp)
        except:
            break
print(len(result))
result = [x for x in result if x is not None]
df = pd.DataFrame.from_dict(result)
"""
URL 기준 중복 제거
"""
df = df.drop_duplicates(["URL"])
result = df.to_dict("records")
print(len(result))
df = pd.DataFrame.from_dict(result)
writer = pd.ExcelWriter(
    "D:/UpennSolution/health_friends/data/coupang/basic_df_dict.xlsx",
    engine="xlsxwriter",
    options={"strings_to_urls": False},
)


df.to_excel(writer)
writer.save()

# result = list()
# # check 원료성분단어 확인
# with open('../data/backup/원료성분단어 확인.pickle', 'rb') as f:
#     while True:
#         try:
#             num += 1
#             temp = pickle.load(f)
#             result.append(temp)
#         except:
#             break
#
# print(len(result))
# result = [x for x in result if x is not None]
# df = pd.DataFrame.from_dict(result)
# df.to_excel("원료성분단어 확인.xlsx", engine="xlsxwriter")
