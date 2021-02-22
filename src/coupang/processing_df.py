import pickle
import pandas as pd
import math

df = pd.read_excel('../../data/coupang/basic_df_dict.xlsx')
df = df.drop_duplicates(["URL"])
df_dict = df.to_dict('records')


for data in df_dict:
    data['1회제공량'] = '값 없음'
    try:
        data['단백질(g)'] = float(data['단백질(g)'])
        data['총 탄수화물(g)'] = float(data['총 탄수화물(g)'])
    except:
        print(data['단백질(g)'],data['총 탄수화물(g)'])
        data['단백질(g)'] = math.nan
        data['총 탄수화물(g)'] = math.nan

df = pd.DataFrame.from_dict(df_dict)

writer = pd.ExcelWriter(
    "D:/UpennSolution/health_friends/data/coupang/basic_df_dict.xlsx",
    engine="xlsxwriter",
    options={"strings_to_urls": False},
)
df.to_excel(writer)
writer.save()