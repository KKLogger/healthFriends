import pandas as pd

""" dataset_list -> data로 바꾸기 하나의 데이터를 어떤 대,중,소 분류를 갖는지 반환"""


def large_classificate(standard_dict, mapping_dict, dataset_list):
    """
    :param standard_dict: 제품분류기준.csv -> dict
    :param mapping_dict: 원료번역.csv -> dict ( 반입 금지 물품 )
    :param dataset_list: 분류 할 데이터 dict list (각 원소는 csv 파일 -> dict )
    :return: 대분류가 완료되어 각 key가 대분류 이름인 값
    """
    '''
    대분류 -> 소분류
    '''
    result = dict()
    result["프로틴"] = list()
    result["운동보조제"] = list()
    result["다이어트보조제"] = list()
    result["반입금지"] = list()
    result["기타"] = list()
    result["예외"] = list()
    ban_list = list()
    print(set(standard_dict[0]["Unnamed: 1"].split("\n")))
    input()
    for item in mapping_dict[947:]:
        # temp = item['통일'].split("\n")
        # ban_list += temp
        ban_list.append(item["통일"])

    for dataset in dataset_list:
        for data in dataset:
            try:
                if bool(list(set(data["원료 성분"]) & set(ban_list))):  # 반입금지
                    result["반입금지"].append(data["제품명"])
                    data["대분류"] = "반입금지"
                    data["중분류"] = "반입금지"
                    data["소분류"] = "반입금지"
                elif "바" in data["1회제공량"]:  # 기타
                    result["기타"].append(data["제품명"])
                    data["대분류"] = "기타"
                    data["중분류"] = "간식"
                    if "프로틴" in data["원료 성분"]:
                        data["소분류"] = "프로틴바"
                    else:
                        data["소분류"] = "에너지바"
                elif "젤" in data["제품명"]:  # 기타
                    result["기타"].append(data["제품명"])
                    data["대분류"] = "기타"
                    data["중분류"] = "간식"
                    data["소분류"] = "케이크"
                elif "칩" in data["1회제공량"]:  # 기타
                    result["기타"].append(data["제품명"])
                    data["대분류"] = "기타"
                    data["중분류"] = "간식"
                    data["소분류"] = "과자"
                elif "아몬드" in data["제품명"]:  # 기타
                    result["기타"].append(data["제품명"])
                    data["대분류"] = "기타"
                    data["중분류"] = "간식"
                    data["소분류"] = "아몬드"
                elif "케이크" in data["제품명"]:  # 기타
                    result["기타"].append(data["제품명"])
                    data["대분류"] = "기타"
                    data["중분류"] = "간식"
                    data["소분류"] = "케이크"
                elif bool(
                    list(
                        set(data["원료 성분"])
                        & set(standard_dict[0]["Unnamed: 1"].split("\n"))
                    )
                ):  # 프로틴
                    result["프로틴"].append(data["제품명"])
                    data["대분류"] = "프로틴"
                    data["중분류"] = "프로틴"
                    data["소분류"] = "프로틴"
                    if '크레아틴' in data['원료 성분']:
                        data['중분류'] = '올인원'
                        data["소분류"] = "올인원"

                    elif '물' in data['원료 성분'] :
                        data['중븐류'] = 'RTD/드링크'
                        data["소분류"] = "RTD/드링크"

                    elif bool(list(set(data['원료 성분']) & set(standard_dict[0]['전체 원료'].split('\n')))): # 유청단백
                        if bool(list(set(data['원료 성분']) & set(standard_dict[8]['전체 원료'].split('\n')))): # 혼합단백
                            data['중분류'] = '혼합단백'
                        else:
                            data['중분류'] = '유청단백'
                    elif bool(list(set(data['원료 성분']) & set(standard_dict[8]['전체 원료'].split('\n')))): # 우유단백
                        data['중분류'] = '우유단백'
                    elif bool(list(set(data['원료 성분']) & set(standard_dict[12]['전체 원료'].split('\n')))):  # 식물성단백
                        data['중분류'] = '식물성단백'
                    else:
                        data['중분류'] = '예외'
                        data['소분류'] = '예외'
                elif bool(
                    list(
                        set(data["원료 성분"])
                        & set(
                            standard_dict[19]["Unnamed: 1"]
                            .replace("/", "\n")
                            .split("\n")
                        )
                    )
                ):  # 운동보조제
                    result["운동보조제"].append(data["제품명"])
                    data["대분류"] = "운동보조제"
                    data["중분류"] = "운동보조제"
                    data["소분류"] = "운동보조제"
                    if list(set(data["원료 성분"]) & set(standard_dict[19]["전체 원료"].split("\n"))): # 아미노산
                        data['중분류'] = '아미노산'
                    elif list(set(data["원료 성분"]) & set(standard_dict[25]["전체 원료"].split("\n"))): # 부스터
                        data['중분류'] = '부스터'
                    else:
                        data['중분류'] = '스포츠드링크'
                elif bool(
                    list(
                        set(data["원료 성분"]) & set(standard_dict[34]["전체 원료"].split("\n"))
                    )
                ):  # 다이어트보조제
                    result["다이어트보조제"].append(data["제품명"])
                    data["대분류"] = "다이어트보조제"
                    data["중분류"] = "다이어트보조제"
                    data["소분류"] = "다이어트보조제"
                else:  # 예외
                    result["예외"].append(data["제품명"])
                    data["대분류"] = "예외"
                    data["중분류"] = "예외"
                    data["소분류"] = "예외"
            except Exception as e:
                print(f"Error : {e}")
                print(data["1회제공량"])
    return result

def small_classificate(standard_dict, mapping_dict, dataset_list):
    """
    :param standard_dict: 제품분류기준.csv -> dict
    :param mapping_dict: 원료번역.csv -> dict ( 반입 금지 물품 )
    :param dataset_list: 분류 할 데이터 dict list (각 원소는 csv 파일 -> dict )
    :return: 소분류 완료되어 각 key가 소분류 이름인 값
    """
    '''
    대분류 -> 소분류
    '''
    result = dict()
    class_list =  list()
    # 소분류 분류 값 지정
    for row in standard_dict[:50]:
        if type(row['소분류']) == float:
            if type(row['중분류']) == float:
                result[row['대분류']] = list()
            else :
                result[row['중분류']] = list()
        else :
            result[row['소분류']] = list()
    #반입 금지 물품 목록
    ban_list = list()
    for item in mapping_dict[947:]:
        ban_list.append(item["통일"])
    #분류 시작
    for dataset in dataset_list:
        for data in dataset:
            try:
                if bool(list(set(data["원료 성분"]) & set(ban_list))):  # 반입금지
                    result["반입금지"].append(data["제품명"])
                    data["대분류"] = "반입금지"
                    data["중분류"] = "반입금지"
                    data["소분류"] = "반입금지"
                elif "바" in data["1회제공량"]:
                    data["대분류"] = "기타"
                    data["중분류"] = "간식"
                    if "프로틴" in data["원료 성분"]:# 프로틴바
                        result["프로틴바"].append(data['제품명'])
                        data['소분류'] = '프로틴바'
                    else: # 에너지바
                        data["소분류"] = "에너지바"
                        result["에너지바"].append(data['제품명'])
                elif "젤" in data["제품명"]:  # 에너지젤
                    result["에너지젤"].append(data["제품명"])
                    data["대분류"] = "기타"
                    data["중분류"] = "간식"
                    data["소분류"] = "에너지젤"
                elif "칩" in data["1회제공량"] or '조각' in data['1회제공량']:  # 과자
                    result["과자"].append(data["제품명"])
                    data["대분류"] = "기타"
                    data["중분류"] = "간식"
                    data["소분류"] = "과자"
                elif "아몬드" in data["제품명"]:  # 아몬드
                    result["아몬드"].append(data["제품명"])
                    data["대분류"] = "기타"
                    data["중분류"] = "간식"
                    data["소분류"] = "아몬드"
                elif "케이크" in data["제품명"]:  # 케이크
                    result["케이크"].append(data["제품명"])
                    data["대분류"] = "기타"
                    data["중분류"] = "간식"
                    data["소분류"] = "케이크"
                elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[0]["Unnamed: 1"].split("\n"))
                        )
                ):  # 프로틴
                    result["프로틴"].append(data["제품명"])
                    data["대분류"] = "프로틴"
                    data["중분류"] = "프로틴"
                    data["소분류"] = "프로틴"
                    if '크레아틴' in data['원료 성분']:
                        data['중분류'] = '올인원'
                        data["소분류"] = "올인원"

                    elif '물' in data['원료 성분']:
                        data['중븐류'] = 'RTD/드링크'
                        data["소분류"] = "RTD/드링크"

                    elif bool(list(set(data['원료 성분']) & set(standard_dict[0]['전체 원료'].split('\n')))):  # 유청단백
                        if bool(list(set(data['원료 성분']) & set(standard_dict[8]['전체 원료'].split('\n')))):  # 혼합단백
                            data['중분류'] = '혼합단백'
                        else:
                            data['중분류'] = '유청단백'
                    elif bool(list(set(data['원료 성분']) & set(standard_dict[8]['전체 원료'].split('\n')))):  # 우유단백
                        data['중분류'] = '우유단백'
                    elif bool(list(set(data['원료 성분']) & set(standard_dict[12]['전체 원료'].split('\n')))):  # 식물성단백
                        data['중분류'] = '식물성단백'
                    else:
                        data['중분류'] = '예외'
                        data['소분류'] = '예외'
                elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(
                                standard_dict[19]["Unnamed: 1"]
                                        .replace("/", "\n")
                                        .split("\n")
                            )
                        )
                ):  # 운동보조제
                    result["운동보조제"].append(data["제품명"])
                    data["대분류"] = "운동보조제"
                    data["중분류"] = "운동보조제"
                    data["소분류"] = "운동보조제"
                    if list(set(data["원료 성분"]) & set(standard_dict[19]["전체 원료"].split("\n"))):  # 아미노산
                        data['중분류'] = '아미노산'
                    elif list(set(data["원료 성분"]) & set(standard_dict[25]["전체 원료"].split("\n"))):  # 부스터
                        data['중분류'] = '부스터'
                    else:
                        data['중분류'] = '스포츠드링크'
                elif bool(
                        list(
                            set(data["원료 성분"]) & set(standard_dict[34]["전체 원료"].split("\n"))
                        )
                ):  # 다이어트보조제
                    result["다이어트보조제"].append(data["제품명"])
                    data["대분류"] = "다이어트보조제"
                    data["중분류"] = "다이어트보조제"
                    data["소분류"] = "다이어트보조제"
                else:  # 예외
                    result["예외"].append(data["제품명"])
                    data["대분류"] = "예외"
                    data["중분류"] = "예외"
                    data["소분류"] = "예외"
            except Exception as e:
                print(f"Error : {e}")
                print(data["1회제공량"])
    return result

