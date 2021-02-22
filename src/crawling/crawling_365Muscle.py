import requests
from bs4 import BeautifulSoup
from urllib.request import urljoin, build_opener, install_opener, urlretrieve
import re
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


def crawling_365Muscle(site_name, href, num, f_num):
    temp = dict()
    res = req.get(href, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")

    if "요청하신 페이지를 찾을수 없습니다." in res.text:
        raise KeyboardInterrupt

    # 사진
    image = soup.find("div", {"id": "goods_thumbs"}).find("img").get("src")
    image = urljoin(res.url, image)
    save_image(site_name, image, num, "product")
    # print(f'제품사진 : {image}')

    # 브랜드
    brand = [
        b.find("dd").text.strip()
        for b in soup.find("div", "goods_spec_table").find_all("dl")
        if b.find("dt").text.strip() == "브랜드"
    ]
    brand = brand[0] if brand != [] else None
    # print(f'브랜드 : {brand}')

    # 제품명
    name = soup.find("li", "goods_name")
    try:
        name.find("span", "hide").decompose()
    except Exception as e:
        print(e)
    name = name.text.strip()
    # print(f'제품명 : {name}')

    # 맛
    if soup.find("table", "goods_option_table").find("select") is not None:
        flavor = [
            x
            for x in soup.find("table", "goods_option_table")
            .find("select")
            .find_all("option")
            if x.get("value") != ""
        ][f_num].get("value")

    else:
        flavor = None
    # print(f'맛 : {flavor}')

    # 용량
    volume = None
    volume_lambda = lambda x: [
        name.split(" ")[n - 1 : n + 1] if re.findall("\d", v) == [] else v
        for n, v in enumerate(name.split(" "))
        if "".join(re.findall("[a-zA-Z]+$", v)) == x
    ]
    if "SERVS" in name:
        volume = volume_lambda("SERVS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "PACKETS" in name:
        volume = volume_lambda("PACKETS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "BARS" in name:
        volume = volume_lambda("BARS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "SRVS" in name:
        volume = volume_lambda("SRVS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "SEVS" in name:
        volume = volume_lambda("SEVS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "VCAPS" in name:
        volume = volume_lambda("VCAPS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "CAPS" in name:
        volume = volume_lambda("CAPS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "TABS" in name:
        volume = volume_lambda("TABS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "LBS" in name:
        volume = volume_lambda("LBS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "SGELS" in name:
        volume = volume_lambda("SGELS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "LGELS" in name:
        volume = volume_lambda("LGELS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "GELS" in name:
        volume = volume_lambda("GELS")
        volume = "".join(volume[0]) if volume != [] else None
    elif "CT" in name:
        volume = volume_lambda("CT")
        volume = "".join(volume[0]) if volume != [] else None
    elif "OZ" in name:
        volume = volume_lambda("OZ")
        volume = "".join(volume[0]) if volume != [] else None
    elif "kg" in name:
        volume = volume_lambda("kg")
        volume = "".join(volume[0]) if volume != [] else None
    elif "PACK" in name:
        volume = volume_lambda("PACK")
        volume = "".join(volume[0]) if volume != [] else None
    elif "EA" in name:
        volume = volume_lambda("EA")
        volume = "".join(volume[0]) if volume != [] else None
    elif "G" in name:
        volume = volume_lambda("G")
        volume = "".join(volume[0]) if volume != [] else None
    # print(f"용량 : {volume}")

    # URL
    url = res.url
    # print(f'제품 URL : {url}')

    # 제품번호
    pcode = res.url.split("no=")[1]
    pcode = pcode.split("#")[0] if "#" in pcode else pcode
    # print(f'제품번호 : {pcode}')

    # 가격
    price = [
        p.text.strip().replace("(", "").replace(")", "")
        for p in soup.find("div", "price_wrap")
        if "원" in str(p)
    ]
    price = price[0] if price != [] else None
    # print(f'가격 : {price}')

    # 품절여부
    stock = None
    # print(f'품절여부 : {stock}')

    # 상세페이지 이미지부분
    i_url = f"https://365muscle.com/goods/view_contents?no={pcode}&setMode=pc&zoom=1"
    res = req.get(i_url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    detail_images = soup.find_all("img")
    detail_images = "|".join([urljoin(res.url, i.get("src")) for i in detail_images])
    save_image(site_name, detail_images, num, "detail")
    # print(f"상세이미지 : {detail_images}")

    # 1회 제공량 / 총 제공량
    if soup.find("p", "nutritionFacts__servingSize") is not None:
        serv_size = (
            soup.find("p", "nutritionFacts__servingSize")
            .find("span", {"style": True})
            .text.strip()
        )
        serv_cont = (
            soup.find("p", "nutritionFacts__servingsPerContainer")
            .find("span", {"style": True})
            .text.strip()
        )
    else:
        serv_size, serv_cont = None, None
    # print(f'1회 제공량 : {serv_size}')
    # print(f'총 제공량 : {serv_cont}')

    # 영양성분표

    try:
        nutri = pd.DataFrame()
        nutri[0] = [
            i.get_text("|").split("|")[0]
            for i in soup.find("div", "nutritionFacts__borders").find_all(
                "div", {"class": True}
            )
            if "nutritionFacts__nutrient" in "".join(i.get("class"))
        ]
        nutri[1] = [
            i.find("span", "nutritionFacts__nutrientAmount").text.strip()
            for i in soup.find("div", "nutritionFacts__borders").find_all(
                "div", {"class": True}
            )
            if "nutritionFacts__nutrient" in "".join(i.get("class"))
        ]
        nutri[2] = [
            i.find("span", "nutritionFacts__dailyValue").text.strip()
            for i in soup.find("div", "nutritionFacts__borders").find_all(
                "div", {"class": True}
            )
            if "nutritionFacts__nutrient" in "".join(i.get("class"))
        ]
    except Exception as e:
        print("영양 성분표가 없습니다.", e)
        nutri = None
        # print(f"영양성분표 : {nutri}")

    # 원료성분
    mingrd = None
    ingr_words = None
    if soup.find("span", "nutritionFacts__ingredientsList") is not None:
        mingrd = soup.find("span", "nutritionFacts__ingredientsList").text.strip()
        mingrd = remove_part(mingrd)
        ingr_words = substract_ingredient(mingrd, ingr_list)
        # print(f"원료성분 : {mingrd}")
        temp["url"] = href
        temp["원료성분"] = ingr_words
    # 알러지성분
    aingrd = None
    # print(f"알러지 성분 : {aingrd}")
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
        etc,
    ) = [[] for _ in range(101)]
    # 영양소 체크 여부
    nonSelected = True

    # 영양성분
    try:
        test = True if nutri is None else False
        if test:
            print("영양성분표 없음")
    except ValueError:
        nutn = list(nutri[list(nutri.columns)[0]])
        nutp = list(nutri[list(nutri.columns)[1]])
        nutd = list(nutri[list(nutri.columns)[2]])
        for nnum, nut in enumerate(nutn):
            if (
                "amount" in nut.lower()
                or "lbs" in nut.lower()
                or "supplement" in nut.lower()
                or "," in nut.lower()
            ):
                continue
            # 칼로리
            if ("calories" in nut.lower() and "fat" not in nut.lower()) and (
                "amount" not in nut.lower() and "lbs" not in nut.lower()
            ):
                cal.append(nutp[nnum])
                nonSelected = False
            # 지방 칼로리
            if (
                "fat calories" in nut.lower()
                or ("calories" in nut.lower() and "fat" in nut.lower())
            ) and ("amount" not in nut.lower() and "lbs" not in nut.lower()):
                fcal.append(nutp[nnum])
                nonSelected = False
            # 나트륨
            if ("salt" in nut.lower() or "sodium" in nut.lower()) and (
                "amount" not in nut.lower() and "lbs" not in nut.lower()
            ):
                sod.append(nutp[nnum])
                nonSelected = False
            # 총 탄수화물
            if (
                "carbohydrates" in nut.lower() or "total carbohydrate" in nut.lower()
            ) and ("amount" not in nut.lower() and "lbs" not in nut.lower()):
                tcarb.append(nutp[nnum])
                nonSelected = False
            # 식이섬유
            if ("fibre" in nut.lower() or "dietary fiber" in nut.lower()) and (
                "amount" not in nut.lower() and "lbs" not in nut.lower()
            ):
                dfib.append(nutp[nnum])
                nonSelected = False
            # 설탕
            if ("sugar" in nut.lower() and "added" not in nut.lower()) and (
                "amount" not in nut.lower() and "lbs" not in nut.lower()
            ):
                tsug.append(nutp[nnum])
                nonSelected = False
            # 첨가당
            if "added sugar" in nut.lower() and (
                "amount" not in nut.lower() and "lbs" not in nut.lower()
            ):
                asug.append("".join(re.findall(r"\d", nut)))
                nonSelected = False
            # 지방
            if (
                ("fat" in nut.lower() and "total fat" in nut.lower())
                and ("saturate" not in nut.lower() or "trans" not in nut.lower())
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                tofat.append(nutp[nnum])
                nonSelected = False
            # 불포화지방
            if (
                "unsaturate" in nut.lower()
                and "fat" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                ufat.append(nutp[nnum])
                nonSelected = False
            # 포화지방
            if (
                "saturate" in nut.lower()
                and "fat" in nut.lower()
                and "unsaturate" not in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                sfat.append(nutp[nnum])
                nonSelected = False
            # 트랜스지방
            if (
                "fat" in nut.lower()
                and "trans" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                tfat.append(nutp[nnum])
                nonSelected = False
            # 콜레스테롤
            if "cholesterol" in nut.lower() and (
                "amount" not in nut.lower() and "lbs" not in nut.lower()
            ):
                chol.append(nutp[nnum])
                nonSelected = False
            # 단백질
            if "protein" in nut.lower() and (
                "amount" not in nut.lower() and "lbs" not in nut.lower()
            ):
                prot.append(nutp[nnum])
                nonSelected = False

            ############################################################################################
            ### % 포함 ###
            if "vitamin a" in nut.lower() and (
                "amount" not in nut.lower() and "lbs" not in nut.lower()
            ):
                vita.append(nutp[nnum])
                vita_per.append(nutd[nnum])
                nonSelected = False
            if "vitamin d" in nut.lower() and (
                "amount" not in nut.lower() and "lbs" not in nut.lower()
            ):
                try:
                    vitd.append(nutp[nnum])
                    vitd_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "vitamin e" in nut.lower()
                or "비타민 E" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    vite.append(nutp[nnum])
                    vite_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "vitamin k" in nut.lower()
                or "비타민 K" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    vitk.append(nutp[nnum])
                    vitk_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "vitamin c" in nut.lower()
                or "비타민 C" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    vitc.append(nutp[nnum])
                    vitc_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "thiamin" in nut.lower()
                or "vitamin b1" in nut.lower()
                or "티아민" in nut.lower()
                or "비타민 B1" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    thim.append(nutp[nnum])
                    thim_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "riboflavin" in nut.lower()
                or "vitamin b2" in nut.lower()
                or "리보플라빈" in nut.lower()
                or "비타민 B2" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    ribo.append(nutp[nnum])
                    ribo_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "niacin" in nut.lower()
                or "vitamin b3" in nut.lower()
                or "니아신" in nut.lower()
                or "비타민 B3" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    niac.append(nutp[nnum])
                    niac_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "pyridoxine" in nut.lower()
                or "vitamin b6" in nut.lower()
                or "프리독신" in nut.lower()
                or "비타민 B6" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    pyrd.append(nutp[nnum])
                    pyrd_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "folate" in nut.lower()
                or "folic acid" in nut.lower()
                or "vitamin b9" in nut.lower()
                or "엽산" in nut.lower()
                or "폴레이트" in nut.lower()
                or "비타민 B9" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    folt.append(nutp[nnum])
                    folt_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "cobalamin" in nut.lower()
                or "cyanocobalamin" in nut.lower()
                or "vitamin b12" in nut.lower()
                or "코발라민" in nut.lower()
                or "비타민 B12" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    coba.append(nutp[nnum])
                    coba_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "pantothenic acid" in nut.lower()
                or "vitamin b5" in nut.lower()
                or "판토텐산" in nut.lower()
                or "비타민 B5" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    pant.append(nutp[nnum])
                    pant_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "biotin" in nut.lower()
                or "vitamin b7" in nut.lower()
                or "비오틴" in nut.lower()
                or "비타민 B7" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    biot.append(nutp[nnum])
                    biot_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "iodine" in nut.lower()
                or "아이오딘" in nut.lower()
                or "요오드" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    iodi.append(nutp[nnum])
                    iodi_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "copper" in nut.lower()
                or "구리" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    copp.append(nutp[nnum])
                    copp_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "fluoride" in nut.lower()
                or "불소" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    fluo.append(nutp[nnum])
                    fluo_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if ("calcium" in nut.lower() or "칼슘" in nut.lower()) and (
                "amount" not in nut.lower() and "lbs" not in nut.lower()
            ):
                try:
                    calc.append(nutp[nnum])
                    calc_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "magnesium" in nut.lower()
                or "마그네슘" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    magn.append(nutp[nnum])
                    magn_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "potassium" in nut.lower()
                or "칼륨" in nut.lower()
                or "포타슘" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    pota.append(nutp[nnum])
                    pota_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "chromium" in nut.lower()
                or "크롬" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    chro.append(nutp[nnum])
                    chro_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "iron" in nut.lower()
                or "철분" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    iron.append(nutp[nnum])
                    iron_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "zinc" in nut.lower()
                or "아연" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    zinc.append(nutp[nnum])
                    zinc_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "molybdenum" in nut.lower()
                or "몰리브덴" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    moly.append(nutp[nnum])
                    moly_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "phosphorus" in nut.lower()
                or "인" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    phos.append(nutp[nnum])
                    phos_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "selenium" in nut.lower()
                or "셀레늄" in nut.lower()
                or "셀레니움" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    sele.append(nutp[nnum])
                    sele_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "manganese" in nut.lower()
                or "망간" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    mang.append(nutp[nnum])
                    mang_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if (
                "chloride" in nut.lower()
                or "염소" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                try:
                    chlo.append(nutp[nnum])
                    chlo_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            ###################################################
            if (
                "histidine" in nut.lower()
                or "히스티딘" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                hist.append(nutp[nnum])
                nonSelected = False
            if (
                "isoleucine" in nut.lower()
                or "이소류신" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                isol.append(nutp[nnum])
                nonSelected = False
            if (
                "leucine" in nut.lower()
                or "류신" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                leuc.append(nutp[nnum])
                nonSelected = False
            if (
                "lysine" in nut.lower()
                or "리신" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                lysi.append(nutp[nnum])
                nonSelected = False
            if (
                "methionine" in nut.lower()
                or "메타오닌" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                meth.append(nutp[nnum])
                nonSelected = False
            if (
                "phenylAlanine" in nut.lower()
                or "페닐알라닌" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                phen.append(nutp[nnum])
                nonSelected = False
            if (
                "threonine" in nut.lower()
                or "트레오닌" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                thre.append(nutp[nnum])
                nonSelected = False
            if (
                "tryptophane" in nut.lower()
                or "트립토판" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                tryp.append(nutp[nnum])
                nonSelected = False
            if (
                "valine" in nut.lower()
                or "발린" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                vali.append(nutp[nnum])
                nonSelected = False
            if (
                "serine" in nut.lower()
                or "세린" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                seri.append(nutp[nnum])
                nonSelected = False
            if (
                "alanine" in nut.lower()
                or "알라닌" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                alan.append(nutp[nnum])
                nonSelected = False
            if (
                "arginine" in nut.lower()
                or "아르기닌" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                argi.append(nutp[nnum])
                nonSelected = False
            if (
                "asparagine" in nut.lower()
                or "아스파라긴" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                aspa.append(nutp[nnum])
                nonSelected = False
            if (
                "cysteine" in nut.lower()
                or "시스테인" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                cyst.append(nutp[nnum])
                nonSelected = False
            if (
                "glutamine" in nut.lower()
                or "글루타민" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                glut.append(nutp[nnum])
                nonSelected = False
            if (
                "glycine" in nut.lower()
                or "글리신" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                glyc.append(nutp[nnum])
                nonSelected = False
            if (
                "proline" in nut.lower()
                or "프롤린" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                prol.append(nutp[nnum])
                nonSelected = False
            if (
                "tyrosine" in nut.lower()
                or "티로신" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                tyro.append(nutp[nnum])
                nonSelected = False
            if (
                "green tea" in nut.lower()
                or "녹차추출물" in nut.lower()
                or "녹차" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                grnt.append(nutp[nnum])
                nonSelected = False
            if (
                "conjugated linoleic" in nut.lower()
                or "공액리놀레산" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                conj.append(nutp[nnum])
                nonSelected = False
            if (
                "garcinia cambogia" in nut.lower()
                or "가르시니아" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                garc.append(nutp[nnum])
                nonSelected = False
            if (
                "chitosan" in nut.lower()
                or "키토산" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                chit.append(nutp[nnum])
                nonSelected = False
            if (
                "psyllium" in nut.lower()
                or "차전자피" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                psyl.append(nutp[nnum])
                nonSelected = False
            if (
                "glucomannan" in nut.lower()
                or "글루코만난" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                gluc.append(nutp[nnum])
                nonSelected = False
            if (
                "aloe" in nut.lower()
                or "알로에" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                aloe.append(nutp[nnum])
                nonSelected = False
            if (
                "creatine" in nut.lower()
                or "크레아틴" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                crea.append(nutp[nnum])
                nonSelected = False
            if (
                "citrulline" in nut.lower()
                or "시트룰린" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                citr.append(nutp[nnum])
                nonSelected = False
            if (
                "agmatine" in nut.lower()
                or "아그마틴" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                agma.append(nutp[nnum])
                nonSelected = False
            if (
                "beta alanine" in nut.lower()
                or "베타알라닌" in nut.lower()
                or "베타 알라닌" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                beta.append(nutp[nnum])
                nonSelected = False
            if (
                "xanthigen" in nut.lower()
                or "잔티젠" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                xant.append(nutp[nnum])
                nonSelected = False
            if (
                "taurine" in nut.lower()
                or "타우린" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                taur.append(nutp[nnum])
                nonSelected = False
            if (
                "caffeine" in nut.lower()
                or "카페인" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                caff.append(nutp[nnum])
                nonSelected = False
            if (
                "carnitine" in nut.lower()
                or "카르니틴" in nut.lower()
                and ("amount" not in nut.lower() and "lbs" not in nut.lower())
            ):
                carn.append(nutp[nnum])
                nonSelected = False
            ############################################################################################

            #                 # print(f'선택되어지지 않았는가? => {nonSelected}')
            if nonSelected:
                etc.append(f"{nut}/{nutp[nnum]}/{nutd[nnum]}")

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
        serv_cont,
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
