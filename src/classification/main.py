import pandas as pd
import json
import numpy as np
import math
import re
import ast

import item_classificater
import word_translater

def load_dataset(dataset_name):
    """
    :param dataset_name: dataset이 저장되어 있는 엑셀파일 이름
    :return: csv 파일 -> DF -> dict
    """
    result = pd.read_excel(f"../../data/classification/{dataset_name}")
    # Nan 값 삭제
    result = result[result["원료 성분"].notnull()]
    result = result[result["1회제공량"].notnull()]
    result = result[result["제품명"].notnull()]
    result = result.to_dict("records")
    return result


def replaceText(text, replace_char):
    # 텍스트에 포함되어 있는 특수 문자 제거
    result = re.sub("[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`'…》]", replace_char, text)
    return result


import os

if __name__ == "__main__":
    standard_dict = pd.read_excel("../../data/common/제품 분류 기준(전송용).xlsx").to_dict("records")
    mapping_dict = pd.read_excel("../../data/common/원료 번역.xlsx")
    translate_dict = word_translater.get_translate_dict(mapping_dict)
    mapping_dict = mapping_dict.to_dict("records")
    dataset_name_list = [
        # "01.쿠팡.xlsx",
        # "365Muscle.xlsx",
        # "iHerb.xlsx",
        # "IronMax.xlsx",
        # "MonsterMart.xlsx",
        # "MyProtein.xlsx",
        # "Ople.xlsx",
        # "4개_외국사이트_종합.xlsx"
        # "basic_df_dict.xlsx"
        "clean_coupang.xlsx"
    ]
    """ 각 데이터에 번역함수 호출"""
    l_temp = list()
    for dataset_name in dataset_name_list:
        dataset = load_dataset(dataset_name)
        temp = list()
        for data in dataset:
            try:
                data["유통사"] = dataset_name.split(".")[0]
                # data["원료 성분"] = (
                #     replaceText(data["원료 성분"], ",")
                #     .replace("†", ",")
                #     .replace("\n", ",")
                #     .replace("‡", ",")
                #     .replace("and", ",")
                #     .split(",")
                # )
                try:
                    math.isnan(data['원료 성분(단어)'])
                    data['원료 성분(단어)']=''
                except:
                    data["원료 성분(단어)"] = ast.literal_eval(data['원료 성분(단어)'])
                    data["원료 성분(단어)"] = [
                        word_translater.word_translater(translate_dict, x).strip()
                        for x in data["원료 성분(단어)"]
                    ]
                temp.append(data)
            except Exception as e:
                print(f"Error : {e} in 원료성분 (단어)")
                print(data['원료 성분(단어)'])
        l_temp.append(temp)
    dataset_list = l_temp
    result = item_classificater.small_classificate(
        standard_dict, mapping_dict, dataset_list
    )

    with open("../../data/classification/result.json", "w", encoding="utf-8-sig") as f:
        json.dump(result, f, ensure_ascii=False)
    dataset_list = sum(dataset_list, [])
    result = pd.DataFrame.from_dict(dataset_list)
    # 테스트 결과를 위한 저장
    # result = result[
    #     ["제품명", "원료 성분", "1회제공량", "총 탄수화물(g)", "단백질(g)", "대분류", "중분류", "소분류"]
    # ]


    # result.to_excel("../../data/classification/분류결과.xlsx")

    writer = pd.ExcelWriter(
        "D:/UpennSolution/health_friends/data/classification/result_coupang.xlsx",
        engine="xlsxwriter",
        options={"strings_to_urls": False},
    )
    result.to_excel(writer)
    writer.save()
