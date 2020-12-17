# -*- coding: utf-8 -*-
import pandas as pd
import json


def compareName(nameList, fullName):
    for name in nameList:
        if name in fullName:
            return True
    return False


""" 파일 읽어오기"""
classification = pd.read_excel("data/제품 분류 기준(전송용).xlsx")
mappingDF = pd.read_excel("data/원료 번역.xlsx")
dataset = pd.read_excel("data/06.몬스터마트.xlsx").to_dict("records")

"""분류 기준 딕셔너리 생성"""
largeCategorical = dict()
mediumCategorical = dict()
smallCategorical = dict()
largeCategorical["프로틴"] = classification["Unnamed: 1"][0].split("\n")[:-1]
largeCategorical["운동보조제"] = classification["Unnamed: 1"][19].split("\n")
largeCategorical["반입금지"] = list()
for item in mappingDF["이명"][947:]:
    temp = item.split("\n")
    largeCategorical["반입금지"] += temp
largeCategorical["기타"] = list(classification["소분류"][43:48])
largeCategorical["다이어트보조제"] = classification["전체 원료"][34].split("\n")

# 데이터 분류
largeCategoricalResult = dict()
largeCategoricalResult["프로틴"] = list()
largeCategoricalResult["운동보조제"] = list()
largeCategoricalResult["다이어트보조제"] = list()
largeCategoricalResult["간식"] = list()
largeCategoricalResult["반입금지"] = list()
largeCategoricalResult["예외"] = list()
mediumCategoricalResult = dict()
smallCategoricalResult = dict()
"""
데이터 모두 저장
"""
# for item in dataset:
#     try:
#         if bool(list(set(item['원료 성분']) & set(largeCategorical['반입금지']))):
#             largeCategoricalResult['반입금지'].append(item)
#         elif compareName(largeCategorical['기타'],item['제품명']):
#             largeCategoricalResult['기타'].append(item)
#         elif bool(list(set(item['원료 성분']) & set(largeCategorical['프로틴']))):
#             largeCategoricalResult['프로틴'].append(item)
#         elif bool(list(set(item['원료 성분']) & set(largeCategorical['운동보조제']))):
#             largeCategoricalResult['운동보조제'].append(item)
#         elif bool(list(set(item['원료 성분']) & set(largeCategorical['다이어트보조제']))):
#             largeCategoricalResult['다이어트보조제'].append(item)
#         else:
#             largeCategoricalResult['예외'].append(item)
#     except Exception as e:
#         print(f'error : {e}')
#         largeCategoricalResult['예외'].append(item)
"""
데이터 이름만 저장
"""
for item in dataset:
    try:
        if "|||" in item["원료 성분"]:
            item["원료 성분"] = item["원료 성분"].replace(".", "").split("|||")
        else:
            item["원료 성분"] = item["원료 성분"].replace(".", "").split(",")
        # 반입금지
        if bool(list(set(item["원료 성분"]) & set(largeCategorical["반입금지"]))):
            largeCategoricalResult["반입금지"].append(item["제품명"])
        # 기타(간식)
        elif compareName(largeCategorical["간식"], item["제품명"]):
            largeCategoricalResult["간식"].append(item["제품명"])
        elif bool(list(set(item["원료 성분"]) & set(largeCategorical["프로틴"]))):
            largeCategoricalResult["프로틴"].append(item["제품명"])
        elif bool(list(set(item["원료 성분"]) & set(largeCategorical["운동보조제"]))):
            largeCategoricalResult["운동보조제"].append(item["제품명"])
        elif bool(list(set(item["원료 성분"]) & set(largeCategorical["다이어트보조제"]))):
            largeCategoricalResult["다이어트보조제"].append(item["제품명"])
        else:
            largeCategoricalResult["예외"].append(item["제품명"])
    except Exception as e:
        print(f"error : {e}")
        largeCategoricalResult["예외"].append(item["제품명"])

with open("data/대분류.json", "w", encoding="utf-8") as f:
    json.dump(largeCategoricalResult, f, ensure_ascii=False)
