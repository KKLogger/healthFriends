import requests
from bs4 import BeautifulSoup
from urllib.request import urljoin, build_opener, install_opener, urlretrieve
import re
import time
import pandas as pd
from urllib.parse import quote
"""
.py import 경로 설정
"""
sys.path.append('../common')
from preprocessing import *
from save_image import *

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
}
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=20)
session.mount("https://", adapter)
session.mount("http://", adapter)
req = session
ingr_list = get_ingredient_list()


def crawling_MyProtein(site_name, href, num, f_num):
    try:
        res = req.get(href, headers=headers)
        soup = BeautifulSoup(res.text, "lxml")
        temp = dict()
        if "The page is not found!" in soup.find("head").find("title").text:
            raise KeyboardInterrupt
        try:
            if (
                "죄송합니다. 본 제품은 일시품절되었습니다."
                in soup.find("h2", {"class": "productAlternativesWrapper_title"}).text
            ):
                raise KeyboardInterrupt
        except AttributeError:
            pass

        # 사진
        try:
            image = soup.select_one(
                'div[class="athenaProductImageCarousel_imageWrapper"]'
            ).find_all("span", {"data-size": True})
            image = {int(i.get("data-size")): i.get("data-path") for i in image}
            image = sorted(image.items(), reverse=True)[0][-1]
            image = urljoin(res.url, image)
            save_image(site_name, image, num, "product")
        except Exception as e:
            print(e)
            image = None
        # print(f'제품사진 : {image}')
        # 브랜드
        brand = "MYPROTEIN"
        # print(f'브랜드 : {brand}')
        # 제품명
        name = soup.find("h1", {"class": "productName_title"}).text.strip()
        # print(f'제품명 : {name}')

        try:
            # 맛
            flavor = (
                [
                    x
                    for x in soup.find_all(
                        "div", {"class": "productDescription_synopsisContent"}
                    )[-2].find_all("p")
                    if ":" in x.text
                ][f_num]
                .text.split(":")[0]
                .strip()
            )
        except AttributeError:
            print("맛 error")
            flavor = None
        # print(f'맛 : {flavor}')

        try:
            # 용량
            volume = soup.find("ul", {"athenaProductVariations_list"}).find_all("li")
            try:
                volume = (
                    [v for v in volume if v.span is not None][0]
                    .text.replace("selected", "")
                    .replace("선택 완료", "")
                    .strip()
                )
            except IndexError:
                try:
                    volume = (
                        [v for v in volume][0]
                        .text.replace("selected", "")
                        .replace("선택 완료", "")
                        .strip()
                    )
                except Exception as e:
                    print(e)
                    volume = None
        except AttributeError:
            volume = None
        # print(f'양 : {volume}')

        try:
            # 원료성분
            ingrd = (
                soup.find(
                    "div",
                    {"class": "productDescription_contentPropertyListItem_ingredients"},
                )
                .find("div", {"class": "productDescription_synopsisContent"})
                .find_all("p")
            )
            mingrd = (
                [
                    x
                    for x in soup.find_all(
                        "div", {"class": "productDescription_synopsisContent"}
                    )[-2].find_all("p")
                    if ":" in x.text
                ][f_num]
                .text.split(":")[1]
                .strip()
            )
            mingrd = remove_part(mingrd)
            ingr_words = substract_ingredient(mingrd, ingr_list)
            temp["원료성분"] = ingr_words
            temp["url"] = href
            # 알러지 성분
            aing = list(
                dict.fromkeys(
                    [
                        aa.text.strip().replace(",", "")
                        for a in ingrd
                        for aa in a.find_all("strong")
                    ]
                )
            )
            aingrd = "/".join([a for a in aing if a != "bold"])
        except AttributeError:
            print("성분 error")
            ingr_words = None
            mingrd = None
            aingrd = None

        # URL
        url = res.url
        # print(f"제품 URL : {url}")

        # 제품번호
        pcode = "/".join(url.split("/")[-2:]).replace(".html", "")
        # print(f"제품번호 : {pcode}")

        # 가격
        try:
            price = soup.find("p", {"class": "productPrice_price"}).text.strip()
        except Exception as e:
            print(e, "가격")
            price = None
        # print(f"가격 : {price}")

        stock = (
            True
            if "soldout"
            in "".join(
                soup.find("div", {"class": "athenaProductPage_actions"})
                .find("button")
                .get("class")
            ).lower()
            else False
        )
        # print(f"품절여부 : {stock}")

        nutri = [
            i
            for i in soup.find_all(
                "div", {"class": "productDescription_contentProperties"}
            )
            if "Serving Size -" in i.text.replace("\xa0", " ")
            or "1회 복용량 -" in i.text.replace("\xa0", " ")
            or "1회 제공량 -" in i.text.replace("\xa0", " ")
            or "1회 섭취량 -" in i.text.replace("\xa0", " ")
            or "서빙 사이즈 -" in i.text.replace("\xa0", " ")
            or "제공량 -" in i.text.replace("\xa0", " ")
        ]
        if nutri == [] and "\xa0" not in "".join(
            [
                str(i)
                for i in soup.find_all(
                    "div", {"class": "productDescription_contentProperties"}
                )
            ]
        ):
            nutri = None
        elif nutri == [] and "\xa0" in "".join(
            [
                i.text
                for i in soup.find_all(
                    "div", {"class": "productDescription_contentProperties"}
                )
            ]
        ):
            nutri = "NoServ"
        else:
            nutri = nutri[0]

        # 1회 제공량
        if nutri is None or nutri == "NoServ":
            serv_size = None
        else:
            serv_size = (
                [
                    n.text
                    for n in nutri.find_all("p")
                    if "Serving Size" in n.text.replace("\xa0", " ")
                    or "1회 복용량 -" in n.text.replace("\xa0", " ")
                    or "1회 제공량 -" in n.text.replace("\xa0", " ")
                    or "1회 섭취량 -" in n.text.replace("\xa0", " ")
                    or "서빙 사이즈 -" in n.text.replace("\xa0", " ")
                    or "제공량 -" in n.text.replace("\xa0", " ")
                ][0]
                .split("-")[1]
                .strip()
            )

        # 총 제공량
        try:
            if nutri is None:
                serv_per_cont = None
            else:
                serv_per_cont = (
                    [
                        n.text
                        for n in nutri.find_all("p")
                        if "Servings Per Container" in n.text or "용기당 제공 횟수" in n.text
                    ][0]
                    .split("-")[1]
                    .strip()
                )
        except Exception as e:
            print(e, "총 제공량")
            serv_per_cont = None

        (
            cal,
            fcal,
            sod,
            tcarb,
            dfib,
            tsug,
            asug,
            tofat,
            ufat,
            sfat,
            tfat,
            chol,
            prot,
            vita,
            vitd,
            vite,
            vitk,
            vitc,
            thim,
            ribo,
            niac,
            pyrd,
            folt,
            coba,
            pant,
            biot,
            iodi,
            copp,
            fluo,
            calc,
            magn,
            pota,
            chro,
            iron,
            zinc,
            moly,
            phos,
            sele,
            mang,
            chlo,
            hist,
            isol,
            leuc,
            lysi,
            meth,
            phen,
            thre,
            tryp,
            vali,
            seri,
            alan,
            argi,
            aspa,
            cyst,
            glut,
            glyc,
            prol,
            tyro,
            grnt,
            conj,
            garc,
            chit,
            psyl,
            gluc,
            aloe,
            crea,
            citr,
            agma,
            beta,
            xant,
            taur,
            caff,
            carn,
            vita_per,
            vitd_per,
            vite_per,
            vitk_per,
            vitc_per,
            thim_per,
            ribo_per,
            niac_per,
            pyrd_per,
            folt_per,
            coba_per,
            pant_per,
            biot_per,
            iodi_per,
            copp_per,
            fluo_per,
            calc_per,
            magn_per,
            pota_per,
            chro_per,
            iron_per,
            zinc_per,
            moly_per,
            phos_per,
            sele_per,
            mang_per,
            chlo_per,
            detail_images,
        ) = [[] for _ in range(101)]
        # 09/12 기타 영양소 확인용
        etc = []
        # 영양소 체크 여부
        nonSelected = True

        # 영양성분
        if nutri is not None:
            try:
                # basic_nut = soup.find_all('div', {'nutritional-info-container'})[0]
                # active_nut = soup.find_all('div', {'nutritional-info-container'})[1]
                nutinfo = soup.find_all("div", {"nutritional-info-container"})
            except Exception as e:
                print(e)
                basic_nut = [
                    i
                    for i in soup.find_all(
                        "div", {"class": "productDescription_synopsisContent"}
                    )
                    if "Nutritional Information" in i.text or "영양 정보" in i.text
                ][0]
                nutinfo = [basic_nut]

            # 영양소
            col_flag = 0
            for nut in nutinfo:
                for enum, s in enumerate(nut.find_all("tr")):
                    nonSelected = True

                    colnames = s.text.strip().split("\n")
                    if (
                        colnames == [""]
                        or colnames == ["영양물 정보"]
                        or colnames == ["영양 정보"]
                        or colnames == ["영양가"]
                    ):
                        continue
                    else:
                        #                     print('======================')
                        if col_flag == 0:
                            colnames = s.text.strip().split("\n")
                            #                         print(f"\n컬럼 : {colnames}")
                            #############################################
                            sum_num = 1
                            try:
                                #                             print(f'colnames : {colnames}')
                                key_index1 = [
                                    cnum
                                    for cnum, c in enumerate(colnames)
                                    if c == "Per Serving"
                                    or "Serving" in c
                                    or "Portion" in c
                                    or "Capsule" in c
                                    or "1회 제공량" in c
                                    or "1회제공량" in c
                                    or "1회 섭취량" in c
                                    or "서빙" in c
                                    or "1회 당" in c
                                    or "제공량" in c
                                    or "섭취 기준량" in c
                                    or "매 섭취량" in c
                                    or "1개" in c
                                    or "태블릿" in c
                                    or "캡슐" in c
                                ][0] + sum_num
                            except Exception as e:
                                print(e)
                                key_index1 = [
                                    cnum
                                    for cnum, c in enumerate(colnames)
                                    if c == "Per 100g"
                                    or c == "100g 당"
                                    or "100g" in c
                                    or "g 당" in c
                                ][0] + sum_num
                            try:
                                key_index2 = [
                                    cnum
                                    for cnum, c in enumerate(colnames)
                                    if c == "*RI" or c == "NRV" or "*권장" in c
                                ][0] + sum_num
                            except Exception as e:
                                print(e)
                                key_index2 = key_index1

                            #                         print(f"key_index1 : {key_index1}")
                            #############################################
                            col_flag += 1
                        else:
                            ingr_infos = s.text.strip().split("\n")
                    #                         print(f'영양소 : {ingr_infos}')

                    # data = [d for d in s.text.strip().split('\n') if d != '\xa0']

                    # 칼로리
                    if (
                        "Energy" in s.text
                        or "Calories" in s.text
                        or "열량" in s.text
                        or "에너지" in s.text
                    ):
                        cal_value = (
                            s.find_all("td")[key_index1].text.split("/")[-1].strip()
                        )
                        cal.append(cal_value.replace("\xa0", ""))
                        nonSelected = False
                    # 지방 칼로리
                    if "Fat Calories" in s.text or "Calories from Fat" in s.text:
                        fcal.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    # 나트륨
                    if (
                        "Salt" in s.text
                        or "Sodium" in s.text
                        or "염분" in s.text
                        or "소금" in s.text
                    ):
                        sod.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    # 총 탄수화물
                    if (
                        "Carbohydrates" in s.text
                        or "Total Carbohydrate" in s.text
                        or "탄수화물" in s.text
                    ):
                        tcarb.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    # 식이섬유
                    if (
                        "Fibre" in s.text
                        or "Dietary Fiber" in s.text
                        or "식이섬유" in s.text
                    ):
                        dfib.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    # 설탕
                    if (
                        "sugar" in s.text
                        or "Total Sugar" in s.text
                        or "당류" in s.text
                        or "당분" in s.text
                        or "설탕" in s.text
                    ):
                        tsug.append(s.find_all("td")[key_index1 + 1].text.strip())
                        nonSelected = False
                    # 첨가당
                    if "Added Sugar" in s.text or "첨가당" in s.text:
                        asug.append(s.find_all("td")[key_index1 + 1].text.strip())
                        nonSelected = False
                    # 지방
                    if "Fat" in s.text or "Total Fat" in s.text or "지방" in s.text:
                        tofat.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    # 불포화지방
                    if (
                        ("지방" in nut.find_all("tr")[enum - 1].text)
                        and ("불포화" in s.text or "불포화 지방" in s.text)
                    ) or (
                        ("Fat" in nut.find_all("tr")[enum - 1].text)
                        and ("unsaturates" in s.text or "Unsaturates" in s.text)
                    ):
                        ufat.append(s.find_all("td")[key_index1 + 1].text.strip())
                        nonSelected = False
                    # 포화지방
                    if (
                        ("지방" in nut.find_all("tr")[enum - 1].text)
                        and ("포화" in s.text or "포화 지방" in s.text)
                    ) or (
                        ("Fat" in nut.find_all("tr")[enum - 1].text)
                        and ("saturates" in s.text or "Saturates" in s.text)
                    ):
                        sfat.append(s.find_all("td")[key_index1 + 1].text.strip())
                        nonSelected = False
                    # 트랜스지방
                    if ("Fat" in nut.find_all("tr")[enum - 1].text) and (
                        "trans" in s.text or "Trans Fat" in s.text
                    ):
                        tfat.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    # 콜레스테롤
                    if "Cholesterol" in s.text or "콜레스테롤" in s.text:
                        chol.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    # 단백질
                    if (
                        "Protein" in s.text
                        and "Calories per gram" not in s.text
                        or "단백질" in s.text
                    ):
                        prot.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False

                    ############################################################################################
                    ### % 포함 ###
                    if "Vitamin A" in s.text or "비타민 A" in s.text:
                        try:
                            vita.append(s.find_all("td")[key_index1].text.strip())
                            vita_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Vitamin D" in s.text or "비타민 D" in s.text:
                        try:
                            vitd.append(s.find_all("td")[key_index1].text.strip())
                            vitd_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Vitamin E" in s.text or "비타민 E" in s.text:
                        try:
                            vite.append(s.find_all("td")[key_index1].text.strip())
                            vite_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Vitamin K" in s.text or "비타민 K" in s.text:
                        try:
                            vitk.append(s.find_all("td")[key_index1].text.strip())
                            vitk_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Vitamin C" in s.text or "비타민 C" in s.text:
                        try:
                            vitc.append(s.find_all("td")[key_index1].text.strip())
                            vitc_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if (
                        "Thiamin" in s.text
                        or "Vitamin B1" in s.text
                        or "티아민" in s.text
                        or "비타민 B1" in s.text
                    ):
                        try:
                            thim.append(s.find_all("td")[key_index1].text.strip())
                            thim_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if (
                        "Riboflavin" in s.text
                        or "Vitamin B2" in s.text
                        or "리보플라빈" in s.text
                        or "비타민 B2" in s.text
                    ):
                        try:
                            ribo.append(s.find_all("td")[key_index1].text.strip())
                            ribo_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if (
                        "Niacin" in s.text
                        or "Vitamin B3" in s.text
                        or "니아신" in s.text
                        or "비타민 B3" in s.text
                    ):
                        try:
                            niac.append(s.find_all("td")[key_index1].text.strip())
                            niac_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if (
                        "Pyridoxine" in s.text
                        or "Vitamin B6" in s.text
                        or "프리독신" in s.text
                        or "비타민 B6" in s.text
                    ):
                        try:
                            pyrd.append(s.find_all("td")[key_index1].text.strip())
                            pyrd_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if (
                        "Folate" in s.text
                        or "Folic Acid" in s.text
                        or "Vitamin B9" in s.text
                        or "엽산" in s.text
                        or "폴레이트" in s.text
                        or "비타민 B9" in s.text
                    ):
                        try:
                            folt.append(s.find_all("td")[key_index1].text.strip())
                            folt_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if (
                        "Cobalamin" in s.text
                        or "Cyanocobalamin" in s.text
                        or "Vitamin B12" in s.text
                        or "코발라민" in s.text
                        or "비타민 B12" in s.text
                    ):
                        try:
                            coba.append(s.find_all("td")[key_index1].text.strip())
                            coba_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if (
                        "Pantothenic Acid" in s.text
                        or "Vitamin B5" in s.text
                        or "판토텐산" in s.text
                        or "비타민 B5" in s.text
                    ):
                        try:
                            pant.append(s.find_all("td")[key_index1].text.strip())
                            pant_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if (
                        "Biotin" in s.text
                        or "Vitamin B7" in s.text
                        or "비오틴" in s.text
                        or "비타민 B7" in s.text
                    ):
                        try:
                            biot.append(s.find_all("td")[key_index1].text.strip())
                            biot_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Iodine" in s.text or "아이오딘" in s.text or "요오드" in s.text:
                        try:
                            iodi.append(s.find_all("td")[key_index1].text.strip())
                            iodi_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Copper" in s.text or "구리" in s.text:
                        try:
                            copp.append(s.find_all("td")[key_index1].text.strip())
                            copp_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Fluoride" in s.text or "불소" in s.text:
                        try:
                            fluo.append(s.find_all("td")[key_index1].text.strip())
                            fluo_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Calcium" in s.text or "칼슘" in s.text:
                        try:
                            calc.append(s.find_all("td")[key_index1].text.strip())
                            calc_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Magnesium" in s.text or "마그네슘" in s.text:
                        try:
                            magn.append(s.find_all("td")[key_index1].text.strip())
                            magn_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Potassium" in s.text or "칼륨" in s.text or "포타슘" in s.text:
                        try:
                            pota.append(s.find_all("td")[key_index1].text.strip())
                            pota_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Chromium" in s.text or "크롬" in s.text:
                        try:
                            chro.append(s.find_all("td")[key_index1].text.strip())
                            chro_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Iron" in s.text or "철분" in s.text:
                        try:
                            iron.append(s.find_all("td")[key_index1].text.strip())
                            iron_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Zinc" in s.text or "아연" in s.text:
                        try:
                            zinc.append(s.find_all("td")[key_index1].text.strip())
                            zinc_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Molybdenum" in s.text or "몰리브덴" in s.text:
                        try:
                            moly.append(s.find_all("td")[key_index1].text.strip())
                            moly_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Phosphorus" in s.text or "인" in s.text:
                        try:
                            phos.append(s.find_all("td")[key_index1].text.strip())
                            phos_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Selenium" in s.text or "셀레늄" in s.text or "셀레니움" in s.text:
                        try:
                            sele.append(s.find_all("td")[key_index1].text.strip())
                            sele_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Manganese" in s.text or "망간" in s.text:
                        try:
                            mang.append(s.find_all("td")[key_index1].text.strip())
                            mang_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    if "Chloride" in s.text or "염소" in s.text:
                        try:
                            chlo.append(s.find_all("td")[key_index1].text.strip())
                            chlo_per.append(s.find_all("td")[key_index2].text.strip())
                        except IndexError:
                            pass
                        nonSelected = False
                    ###################################################
                    if "Histidine" in s.text or "히스티딘" in s.text:
                        hist.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Isoleucine" in s.text or "이소류신" in s.text:
                        isol.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Leucine" in s.text or "류신" in s.text:
                        leuc.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Lysine" in s.text or "리신" in s.text:
                        lysi.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Methionine" in s.text or "메타오닌" in s.text:
                        meth.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "PhenylAlanine" in s.text or "페닐알라닌" in s.text:
                        phen.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Threonine" in s.text or "트레오닌" in s.text:
                        thre.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Tryptophane" in s.text or "트립토판" in s.text:
                        tryp.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Valine" in s.text or "발린" in s.text:
                        vali.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Serine" in s.text or "세린" in s.text:
                        seri.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Alanine" in s.text or "알라닌" in s.text:
                        alan.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Arginine" in s.text or "아르기닌" in s.text:
                        argi.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Asparagine" in s.text or "아스파라긴" in s.text:
                        aspa.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Cysteine" in s.text or "시스테인" in s.text:
                        cyst.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Glutamine" in s.text or "글루타민" in s.text:
                        glut.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Glycine" in s.text or "글리신" in s.text:
                        glyc.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Proline" in s.text or "프롤린" in s.text:
                        prol.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Tyrosine" in s.text or "티로신" in s.text:
                        tyro.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Green Tea" in s.text or "녹차추출물" in s.text or "녹차" in s.text:
                        grnt.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Conjugated Linoleic" in s.text or "공액리놀레산" in s.text:
                        conj.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Garcinia Cambogia" in s.text or "가르시니아" in s.text:
                        garc.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Chitosan" in s.text or "키토산" in s.text:
                        chit.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Psyllium" in s.text or "차전자피" in s.text:
                        psyl.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Glucomannan" in s.text or "글루코만난" in s.text:
                        gluc.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Aloe" in s.text or "알로에" in s.text:
                        aloe.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Creatine" in s.text or "크레아틴" in s.text:
                        crea.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Citrulline" in s.text or "시트룰린" in s.text:
                        citr.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Agmatine" in s.text or "아그마틴" in s.text:
                        agma.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if (
                        "Beta Alanine" in s.text
                        or "베타알라닌" in s.text
                        or "베타 알라닌" in s.text
                    ):
                        beta.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Xanthigen" in s.text or "잔티젠" in s.text:
                        xant.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Taurine" in s.text or "타우린" in s.text:
                        taur.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Caffeine" in s.text or "카페인" in s.text:
                        caff.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    if "Carnitine" in s.text or "카르니틴" in s.text:
                        carn.append(s.find_all("td")[key_index1].text.strip())
                        nonSelected = False
                    ############################################################################################

                    #                 print(f'선택되어지지 않았는가? => {nonSelected}')
                    if nonSelected:
                        etcmap2 = []
                        for e in [e.text.strip() for e in s.find_all("td")]:
                            if (
                                e != ""
                                and "Per 100g" not in e
                                and "Per Serving" not in e
                                and "100g 당" not in e
                                and "1회 섭취량 당" not in e
                                and "100g당" not in e
                                and "1회 제공량" not in e
                            ):
                                etcmap2.append(e)
                        etc.append("/".join(etcmap2))

        cal = cal[0] if cal != [] else None
        fcal = fcal[0] if fcal != [] else None
        sod = sod[0] if sod != [] else None
        tcarb = tcarb[0] if tcarb != [] else None
        dfib = dfib[0] if dfib != [] else None
        tsug = tsug[0] if tsug != [] else None
        asug = asug[0] if asug != [] else None
        tofat = tofat[0] if tofat != [] else None
        ufat = ufat[0] if ufat != [] else None
        sfat = sfat[0] if sfat != [] else None
        tfat = tfat[0] if tfat != [] else None
        chol = chol[0] if chol != [] else None
        prot = prot[0] if prot != [] else None
        vita = vita[0] if vita != [] else None
        vitd = vitd[0] if vitd != [] else None
        vite = vite[0] if vite != [] else None
        vitk = vitk[0] if vitk != [] else None
        vitc = vitc[0] if vitc != [] else None
        thim = thim[0] if thim != [] else None
        ribo = ribo[0] if ribo != [] else None
        niac = niac[0] if niac != [] else None
        pyrd = pyrd[0] if pyrd != [] else None
        folt = folt[0] if folt != [] else None
        coba = coba[0] if coba != [] else None
        pant = pant[0] if pant != [] else None
        biot = biot[0] if biot != [] else None
        iodi = iodi[0] if iodi != [] else None
        copp = copp[0] if copp != [] else None
        fluo = fluo[0] if fluo != [] else None
        calc = calc[0] if calc != [] else None
        magn = magn[0] if magn != [] else None
        pota = pota[0] if pota != [] else None
        chro = chro[0] if chro != [] else None
        iron = iron[0] if iron != [] else None
        zinc = zinc[0] if zinc != [] else None
        moly = moly[0] if moly != [] else None
        phos = phos[0] if phos != [] else None
        sele = sele[0] if sele != [] else None
        mang = mang[0] if mang != [] else None
        chlo = chlo[0] if chlo != [] else None
        hist = hist[0] if hist != [] else None
        isol = isol[0] if isol != [] else None
        leuc = leuc[0] if leuc != [] else None
        lysi = lysi[0] if lysi != [] else None
        meth = meth[0] if meth != [] else None
        phen = phen[0] if phen != [] else None
        thre = thre[0] if thre != [] else None
        tryp = tryp[0] if tryp != [] else None
        vali = vali[0] if vali != [] else None
        seri = seri[0] if seri != [] else None
        alan = alan[0] if alan != [] else None
        argi = argi[0] if argi != [] else None
        aspa = aspa[0] if aspa != [] else None
        cyst = cyst[0] if cyst != [] else None
        glut = glut[0] if glut != [] else None
        glyc = glyc[0] if glyc != [] else None
        prol = prol[0] if prol != [] else None
        tyro = tyro[0] if tyro != [] else None
        grnt = grnt[0] if grnt != [] else None
        conj = conj[0] if conj != [] else None
        garc = garc[0] if garc != [] else None
        chit = chit[0] if chit != [] else None
        psyl = psyl[0] if psyl != [] else None
        gluc = gluc[0] if gluc != [] else None
        aloe = aloe[0] if aloe != [] else None
        crea = crea[0] if crea != [] else None
        citr = citr[0] if citr != [] else None
        agma = agma[0] if agma != [] else None
        beta = beta[0] if beta != [] else None
        xant = xant[0] if xant != [] else None
        taur = taur[0] if taur != [] else None
        caff = caff[0] if caff != [] else None
        carn = carn[0] if carn != [] else None

        vita_per = vita_per[0] if vita_per != [] else None
        vitd_per = vitd_per[0] if vitd_per != [] else None
        vite_per = vite_per[0] if vite_per != [] else None
        vitk_per = vitk_per[0] if vitk_per != [] else None
        vitc_per = vitc_per[0] if vitc_per != [] else None
        thim_per = thim_per[0] if thim_per != [] else None
        ribo_per = ribo_per[0] if ribo_per != [] else None
        niac_per = niac_per[0] if niac_per != [] else None
        pyrd_per = pyrd_per[0] if pyrd_per != [] else None
        folt_per = folt_per[0] if folt_per != [] else None
        coba_per = coba_per[0] if coba_per != [] else None
        pant_per = pant_per[0] if pant_per != [] else None
        biot_per = biot_per[0] if biot_per != [] else None
        iodi_per = iodi_per[0] if iodi_per != [] else None
        copp_per = copp_per[0] if copp_per != [] else None
        fluo_per = fluo_per[0] if fluo_per != [] else None
        calc_per = calc_per[0] if calc_per != [] else None
        magn_per = magn_per[0] if magn_per != [] else None
        pota_per = pota_per[0] if pota_per != [] else None
        chro_per = chro_per[0] if chro_per != [] else None
        iron_per = iron_per[0] if iron_per != [] else None
        zinc_per = zinc_per[0] if zinc_per != [] else None
        moly_per = moly_per[0] if moly_per != [] else None
        phos_per = phos_per[0] if phos_per != [] else None
        sele_per = sele_per[0] if sele_per != [] else None
        mang_per = mang_per[0] if mang_per != [] else None
        chlo_per = chlo_per[0] if chlo_per != [] else None

        avoid_words = [
            "Per Serving",
            "Serving",
            "Portion",
            "Capsule",
            "1회 제공량",
            "1회",
            "제공",
            "1회제공량",
            "1회 섭취량",
            "서빙",
            "1회 당",
            "제공량",
            "섭취 기준량",
            "Per",
            "Active",
            "Ingredients",
            "매 섭취량",
            "1개",
            "태블릿",
            "캡슐",
            "NRV",
            "Per 100g",
            "100g 당",
            "g 당",
            "권장" "*RI",
            "*권장",
        ]
        etc = list(dict.fromkeys(etc))
        etc = [e for e in etc if not any([aw for aw in avoid_words if aw in e])]
        etc = "|".join(etc) if etc != [] else None
        # print(f"기타성분 : {etc}")

        return (
            image,
            brand,
            name,
            flavor,
            volume,
            mingrd,
            aingrd,
            url,
            pcode,
            price,
            stock,
            serv_size,
            serv_per_cont,
            cal,
            fcal,
            sod,
            tcarb,
            dfib,
            tsug,
            asug,
            tofat,
            ufat,
            sfat,
            tfat,
            chol,
            prot,
            vita,
            vitd,
            vite,
            vitk,
            vitc,
            thim,
            ribo,
            niac,
            pyrd,
            folt,
            coba,
            pant,
            biot,
            iodi,
            copp,
            fluo,
            calc,
            magn,
            pota,
            chro,
            iron,
            zinc,
            moly,
            phos,
            sele,
            mang,
            chlo,
            hist,
            isol,
            leuc,
            lysi,
            meth,
            phen,
            thre,
            tryp,
            vali,
            seri,
            alan,
            argi,
            aspa,
            cyst,
            glut,
            glyc,
            prol,
            tyro,
            grnt,
            conj,
            garc,
            chit,
            psyl,
            gluc,
            aloe,
            crea,
            citr,
            agma,
            beta,
            xant,
            taur,
            caff,
            carn,
            vita_per,
            vitd_per,
            vite_per,
            vitk_per,
            vitc_per,
            thim_per,
            ribo_per,
            niac_per,
            pyrd_per,
            folt_per,
            coba_per,
            pant_per,
            biot_per,
            iodi_per,
            copp_per,
            fluo_per,
            calc_per,
            magn_per,
            pota_per,
            chro_per,
            iron_per,
            zinc_per,
            moly_per,
            phos_per,
            sele_per,
            mang_per,
            chlo_per,
            etc,
            detail_images,
            temp,
            ingr_words,
        )
    except:
        return (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
