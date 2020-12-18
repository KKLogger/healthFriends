import pandas as pd
import re
""" dataset_list -> data로 바꾸기 하나의 데이터를 어떤 대,중,소 분류를 갖는지 반환"""

#
# def large_classificate(standard_dict, mapping_dict, dataset_list):
#     """
#     :param standard_dict: 제품분류기준.csv -> dict
#     :param mapping_dict: 원료번역.csv -> dict ( 반입 금지 물품 )
#     :param dataset_list: 분류 할 데이터 dict list (각 원소는 csv 파일 -> dict )
#     :return: 대분류가 완료되어 각 key가 대분류 이름인 값
#     """
#     """
#     대분류 -> 소분류
#     """
#     result = dict()
#     result["프로틴"] = list()
#     result["운동보조제"] = list()
#     result["다이어트보조제"] = list()
#     result["반입금지"] = list()
#     result["기타"] = list()
#     result["예외"] = list()
#     ban_list = list()
#     print(set(standard_dict[0]["Unnamed: 1"].split("\n")))
#     input()
#     for item in mapping_dict[947:]:
#         # temp = item['통일'].split("\n")
#         # ban_list += temp
#         ban_list.append(item["통일"])
#
#     for dataset in dataset_list:
#         for data in dataset:
#             try:
#                 if bool(list(set(data["원료 성분"]) & set(ban_list))):  # 반입금지
#                     result["반입금지"].append(data["제품명"])
#                     data["대분류"] = "반입금지"
#                     data["중분류"] = "반입금지"
#                     data["소분류"] = "반입금지"
#                 elif "바" in data["1회제공량"]:  # 기타
#                     result["기타"].append(data["제품명"])
#                     data["대분류"] = "기타"
#                     data["중분류"] = "간식"
#                     if "프로틴" in data["원료 성분"]:
#                         data["소분류"] = "프로틴바"
#                     else:
#                         data["소분류"] = "에너지바"
#                 elif "젤" in data["제품명"]:  # 기타
#                     result["기타"].append(data["제품명"])
#                     data["대분류"] = "기타"
#                     data["중분류"] = "간식"
#                     data["소분류"] = "케이크"
#                 elif "칩" in data["1회제공량"]:  # 기타
#                     result["기타"].append(data["제품명"])
#                     data["대분류"] = "기타"
#                     data["중분류"] = "간식"
#                     data["소분류"] = "과자"
#                 elif "아몬드" in data["제품명"]:  # 기타
#                     result["기타"].append(data["제품명"])
#                     data["대분류"] = "기타"
#                     data["중분류"] = "간식"
#                     data["소분류"] = "아몬드"
#                 elif "케이크" in data["제품명"]:  # 기타
#                     result["기타"].append(data["제품명"])
#                     data["대분류"] = "기타"
#                     data["중분류"] = "간식"
#                     data["소분류"] = "케이크"
#                 elif bool(
#                     list(
#                         set(data["원료 성분"])
#                         & set(standard_dict[0]["Unnamed: 1"].split("\n"))
#                     )
#                 ):  # 프로틴
#                     result["프로틴"].append(data["제품명"])
#                     data["대분류"] = "프로틴"
#                     data["중분류"] = "프로틴"
#                     data["소분류"] = "프로틴"
#                     if "크레아틴" in data["원료 성분"]:
#                         data["중분류"] = "올인원"
#                         data["소분류"] = "올인원"
#
#                     elif "물" in data["원료 성분"]:
#                         data["중븐류"] = "RTD/드링크"
#                         data["소분류"] = "RTD/드링크"
#
#                     elif bool(
#                         list(
#                             set(data["원료 성분"])
#                             & set(standard_dict[0]["전체 원료"].split("\n"))
#                         )
#                     ):  # 유청단백
#                         if bool(
#                             list(
#                                 set(data["원료 성분"])
#                                 & set(standard_dict[8]["전체 원료"].split("\n"))
#                             )
#                         ):  # 혼합단백
#                             data["중분류"] = "혼합단백"
#                         else:
#                             data["중분류"] = "유청단백"
#                     elif bool(
#                         list(
#                             set(data["원료 성분"])
#                             & set(standard_dict[8]["전체 원료"].split("\n"))
#                         )
#                     ):  # 우유단백
#                         data["중분류"] = "우유단백"
#                     elif bool(
#                         list(
#                             set(data["원료 성분"])
#                             & set(standard_dict[12]["전체 원료"].split("\n"))
#                         )
#                     ):  # 식물성단백
#                         data["중분류"] = "식물성단백"
#                     else:
#                         data["중분류"] = "예외"
#                         data["소분류"] = "예외"
#                 elif bool(
#                     list(
#                         set(data["원료 성분"])
#                         & set(
#                             standard_dict[19]["Unnamed: 1"]
#                             .replace("/", "\n")
#                             .split("\n")
#                         )
#                     )
#                 ):  # 운동보조제
#                     result["운동보조제"].append(data["제품명"])
#                     data["대분류"] = "운동보조제"
#                     data["중분류"] = "운동보조제"
#                     data["소분류"] = "운동보조제"
#                     if list(
#                         set(data["원료 성분"]) & set(standard_dict[19]["전체 원료"].split("\n"))
#                     ):  # 아미노산
#                         data["중분류"] = "아미노산"
#                     elif list(
#                         set(data["원료 성분"]) & set(standard_dict[25]["전체 원료"].split("\n"))
#                     ):  # 부스터
#                         data["중분류"] = "부스터"
#                     else:
#                         data["중분류"] = "스포츠드링크"
#                 elif bool(
#                     list(
#                         set(data["원료 성분"]) & set(standard_dict[34]["전체 원료"].split("\n"))
#                     )
#                 ):  # 다이어트보조제
#                     result["다이어트보조제"].append(data["제품명"])
#                     data["대분류"] = "다이어트보조제"
#                     data["중분류"] = "다이어트보조제"
#                     data["소분류"] = "다이어트보조제"
#                 else:  # 예외
#                     result["예외"].append(data["제품명"])
#                     data["대분류"] = "예외"
#                     data["중분류"] = "예외"
#                     data["소분류"] = "예외"
#             except Exception as e:
#                 print(f"Error : {e}")
#                 print(data["1회제공량"])
#     return result


def small_classificate(standard_dict, mapping_dict, dataset_list):
    """
    :param standard_dict: 제품분류기준.csv -> dict
    :param mapping_dict: 원료번역.csv -> dict ( 반입 금지 물품 )
    :param dataset_list: 분류 할 데이터 dict list (각 원소는 csv 파일 -> dict )
    :return: 소분류 완료되어 각 key가 소분류 이름인 값
    """
    """
    대분류 -> 소분류
    """
    result = dict()
    class_list = list()
    # 소분류 분류 값 지정
    for row in standard_dict[:50]:
        if type(row["소분류"]) == float:
            if type(row["중분류"]) == float:
                result[row["대분류"]] = list()
            else:
                result[row["중분류"]] = list()
        else:
            if row["소분류"] == "기타":
                # 기타는 중분류 마다 존재 -> 각 중분류마다 기타 key값 생성
                pass
            else:
                result[row["소분류"]] = list()
    # 반입 금지 물품 목록
    ban_list = list()
    for item in mapping_dict[947:]:
        ban_list.append(item["통일"])
    for dataset in dataset_list:
        for data in dataset:
            # 성분 ( 단백질, 탄수화물 단위 통일 및 Nan Pass )
            if type(data['단백질(g)']) == float or type(data['총 탄수화물(g)']) == float:
                data['단백질(g)'] = 3
                data['총 탄수화물(g)'] = 1
            else:
                data['단백질(g)'] = re.findall('\d+',data['단백질(g)'])
                data['총 탄수화물(g)'] = re.findall('\d+',data['총 탄수화물(g)'])
            # 분류 시작
            if bool(list(set(data["원료 성분"]) & set(ban_list))):  # 반입금지
                result["반입금지"].append(data["제품명"])
                data["대분류"] = "반입금지"
                data["중분류"] = "반입금지"
                data["소분류"] = "반입금지"
            elif "바" in data["1회제공량"]:
                data["대분류"] = "기타"
                data["중분류"] = "간식"
                if "프로틴" in data["원료 성분"]:  # 프로틴바
                    result["프로틴바"].append(data["제품명"])
                    data["소분류"] = "프로틴바"
                else:  # 에너지바
                    data["소분류"] = "에너지바"
                    result["에너지바"].append(data["제품명"])
            elif "젤" in data["제품명"]:  # 에너지젤
                result["에너지젤"].append(data["제품명"])
                data["대분류"] = "기타"
                data["중분류"] = "간식"
                data["소분류"] = "에너지젤"
            elif "칩" in data["1회제공량"] or "조각" in data["1회제공량"]:  # 과자
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
                    set(data["원료 성분"]) & set(standard_dict[0]["Unnamed: 1"].split("\n"))
                )
            ):  # 프로틴
                data["대분류"] = "프로틴"
                if "크레아틴" in data["원료 성분"]:  # 올인원
                    data["중분류"] = "올인원"
                    data["소분류"] = "올인원"
                    result["올인원"] = data["제품명"]  # RTD/드링크
                elif "물" in data["원료 성분"]:
                    data["중븐류"] = "RTD/드링크"
                    data["소분류"] = "RTD/드링크"
                    result["RTD/드링크"] = data["제품명"]
                elif data['단백질(g)'] <= data['총 탄수화물(g)'] * 2:
                    data['중분류']  = '식사대용/게이너'
                    data['소분류'] = '식사대용/게이너'
                    result['식사대용/게이너'] = data['제품명']
                elif bool(
                    list(
                        set(data["원료 성분"]) & set(standard_dict[0]["전체 원료"].split("\n"))
                    )
                ) and bool(
                    list(
                        set(data["원료 성분"])
                        & set(
                            standard_dict[8]["전체 원료"].split("\n")
                            + standard_dict[6]["전체 원료"].split("\n")
                        )
                    )
                ):  # 혼합단백
                    data["중분류"] = "혼합단백"
                    if bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[0]["전체 원료"].split("\n"))
                        )
                    ) and bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[8]["전체 원료"].split("\n"))
                        )
                    ):  # 유청 + 우유
                        data["소분류"] = "유청 + 우유"
                        result["유청 + 우유"] = data["제품명"]
                    else:  # 유청 + 기타
                        data["소분류"] = "유청 + 기타"
                        result["유청 + 기타"] = data["제품명"]
                elif bool(
                    list(
                        set(data["원료 성분"]) & set(standard_dict[0]["전체 원료"].split("\n"))
                    )
                ):  # 유청단백
                    data["중분류"] = "유청단백"
                    if (
                        len(
                            list(
                                set(data["원료 성분"])
                                & set(standard_dict[0]["전체 원료"].split("\n"))
                            )
                        )
                        >= 2
                    ):  # 혼합유청단백
                        data["소분류"] = "혼합유청단백"
                        result["혼합유청단백"] = data["제품명"]
                    elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[0]["분류기준"].split("\n"))
                        )
                    ):  # 농축유청단백(WPC)
                        data["소분류"] = "농축유청단백(WPC)"
                        result["농축유청단백(WPC)"] = data["제품명"]
                    elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[1]["분류기준"].split("\n"))
                        )
                    ):  # 분리유청단백(WPI)
                        data["소분류"] = "분리유청단백(WPI)"
                        result["분리유청단백(WPI)"] = data["제품명"]
                    elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[2]["분류기준"].split("\n"))
                        )
                    ):  # 가수분해농축유청단백(WPH)
                        data["소분류"] = "가수분해농축유청단백(WPH)"
                        result["가수분해농축유청단백(WPH)"] = data["제품명"]
                    elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[3]["분류기준"].split("\n"))
                        )
                    ):  # 가수분해분리유청단백(WPIH)
                        data["소분류"] = "가수분해분리유청단백(WPIH)"
                        result["가수분해분리유청단백(WPIH)"] = data["제품명"]
                    else:
                        data["소분류"] = "유청단백기타"
                        if '유청단백기타' in result.keys():
                            pass
                        else:
                            result["유청단백기타"] = list()
                        result["유청단백기타"].append(data["제품명"])
                elif bool(
                    list(
                        set(data["원료 성분"]) & set(standard_dict[8]["전체 원료"].split("\n"))
                    )
                ):  # 우유단백
                    data["중분류"] = "우유단백"
                    if (
                        len(
                            list(
                                set(data["원료 성분"])
                                & set(standard_dict[8]["전체 원료"].split("\n"))
                            )
                        )
                        >= 2
                    ):  # 혼합우유단백
                        data["소분류"] = "혼합"
                        result["혼합"] = data["제품명"]
                    elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[8]["분류기준"].split("\n"))
                        )
                    ):  # 농축우유단백(MPC)
                        data["소분류"] = "농축우유단백(MPC)"
                        result["농축우유단백(MPC)"] = data["제품명"]
                    elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[9]["분류기준"].split("\n"))
                        )
                    ):  # 분리우유단백(MPI)
                        data["소분류"] = "분리우유단백(MPI)"
                        result["분리우유단백(MPI)"] = data["제품명"]
                    elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[10]["분류기준"].split("\n"))
                        )
                    ):  # 카제인
                        data["소분류"] = "카제인"
                        result["카제인"] = data["제품명"]
                    else:
                        data["소분류"] = "우유단백기타"
                        if '우유단백기타' in result.keys():
                            pass
                        else:
                            result["유청단백기타"] = list()
                        result["우유단백기타"].append(data["제품명"])
                elif bool(
                    list(
                        set(data["원료 성분"]) & set(standard_dict[12]["전체 원료"].split("\n"))
                    )
                ):  # 식물성단백
                    data["중분류"] = "식물성단백"
                    if (
                        len(
                            list(
                                set(data["원료 성분"])
                                & set(standard_dict[12]["전체 원료"].split("\n"))
                            )
                        )
                        >= 2
                    ):  # 혼합식물성단백
                        data["소분류"] = "혼합혼합식물성단백"
                        result["혼합식물성단백"] = data["제품명"]
                    elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[12]["분류기준"].split("\n"))
                        )
                    ):  # 대두
                        data["소분류"] = "대두"
                        result["대두"] = data["제품명"]
                    elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[13]["분류기준"].split("\n"))
                        )
                    ):  # 완두
                        data["소분류"] = "완두"
                        result["완두"] = data["제품명"]
                    elif bool(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[10]["분류기준"].split("\n"))
                        )
                    ):  # 현미
                        data["소분류"] = "현미"
                        result["현미"] = data["제품명"]
                    else:
                        data["소분류"] = "식물성단백기타"
                        if '식물성단백기타' in result.keys():
                            pass
                        else:
                            result["식물성단백기타"] = list()
                        result["식물성단백기타"].append(data["제품명"])
                else:
                    data["중분류"] = "프로틴예외"
                    data["소분류"] = "프로틴예외"
                    if '프로틴예외' in result.keys():
                        pass
                    else:
                        result["프로틴예외"] = list()
                    result["프로틴예외"].append(data["제품명"])
            elif bool(
                list(
                    set(data["원료 성분"])
                    & set(
                        standard_dict[19]["Unnamed: 1"].replace("/", "\n").split("\n")
                    )
                )
            ):  # 운동보조제
                data["대분류"] = "운동보조제"
                data["중분류"] = "운동보조제"
                if list(
                    set(data["원료 성분"]) & set(standard_dict[19]["전체 원료"].split("\n"))
                ):  # 아미노산
                    data["중분류"] = "아미노산"
                    if (
                        len(
                            list(
                                set(data["원료 성분"])
                                & set(standard_dict[19]["전체 원료"].split("\n"))
                            )
                        )
                        >= 2
                    ):
                        data["소분류"] = "혼합아미노산"
                        result["혼합아미노산"].append(data["제품명"])
                    elif list(
                        set(data["원료 성분"]) & set(standard_dict[19]["분류기준"].split("\n"))
                    ):
                        data["소분류"] = "BCAA"
                        result["BCAA"].append(data["제품명"])
                    elif list(
                        set(data["원료 성분"]) & set(standard_dict[20]["분류기준"].split("\n"))
                    ):
                        data["소분류"] = "EAA"
                        result["EAA"].append(data["제품명"])
                    elif list(
                        set(data["원료 성분"]) & set(standard_dict[21]["분류기준"].split("\n"))
                    ):
                        data["소분류"] = "글루타민"
                        result["글루타민"].append(data["제품명"])
                    elif list(
                        set(data["원료 성분"]) & set(standard_dict[22]["분류기준"].split("\n"))
                    ):
                        data["소분류"] = "HMB"
                        result["HMB"].append(data["제품명"])
                    else:
                        data["소분류"] = "아미노산기타"
                        if '아미노산기타' in result.keys():
                            pass
                        else:
                            result["아미노산기타"] = list()
                        result["아미노산기타"].append(data["제품명"])

                elif list(
                    set(data["원료 성분"]) & set(standard_dict[25]["전체 원료"].split("\n"))
                ):  # 부스터
                    data["중분류"] = "부스터"
                    if len(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[25]["전체 원료"].split("\n"))
                        )
                    ):  # 혼합부스터
                        data["소분류"] = "혼합부스터"
                        result["혼합부스터"].append(data["제품명"])
                    elif list(
                        set(data["원료 성분"]) & set(standard_dict[25]["분류기준"].split("\n"))
                    ):  # 크레아틴
                        data["소분류"] = "크레아틴"
                        result["크레아틴"].append(data["제품명"])
                    elif list(
                        set(data["원료 성분"]) & set(standard_dict[25]["분류기준"].split("\n"))
                    ):  # 카페인
                        data["소분류"] = "카페인"
                        result["카페인"].append(data["제품명"])
                    elif list(
                        set(data["원료 성분"]) & set(standard_dict[25]["분류기준"].split("\n"))
                    ):  # 아르기닌
                        data["소분류"] = "아르기닌"
                        result["아르기닌"].append(data["제품명"])
                    elif list(
                        set(data["원료 성분"]) & set(standard_dict[25]["분류기준"].split("\n"))
                    ):  # 시트룰린
                        data["소분류"] = "시트룰린"
                        result["시트룰린"].append(data["제품명"])
                    elif list(
                        set(data["원료 성분"]) & set(standard_dict[25]["분류기준"].split("\n"))
                    ):  # 베타알라닌
                        data["소분류"] = "베타알라닌"
                        result["베타알라닌"].append(data["제품명"])
                    elif list(
                        set(data["원료 성분"]) & set(standard_dict[25]["분류기준"].split("\n"))
                    ):  # 아그마틴
                        data["소분류"] = "아그마틴"
                        result["아그마틴"].append(data["제품명"])
                    else:
                        data["소분류"] = "부스터기타"
                        if '부스터기타' in result.keys():
                            pass
                        else:
                            result["부스터기타"] = list()
                        result["부스터기타"].append(data["제품명"])
                else:
                    data["중분류"] = "스포츠드링크"
            elif bool(
                list(set(data["원료 성분"]) & set(standard_dict[34]["전체 원료"].split("\n")))
            ):  # 다이어트보조제
                data["대분류"] = "다이어트보조제"
                data["중분류"] = "다이어트보조제"
                if (
                    len(
                        list(
                            set(data["원료 성분"])
                            & set(standard_dict[34]["전체 원료"].split("\n"))
                        )
                    )
                    >= 2
                ):  # 혼합다이어트보조제
                    data["소분류"] = "혼합다이어트보조제"
                    result["혼합다이어트보조제"].append(data["제품명"])
                elif list(
                    set(data["원료 성분"]) & set(standard_dict[34]["분류기준"].split("\n"))
                ):  # 녹차추출물
                    data["소분류"] = "녹차추출물"
                    result["녹차추출물"].append(data["제품명"])
                elif list(
                    set(data["원료 성분"]) & set(standard_dict[35]["분류기준"].split("\n"))
                ):  # 공액리놀레산
                    data["소분류"] = "공액리놀레산"
                    result["공액리놀레산"].append(data["제품명"])
                elif list(
                    set(data["원료 성분"]) & set(standard_dict[36]["분류기준"].split("\n"))
                ):  # 가르시니아
                    data["소분류"] = "가르시니아"
                    result["가르시니아"].append(data["제품명"])
                elif list(
                    set(data["원료 성분"]) & set(standard_dict[37]["분류기준"].split("\n"))
                ):  # 키토산
                    data["소분류"] = "키토산"
                    result["키토산"].append(data["제품명"])
                elif list(
                    set(data["원료 성분"]) & set(standard_dict[38]["분류기준"].split("\n"))
                ):  # 카르니틴
                    data["소분류"] = "카르니틴"
                    result["카르니틴"].append(data["제품명"])
                elif list(
                    set(data["원료 성분"]) & set(standard_dict[39]["분류기준"].split("\n"))
                ):  # 콜레우스포스콜리
                    data["소분류"] = "콜레우스포스콜리"
                    result["콜레우스포스콜리"].append(data["제품명"])
                elif list(
                    set(data["원료 성분"]) & set(standard_dict[35]["분류기준"].split("\n"))
                ):  # 그린커피추출물
                    data["소분류"] = "그린커피추출물"
                    result["그린커피추출물"].append(data["제품명"])
                else:
                    data["소분류"] = "다이어트보조제기타"
                    if '다이어트보조제기타' in result.keys():
                        pass
                    else:
                        result["다이어트보조제기타"] = list()
                    result["다이어트보조제기타"].append(data["제품명"])
            else:  # 예외
                if '예외' in result.keys():
                    pass
                else:
                    result["예외"] = list()
                print(data['원료 성분'])
                result["예외"].append(data["제품명"])
                data["대분류"] = "예외"
                data["중분류"] = "예외"
                data["소분류"] = "예외"
    print(result)
    return result
