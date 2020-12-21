import pandas as pd
import json
import item_classificater
import word_translater
import numpy as np
import math
import re


def load_dataset(dataset_name_list):
    """
    :param dataset_name_list: dataset이 저장되어 있는 엑셀파일 이름 리스트
    :return: csv 파일 -> DF -> dict
    """
    result = list()
    for dataset_name in dataset_name_list:
        temp = pd.read_excel(f"data/{dataset_name}")
        # Nan 값 삭제
        temp = temp[temp["원료 성분"].notnull()]
        temp = temp[temp["1회제공량"].notnull()]
        temp = temp[temp["제품명"].notnull()]
        temp = temp.to_dict("records")

        result.append(temp)
    return result


def replaceText(text, replace_char):
    # 텍스트에 포함되어 있는 특수 문자 제거
    result = re.sub("[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`'…》]", replace_char, text)
    return result


import os

if __name__ == "__main__":
    standard_dict = pd.read_excel("./data/제품 분류 기준(전송용).xlsx").to_dict("records")
    mapping_dict = pd.read_excel("./data/원료 번역.xlsx")
    translate_dict = word_translater.get_translate_dict(mapping_dict)
    mapping_dict = mapping_dict.to_dict("records")
    dataset_name_list = [
        "01.쿠팡.xlsx",
        "02.아이허브.xlsx",
        "03.마이프로틴.xlsx",
        "04.오플.xlsx",
        "06.몬스터마트.xlsx",
    ]
    dataset_list = load_dataset(dataset_name_list)
    """ 각 데이터에 번역함수 호출"""
    l_temp = list()
    for dataset in dataset_list:
        temp = list()
        for data in dataset:
            try:
                data["원료 성분"] = (
                    replaceText(data["원료 성분"], ",")
                    .replace("†", ",")
                    .replace("\n", ",")
                    .replace('‡',',')
                    .replace('and',',')
                    .split(",")
                )

                data["원료 성분"] = [
                    word_translater.word_translater(translate_dict, x)
                    .strip()
                    .replace("'", "")
                    for x in data["원료 성분"]
                ]
                temp.append(data)
            except Exception as e:
                print(f"Error : {e}")
                # data['원료 성분'] 가 NaN 값일 때
                pass
        l_temp.append(temp)
    dataset_list = l_temp
    result = item_classificater.small_classificate(
        standard_dict, mapping_dict, dataset_list
    )
    with open("test.json", "w", encoding="utf-8-sig") as f:
        json.dump(result, f, ensure_ascii=False)
