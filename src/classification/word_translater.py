import pandas as pd


def word_translater(dict_data, word):
    """
    :param dict_data: 원료 번역.csv to dict
    :param word: 번역(매핑)할 단어
    :return: translated word
    """
    result = word.lower()
    for data in dict_data:
        if word.lower() in data["이명"]:
            result = data["통일"]

    return result.strip()


def get_translate_dict(df):
    """
    :param df: 원료분석.csv to df
    :return: 필요없는 컬럼은 삭제한 df to dict
    """
    del df["대분류"]
    del df["용도(중분류)"]
    del df["주영양소(소분류)"]
    del df["일일섭취량"]
    del df["주의사항"]

    dict_data = df.to_dict("records")
    for data in dict_data:
        if type(data["이명"]) == float:
            print("이명 컬럼이 비어있는 통일값 : ", data["통일"], data["이명"])
            data["이명"] = [""]
        else:
            data["이명"] = data["이명"].split("\n")
            data["이명"] = [x.lower() for x in data["이명"]]
    return dict_data
