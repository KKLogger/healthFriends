import requests
from bs4 import BeautifulSoup
from urllib.request import urljoin, build_opener, install_opener, urlretrieve
import re
import time
from urllib.parse import quote
from save_image import save_image
import pandas as pd

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
}
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=20)
session.mount("https://", adapter)
session.mount("http://", adapter)
req = session


def crawling(site_name, href, num):
    if site_name == "365Muscle":
        return crawling_365Muscle(site_name, href, num)
    elif site_name == "IronMax":
        return crawling_IronMax(site_name, href, num)
    elif site_name == "iHerb":
        return crawling_iHerb(site_name, href, num)
    elif site_name == "Kingmass":
        return crawling_Kingmass(site_name, href, num)
    elif site_name == "MonsterMart":
        return crawling_MonsterMart(site_name, href, num)
    elif site_name == "MyProtein":
        return crawling_MyProtein(site_name, href, num)
    elif site_name == "Ople":
        return crawling_Ople(site_name, href, num)
    else:
        return crawling_Coupang(site_name, href, num)


def crawling_365Muscle(site_name, href, num):
    time.sleep(0.2)
    temp = dict()
    res = req.get(href, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")

    if "요청하신 페이지를 찾을수 없습니다." in res.text:
        raise KeyboardInterrupt

    # 사진
    image = soup.find("div", {"id": "goods_thumbs"}).find("img").get("src")
    image = urljoin(res.url, image)
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
            f.get("value")
            for f in soup.find("table", "goods_option_table")
            .find("select")
            .find_all("option")
            if f.get("value") != ""
        ]
        flavor = "/".join(flavor)
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
    time.sleep(0.2)
    res = req.get(i_url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    detail_images = soup.find_all("img")
    detail_images = "|".join([urljoin(res.url, i.get("src")) for i in detail_images])
    save_image(site_name, detail_images, num)
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
    if soup.find("span", "nutritionFacts__ingredientsList") is not None:
        mingrd = soup.find("span", "nutritionFacts__ingredientsList").text.strip()
        print(f"원료성분 : {mingrd}")
        temp["url"] = href
        temp["원료성분"] = mingrd
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
    )


def crawling_IronMax(site_name, href, num):
    res = req.get(href, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    temp = dict()
    if "요청하신 페이지를 찾을수 없습니다." in res.text:
        raise KeyboardInterrupt

    # 사진
    image = soup.find("a", {"id": "mainImage"}).find("img").get("src")
    image = urljoin(res.url, image)
    save_image(site_name, image, num)
    # print(f"제품사진 : {image}")

    # 브랜드
    brand = [
        b.find("dd").text.strip()
        for b in soup.find("div", "item_detail_list").find_all("dl")
        if b.find("dt").text.strip() == "브랜드"
    ]
    brand = brand[0] if brand != [] else None
    # print(f"브랜드 : {brand}")

    # 제품명
    name = soup.find("div", "item_info_box").find("div", "item_detail_tit")
    try:
        name.find("div").decompose()
    except Exception as e:
        print(e)
    name = name.text.strip()
    # print(f"제품명 : {name}")

    # 맛
    if (
        soup.find("div", "item_add_option_box") is not None
        and soup.find("div", "item_add_option_box").find("dt").text.strip() == "맛"
    ):
        flavor = "|".join(
            [
                o.text.strip()
                for o in soup.find("div", "item_add_option_box")
                .find("select")
                .find_all("option")
                if o.get("value") != ""
            ]
        )
    else:
        flavor = None
    # print(f"맛 : {flavor}")

    # 용량
    volume = [
        b.find("dd").text.strip()
        for b in soup.find("div", "item_detail_list").find_all("dl")
        if b.find("dt").text.strip() == "상품 무게"
    ]
    volume = volume[0] if volume != [] else None
    # print(f"용량 : {volume}")

    # URL
    url = res.url
    # print(f"제품 URL : {url}")

    # 제품번호
    pcode = [
        b.find("dd").text.strip()
        for b in soup.find("div", "item_detail_list").find_all("dl")
        if b.find("dt").text.strip() == "상품코드"
    ]
    pcode = pcode[0] if pcode != [] else None
    # print(f"제품번호 : {pcode}")

    # 가격
    price = soup.find("dl", "item_price").find("dd").text.strip()
    # print(f"가격 : {price}")

    # 품절여부
    if flavor is not None:
        if all([True if "[품절]" in f else False for f in flavor.split("|")]):
            stock = True
        else:
            stock = False
    else:
        stock = None
    # print(f"품절여부 : {stock}")

    # 상세페이지 이미지부분
    detail_images = [
        urljoin(res.url, i.get("src"))
        for i in soup.find("div", "detail_explain_box").find_all("img")
    ]
    detail_images = "|".join(detail_images)
    # print(f"상세이미지 : {detail_images}")

    # 1회 제공량 / 총 제공량
    serv_size, serv_cont = None, None
    # print(f"1회 제공량 : {serv_size}")
    # print(f"총 제공량 : {serv_cont}")

    # 영양성분표
    nutri = None
    # print(f"영양성분표 : {nutri}")

    # 원료성분
    mingrd = None
    temp["원료성분"] = None
    # print(f"원료성분 : {mingrd}")

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
    )


def crawling_iHerb(site_name, href, num):
    res = req.get(href, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    temp = dict()
    if res.status_code == 404:
        raise KeyboardInterrupt
    if "The page is not found!" in soup.find("head").find("title").text:
        raise KeyboardInterrupt

    try:
        image = soup.find("img", {"id": "iherb-product-image"}).get("src")
        save_image(site_name, image, num)
    except AttributeError as e:
        image = None
        print("no image tag error : ", e)
    detail_images = None
    # print(f'제품사진 : {image}')
    try:
        brand = (
            soup.find("div", {"itemprop": "brand"})
            .find("span", {"itemprop": "name"})
            .text.strip()
        )
    except Exception as e:
        print(e)
        brand = None
    # print(f'브랜드 : {brand}')
    name = soup.find("h1", {"id": "name"}).text.strip()
    # print(f'제품명 : {name}')

    try:
        flavor = (
            soup.select_one(
                "body > div.product-grouping-wrapper.defer-block > article > div.container-fluid > div.product-detail-container.ga-product.clearfix > section > div.product-grouping-row"
            )
            .get_text("|")
            .strip()
            .split("|")
        )
        flavor = [f.strip() for f in flavor if f != "" and f != "\n"]
        flavor = flavor[1] if "향" in flavor[0] else None
    except Exception as e:
        print(e)
        flavor = None
    # print(f'맛 : {flavor}')

    try:
        volume = filter(
            lambda y: True if "포장 수량" in y.text else False,
            soup.find("ul", {"id": "product-specs-list"}).find_all("li"),
        )
        volume = next(volume).text.split(":")[-1].strip()
    except StopIteration:
        volume = filter(
            lambda y: True if "부피 및 배송 중량" in y.text else False,
            soup.find("ul", {"id": "product-specs-list"}).find_all("li"),
        )
        volume = next(volume).text.split(",")[-1].strip()
    # print(f'양 : {volume}')

    # 영양성분 임시 통합
    try:
        mingrd = soup.find("div", {"class": "prodOverviewIngred"}).get_text("|||")
        temp["원료성분"] = mingrd
        temp["url"] = href
    except Exception as e:
        mingrd = None
        print(e)
    aingrd = None
    ################################################################

    url = href + "?rcode=AAR7724"
    # print(f'제품 URL : {url}')

    pcode = filter(
        lambda y: True if "상품 코드" in y.text else False,
        soup.find("ul", {"id": "product-specs-list"}).find_all("li"),
    )
    pcode = next(pcode).text.split(":")[-1].strip()
    # print(f'제품번호 : {pcode}')

    try:
        pricing = soup.find("section", {"id": "pricing"}).find_all("section")
        sprice = [p for p in pricing if p.get("class") is not None]
        price = (
            sprice[0].find("b", {"class": "s24"}).text.strip()
            if sprice != []
            else pricing[0].find("div", {"id": "price"}).text.strip()
        )
    except AttributeError:
        if (
            soup.find("p", {"class": "discontinued-title"}).text.strip()
            == "Discontinued"
        ):
            price = "Discontinued"
        else:
            raise KeyboardInterrupt
    # print(f'가격 : {price}')

    stock = soup.find("div", {"id": "stock-status"}).text.strip()
    # print(f'품절여부 : {stock}')

    serv_size, serv_per_cont = None, None
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
    try:
        sfacts = soup.find("div", {"class": "supplement-facts-container"}).find_all(
            "tr"
        )
        sfacts = [
            s
            for s in sfacts
            if s.find("td", {"colspan": False}) and s.find("strong") is None
        ]
    except AttributeError:
        sfacts = []
    # 영양소 체크 여부
    for s in sfacts:
        nonSelected = True
        if "Serving Size" in s.text:
            serv_size = s.text.split("Serving Size:")[1].strip()
        try:
            if "Servings Per Container" in s.text:
                serv_per_cont = s.text.split("Servings Per Container:")[1].strip()
            if "Serving Per Container" in s.text:
                serv_per_cont = s.text.split("Serving Per Container:")[1].strip()
        except IndexError:
            serv_per_cont = re.findall("\d+", s.text)[0]
        if (
            ("칼로리" in s.text or "Calories" in s.text)
            and "Calories from Fat" not in s.text
            and "Calories per gram" not in s.text
            and "Calories:" not in s.text
        ):
            try:
                cal.append(s.find_all("td")[1].text.strip())
            except Exception as e:
                print(e)
                cal.append(None)
            nonSelected = False
        if "지방 칼로리" in s.text or "지방에서 칼로리" in s.text or "Fat Calories" in s.text:
            fcal.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "나트륨" in s.text or "Sodium" in s.text:
            try:
                sod.append(s.find_all("td")[1].text.strip())
            except Exception as e:
                print(e)
                sod.append(None)
            nonSelected = False
        if "총 탄수화물" in s.text or "총탄수화물" in s.text or "Total Carbohydrate" in s.text:
            try:
                tcarb.append(s.find_all("td")[1].text.strip())
            except Exception as e:
                print(e)
                tcarb.append(None)
            nonSelected = False
        if "식이섬유" in s.text or "식이 섬유" in s.text:
            dfib.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if (
            "총 당류" in s.text or "당류" in s.text or "설탕" in s.text
        ) and "첨가" not in s.text:
            tsug.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if (
            "첨가된 설탕" in s.text
            or "첨가 된 설탕" in s.text
            or "첨가 당류" in s.text
            or "첨가된 당류" in s.text
            or "설탕 첨가" in s.text
            or "첨가당" in s.text
        ):
            asug.append(s.find_all("td")[0].text.strip())
            nonSelected = False
        if "총 지방" in s.text or "총지방" in s.text:
            tofat.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "불포화 지방" in s.text:
            ufat.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "포화지방" in s.text or "포화 지방" in s.text:
            sfat.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "트랜스 지방" in s.text:
            tfat.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "콜레스테롤" in s.text:
            chol.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "단백질" in s.text and "Calories per gram" not in s.text:
            try:
                prot.append(s.find_all("td")[1].text.strip())
            except Exception as e:
                print(e)
                prot.append(None)
            nonSelected = False

        ### % 포함 ###
        if "비타민 A" in s.text or "비타민A" in s.text:
            try:
                vita.append(s.find_all("td")[1].text.strip())
                vita_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "비타민 D" in s.text or "비타민D" in s.text:
            try:
                vitd.append(s.find_all("td")[1].text.strip())
                vitd_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "비타민 E" in s.text or "비타민E" in s.text:
            try:
                vite.append(s.find_all("td")[1].text.strip())
                vite_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "비타민 K" in s.text or "비타민K" in s.text:
            try:
                vitk.append(s.find_all("td")[1].text.strip())
                vitk_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "비타민 C" in s.text or "비타민C" in s.text:
            try:
                vitc.append(s.find_all("td")[1].text.strip())
                vitc_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if (
            "티아민" in s.text
            or "Vitamin B1" in s.text
            or "비타민 B-1" in s.text
            or "비타민 B1" in s.text
            or "비타민B1" in s.text
        ):
            try:
                thim.append(s.find_all("td")[1].text.strip())
                thim_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if (
            "리보플라빈" in s.text
            or "Vitamin B2" in s.text
            or "비타민 B-2" in s.text
            or "비타민 B2" in s.text
            or "비타민B2" in s.text
        ):
            try:
                ribo.append(s.find_all("td")[1].text.strip())
                ribo_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if (
            "니아신" in s.text
            or "Vitamin B3" in s.text
            or "비타민 B-3" in s.text
            or "비타민 B3" in s.text
            or "비타민B3" in s.text
        ):
            try:
                niac.append(s.find_all("td")[1].text.strip())
                niac_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if (
            "피리독신" in s.text
            or "Vitamin B6" in s.text
            or "비타민 B-6" in s.text
            or "비타민 B6" in s.text
            or "비타민B6" in s.text
        ):
            try:
                pyrd.append(s.find_all("td")[1].text.strip())
                pyrd_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if (
            "엽산" in s.text
            or "Folic Acid" in s.text
            or "Vitamin B9" in s.text
            or "비타민 B-9" in s.text
            or "비타민 B9" in s.text
            or "비타민B9" in s.text
        ):
            try:
                folt.append(s.find_all("td")[1].text.strip())
                folt_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if (
            "코발라민" in s.text
            or "시아노코발라민" in s.text
            or "Cobalamin" in s.text
            or "Cyanocobalamin" in s.text
            or "비타민 B12" in s.text
            or "비타민 B-12" in s.text
            or "비타민B12" in s.text
        ):
            try:
                coba.append(s.find_all("td")[1].text.strip())
                coba_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if (
            "판토텐산" in s.text
            or "Vitamin B5" in s.text
            or "비타민 B-5" in s.text
            or "비타민 B5" in s.text
            or "비타민B5" in s.text
        ):
            try:
                pant.append(s.find_all("td")[1].text.strip())
                pant_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if (
            "비오틴" in s.text
            or "Vitamin B7" in s.text
            or "비타민 B-7" in s.text
            or "비타민 B7" in s.text
            or "비타민B7" in s.text
        ):
            try:
                biot.append(s.find_all("td")[1].text.strip())
                biot_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "요오드" in s.text:
            try:
                iodi.append(s.find_all("td")[1].text.strip())
                iodi_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "구리" in s.text:
            try:
                copp.append(s.find_all("td")[1].text.strip())
                copp_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "불소" in s.text:
            try:
                fluo.append(s.find_all("td")[1].text.strip())
                fluo_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "칼슘" in s.text:
            try:
                calc.append(s.find_all("td")[1].text.strip())
                calc_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "마그네슘" in s.text:
            try:
                magn.append(s.find_all("td")[1].text.strip())
                magn_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "칼륨" in s.text:
            try:
                pota.append(s.find_all("td")[1].text.strip())
                pota_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "크롬" in s.text:
            try:
                chro.append(s.find_all("td")[1].text.strip())
                chro_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "철분" in s.text:
            try:
                iron.append(s.find_all("td")[1].text.strip())
                iron_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "아연" in s.text:
            try:
                zinc.append(s.find_all("td")[1].text.strip())
                zinc_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "몰리브덴" in s.text:
            try:
                moly.append(s.find_all("td")[1].text.strip())
                moly_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "인" in s.text:
            try:
                phos.append(s.find_all("td")[1].text.strip())
                phos_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "셀레늄" in s.text:
            try:
                sele.append(s.find_all("td")[1].text.strip())
                sele_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "망간" in s.text:
            try:
                mang.append(s.find_all("td")[1].text.strip())
                mang_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        if "염소" in s.text:
            try:
                chlo.append(s.find_all("td")[1].text.strip())
                chlo_per.append(s.find_all("td")[2].text.strip())
            except IndexError:
                pass
            nonSelected = False
        ###################################################
        if "히스티딘" in s.text:
            hist.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "이소류신" in s.text:
            isol.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "류신" in s.text:
            leuc.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "리신" in s.text:
            lysi.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "메타오닌" in s.text:
            meth.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "페닐알라닌" in s.text:
            phen.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "트레오닌" in s.text:
            thre.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "트립토판" in s.text:
            tryp.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "발린" in s.text:
            vali.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "세린" in s.text and "글리세린" not in s.text:
            seri.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "알라닌" in s.text:
            alan.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "아르기닌" in s.text:
            argi.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "아스파라긴" in s.text:
            aspa.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "시스테인" in s.text:
            cyst.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "글루타민" in s.text:
            glut.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "글리신" in s.text:
            glyc.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "프롤린" in s.text:
            prol.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "티로신" in s.text:
            tyro.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "녹차추출물" in s.text or "녹차잎추출물" in s.text:
            grnt.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "공액리놀레산" in s.text or "리놀레산" in s.text:
            conj.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "가르니시아" in s.text:
            garc.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "키토산" in s.text:
            chit.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "차전자피" in s.text:
            psyl.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "글루코만난" in s.text:
            gluc.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "알로에전잎" in s.text:
            aloe.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "크레아틴" in s.text:
            crea.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "시트룰린" in s.text:
            citr.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "아그마틴" in s.text:
            agma.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "베타알라닌" in s.text or "베타 알라닌" in s.text:
            beta.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "잔티젠" in s.text:
            xant.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "타우린" in s.text:
            taur.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "카페인" in s.text:
            caff.append(s.find_all("td")[1].text.strip())
            nonSelected = False
        if "카르니틴" in s.text:
            carn.append(s.find_all("td")[1].text.strip())
            nonSelected = False

        if nonSelected:
            etc.append("/".join([e.text.strip() for e in s.find_all("td")]))

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

    etc = "|".join(etc) if etc != [] else None

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
    )


def crawling_Kingmass(site_name, href, num):
    res = req.get(href, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")

    if "요청하신 페이지를 찾을수 없습니다." in res.text:
        raise KeyboardInterrupt

    # 사진
    image = soup.find("div", "keyImg").find("img").get("src")
    image = urljoin(res.url, image)
    save_image(site_name, image, num)
    # print(f"제품사진 : {image}")

    # 브랜드
    brand = "로니콜먼"
    # print(f"브랜드 : {brand}")

    # 제품명
    name = soup.find("h2", "item_name").text.strip()
    # print(f"제품명 : {name}")

    # 맛
    if (
        soup.find("tbody", "xans-product-option") is not None
        and soup.find("tbody", "xans-product-option")
        .find("th", {"scope": "row"})
        .text.strip()
        == "Flavor"
    ):
        flavor = [
            f.text.strip()
            for f in soup.find("tbody", "xans-product-option")
            .find("select")
            .find_all("option")
            if "*" not in f.get("value")
        ]
        flavor = "/".join(flavor)
    else:
        flavor = None
    # print(f"맛 : {flavor}")

    # 용량
    volume = (
        name.split(" ")[-1]
        if "(" not in name.split(" ")[-1]
        else " ".join(name.split(" ")[-2:])
    )
    # print(f"용량 : {volume}")

    # URL
    url = res.url
    # print(f"제품 URL : {url}")

    # 제품번호
    pcode = res.url.split("product_no=")[1].split("&")[0]
    # print(f"제품번호 : {pcode}")

    # 가격
    price = soup.find("tr", "price").find("strong", {"id": "span_product_price_text"})
    price = price.text.strip() if price is not None else None
    # print(f"가격 : {price}")

    # 품절여부
    if flavor is not None:
        if all([True if "[품절]" in s else False for s in flavor.split("/")]):
            stock = True
        else:
            stock = False
    else:
        stock = None
    # print(f"품절여부 : {stock}")

    # 상세페이지 이미지부분
    detail_images = soup.find("div", "cont").find_all("img")
    detail_images = [quote(i.get("ec-data-src")) for i in detail_images]
    detail_images = "|".join([urljoin(res.url, i) for i in detail_images])
    # print(f"상세이미지 : {detail_images}")

    # 1회 제공량 / 총 제공량
    serv_size, serv_cont = None, None
    # print(f"1회 제공량 : {serv_size}")
    # print(f"총 제공량 : {serv_cont}")

    # 영양성분표
    nutri = None
    # print(f"영양성분표 : {nutri}")

    # 원료성분
    mingrd = None
    # print(f"원료성분 : {mingrd}")

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
    temp = dict()
    # 영양성분
    try:
        test = True if nutri is None else False
        if test:
            pass
            # print("영양성분표 없음")
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

            #                 print(f'선택되어지지 않았는가? => {nonSelected}')
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
    )


def crawling_MonsterMart(site_name, href, num):
    res = req.get(href, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    temp = dict()
    if "요청하신 페이지를 찾을수 없습니다." in res.text:
        raise KeyboardInterrupt

    # 사진
    image = soup.find("img", "ty-pict").get("src")
    save_image(site_name, image, num)
    # print(f"제품사진 : {image}")

    # 브랜드
    brand = soup.find("div", "brand").text.strip()
    # print(f"브랜드 : {brand}")

    # 제품명
    name = soup.find("h1", "ty-product-block-title").text.strip()
    # print(f"제품명 : {name}")

    # 맛
    try:
        flavor = soup.find("span", "label_flavor").text.strip()
    except Exception as er:
        try:
            flavor = soup.find("select").text.strip()
            flavor = flavor if "맛선택" not in flavor else None
        except Exception as e:
            print(e, er)
            flavor = None
    # print(f"맛 : {flavor}")

    # 용량
    try:
        volume = soup.find("td", "label_size").text.strip()
    except Exception as e:
        print(e)
        volume = None
    # print(f"용량 : {volume}")

    # 1회 제공량 / 총 제공량
    if soup.find_all("", {"class": "label_serving"}):
        serv_size = [
            s.text.lower()
            for s in soup.find_all("", {"class": "label_serving"})
            if "serving size" in s.text.lower()
        ]
        if serv_size:
            serv_size = "|".join(serv_size)
            serv_size = (
                serv_size.split("serving size")[1]
                .split("|")[0]
                .replace(":", "")
                .strip()
            )
        else:
            serv_size = None

        serv_cont = [
            s.text.lower()
            for s in soup.find_all("", {"class": "label_serving"})
            if "servings per" in s.text.lower() or "serving per" in s.text.lower()
        ]
        if serv_cont:
            serv_cont = "|".join(serv_cont)
            try:
                serv_cont = (
                    serv_cont.split("servings per")[1]
                    .split("|")[0]
                    .split(":")[1]
                    .strip()
                )
            except IndexError:
                try:
                    serv_cont = serv_cont.split("servings per")[1].split("|")[0].strip()
                except IndexError:
                    try:
                        serv_cont = (
                            serv_cont.split("serving per")[1]
                            .split("|")[0]
                            .split(":")[1]
                            .strip()
                        )
                    except IndexError:
                        serv_cont = (
                            serv_cont.split("serving per")[1].split("|")[0].strip()
                        )
            serv_cont = serv_cont.replace("container", "").strip()
        else:
            serv_cont = None
    else:
        serv_size, serv_cont = None, None
    # print(f"1회 제공량 : {serv_size}")
    # print(f"총 제공량 : {serv_cont}")

    # 영양성분표
    table_list = []
    if soup.find_all("table", {"id": "label_outer_table"}):
        for table in soup.find_all("table", {"id": "label_outer_table"}):
            try:
                table.find("span", "label_size").decompose()
            except AttributeError:
                pass
            try:
                table.find("td", "label_flavor").decompose()
            except AttributeError:
                pass

            for ls in table.find_all("td", "label_serving"):
                ls.decompose()
            for ls in table.find_all("span", "label_serving"):
                ls.decompose()
            try:
                table_list += pd.read_html(str(table), header=None)
            except IndexError:
                pass
    elif soup.find_all("table", {"id": "facts_table"}):
        for table in soup.find_all("table", {"id": "facts_table"}):
            try:
                table.find("span", "label_size").decompose()
            except AttributeError:
                pass
            try:
                table.find("td", "label_flavor").decompose()
            except AttributeError:
                pass

            for ls in table.find_all("td", "label_serving"):
                ls.decompose()
            for ls in table.find_all("span", "label_serving"):
                ls.decompose()
            try:
                table_list += pd.read_html(str(table), header=None)
            except IndexError:
                pass
    elif soup.find_all("table", {"class": "ingredients"}):
        for table in soup.find_all("table", {"class": "ingredients"}):
            try:
                table.find("big").decompose()
            except AttributeError:
                pass
            try:
                table.find("span", "label_size").decompose()
            except AttributeError:
                pass
            try:
                table.find("td", "label_flavor").decompose()
            except AttributeError:
                pass

            for ls in table.find_all("td", "label_serving"):
                ls.decompose()
            for ls in table.find_all("span", "label_serving"):
                ls.decompose()
            try:
                table_list += pd.read_html(str(table), header=None)
            except IndexError:
                pass
    else:
        for table in soup.find_all("table"):
            try:
                table.find("big").decompose()
            except AttributeError:
                pass
            try:
                table.find("span", "label_size").decompose()
            except AttributeError:
                pass
            try:
                table.find("td", "label_flavor").decompose()
            except AttributeError:
                pass

            for ls in table.find_all("td", "label_serving"):
                ls.decompose()
            for ls in table.find_all("span", "label_serving"):
                ls.decompose()
            try:
                table_list += pd.read_html(str(table), header=None)
            except IndexError:
                pass
    if table_list:
        nutri = table_list[0]
        for num in range(len(table_list)):
            nutri = pd.concat([nutri, table_list[num]])
    else:
        tr_ings, tr_qty, tr_dvs = [], [], []
        for tr in soup.find_all("tr", {"class": "facts_label"}):
            if tr.find("td", "label_ing") is None:
                continue
            tr_ings.append(
                tr.find("td", "label_ing").text.strip()
                if tr.find("td", "label_ing") is not None
                else None
            )
            tr_qty.append(
                tr.find("td", "label_qty").text.strip()
                if tr.find("td", "label_qty") is not None
                else None
            )
            tr_dvs.append(
                tr.find("td", "label_dv").text.strip()
                if tr.find("td", "label_dv") is not None
                else None
            )
        nutri = pd.DataFrame()
        nutri[0] = tr_ings
        nutri[1] = tr_qty
        nutri[2] = tr_dvs
    nutri = nutri.drop_duplicates(list(nutri.columns)[0]).reset_index()
    nutri = nutri.fillna("")
    del nutri["index"]
    # print(f"성분표 : {nutri}")

    # 원료성분
    ingrd = "".join([o.text.strip() for o in soup.find_all("tr", "other_label")])
    mingrd = (
        ingrd.lower().split("ingredients:")[-1].split(".")[0]
        if "ingredients:" in ingrd.lower()
        else None
    )
    temp["원료성분"] = ingrd
    if mingrd is None:
        mingrd = (
            ingrd.lower().split("ingredients")[-1].split(".")[0]
            if "ingredients" in ingrd.lower()
            else None
        )
    # print(f"원료성분 : {mingrd}")

    # 알러지성분
    aingrd = None
    if "allergens:" in ingrd.lower():
        aingrd = (
            ingrd.lower().split("allergens:")[-1].split(".")[0].replace(":", "").strip()
        )
    elif "contains" in ingrd.lower():
        aingrd = (
            ingrd.lower().split("contains")[-1].split(".")[0].replace(":", "").strip()
        )
    # print(f"알러지 성분 : {aingrd}")

    # URL
    url = res.url
    # print(f"제품 URL : {url}")

    # 제품번호
    pcode = res.url.split(".net/")[-1].replace(".html", "")
    # print(f"제품번호 : {pcode}")

    # 가격
    price = soup.find("span", "ty-price").text.strip()
    # print(f"가격 : {price}")

    # 품절여부
    try:
        stock = (
            True if soup.find("span", "ty-qty-in-stock").text.strip() != "가능" else False
        )
    except AttributeError:
        stock = None
    # print(f"품절여부 : {stock}")

    # 09/07 추가 일부영양소 일일 %량
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
    etc = []
    # 영양소 체크 여부
    nonSelected = True
    # 영양성분
    try:
        test = True if nutri is None else False
        if test:
            # print("영양성분표 없음")
            raise KeyboardInterrupt
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
                ("fat" in nut.lower() or "total fat" in nut.lower())
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

            #                 print(f'선택되어지지 않았는가? => {nonSelected}')
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
        ingrd,
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
    )


def crawling_MyProtein(site_name, href, num):
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
        save_image(site_name, image, num)
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
        flavor = soup.find(
            "select", {"id": "athena-product-variation-dropdown-5"}
        ).find_all("option")
        flavor = "/".join([f.text.strip() for f in flavor])
    except AttributeError:
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
        mingrd = "/".join([i.text.strip() for i in ingrd])

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
        print(e)
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
        for i in soup.find_all("div", {"class": "productDescription_contentProperties"})
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
        print(e)
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
                    cal_value = s.find_all("td")[key_index1].text.split("/")[-1].strip()
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
                if "Fibre" in s.text or "Dietary Fiber" in s.text or "식이섬유" in s.text:
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
                if "Beta Alanine" in s.text or "베타알라닌" in s.text or "베타 알라닌" in s.text:
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
    )


def crawling_Ople(site_name, href, num):
    res = req.get(href, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    temp = dict()
    if "단종된 상품입니다." in res.text:
        print(f"단종된 상품.")
        raise KeyboardInterrupt

    # 사진
    image = soup.find("div", "item-Thum").find("img").get("src")
    # print(f'제품사진 : {image}')
    save_image(site_name, image, num)
    # *** 기본 데이터
    basic_data = soup.find("div", {"id": "div_explan"}).find_all("div", "ex_box")
    # 브랜드
    try :
        brand = [
            b.find("div", "box_item_title").text.strip()
            for b in basic_data
            if "제조사" == b.find("p", "box_title").text.strip()
        ]
        brand = brand[0] if brand != [] else None
    except Exception as e:
        brand = None
        print(e)

    # print(f'브랜드 : {brand}')

    # 제품명
    name = [
        b.find("div", "box_item_title").text.strip()
        for b in basic_data
        if "제품명" in b.find("p", "box_title").text.strip()
    ]
    name = " / ".join(name)
    # print(f'제품명 : {name}')

    # 맛
    flavor = None
    # print(f'맛 : {flavor}')

    # 용량
    volume = [
        b.find("div", "box_item_title").text.strip()
        for b in basic_data
        if "용량" in b.find("p", "box_title").text.strip()
    ]
    volume = volume[0] if volume != [] else None
    # print(f"용량 : {volume}")

    # 원료성분
    try:
        ingrd = [
            b.find("div", "box_item_title")
            for b in basic_data
            if "영문 설명" in b.find("p", "box_title").text.strip()
        ][-1]
        ingrd = [p.text for p in ingrd.find_all("p")]
        ingrdList = []
        for inum, ig in enumerate(ingrd):
            if "ingredients" in ig.lower():
                try:
                    ingrdList.append(f"{ig}\n{ingrd[inum + 1]}")
                except IndexError:
                    ingrdList.append(f"{ig}")
        ingrd = ingrdList[-1] if ingrdList != [] else None
        temp["원료성분"] = ingrd
    except IndexError:
        ingrd = None
    # print(f"원료성분 : {ingrd}")

    # 알러지 성분
    if ingrd is not None:
        aingrd = (
            ingrd.lower().split("contains")[-1].split(".")[0].strip()
            if "contains" in ingrd.lower()
            else None
        )
    else:
        aingrd = None
    # print(f"알러지 성분 : {aingrd}")

    # 영양성분표
    if soup.find("table", "SupplementFacts") is not None:
        nutri = pd.read_html(str(soup.find("table", "SupplementFacts")), header=2)[0]
        nutri = nutri.fillna("")
    else:
        nutri = None

    # URL
    url = res.url
    # print(f'제품 URL : {url}')

    # 제품번호
    pcode = res.url.split("=")[-1]
    # print(f'제품번호 : {pcode}')

    # 가격
    price = str([s for s in soup.find_all("script") if "basic_amount" in str(s)][0])
    price = [j.strip() for j in price.split("\n") if "var basic_amount" in j][0]
    price = price.split("=")[-1].replace("parseInt", "").strip()
    price = "".join(re.findall(r"\d", price))
    # print(f'가격 : {price}')

    # 품절여부
    stock = None
    # print(f'품절여부 : {stock}')

    # 1회 제공량 / 총 제공량
    try:
        test = True if nutri is None else False
        serv_size, serv_cont = None, None
    except ValueError:
        serving = [
            t.text.strip()
            for t in soup.find("table", "SupplementFacts").find("thead").find_all("tr")
        ]
        try:
            serv_size = [
                s.split(":")[-1].strip() for s in serving if "size" in s.lower()
            ][0]
        except IndexError:
            serv_size = None
        try:
            serv_cont = [
                s.split(":")[-1].strip() for s in serving if "container" in s.lower()
            ][0]
        except IndexError:
            serv_cont = None
    # print(f'1회 제공량 : {serv_size}')
    # print(f'총 제공량 : {serv_cont}')

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
    ) = [[] for x in range(101)]
    etc = []
    # 영양소 체크 여부
    nonSelected = True

    # 영양성분
    try:
        test = True if nutri is None else False
    except ValueError:
        nutn = list(nutri["Unnamed: 0"])
        nutp = list(nutri["Amount Per Serving"])
        nutd = list(nutri["% Daily Value"])
        for nnum, nut in enumerate(nutn):
            # 칼로리
            if "calories" in nut.lower() and "fat" not in nut.lower():
                cal.append(nutp[nnum])
                nonSelected = False
            # 지방 칼로리
            if "fat calories" in nut.lower() or (
                "calories" in nut.lower() and "fat" in nut.lower()
            ):
                fcal.append(nutp[nnum])
                nonSelected = False
            # 나트륨
            if "salt" in nut.lower() or "sodium" in nut.lower():
                sod.append(nutp[nnum])
                nonSelected = False
            # 총 탄수화물
            if "carbohydrates" in nut.lower() or "total carbohydrate" in nut.lower():
                tcarb.append(nutp[nnum])
                nonSelected = False
            # 식이섬유
            if "fibre" in nut.lower() or "dietary fiber" in nut.lower():
                dfib.append(nutp[nnum])
                nonSelected = False
            # 설탕
            if "sugar" in nut.lower() and "added" not in nut.lower():
                tsug.append(nutp[nnum])
                nonSelected = False
            # 첨가당
            if "added sugar" in nut.lower():
                asug.append(nutp[nnum])
                nonSelected = False
            # 지방
            if ("fat" in nut.lower() or "total fat" in nut.lower()) and (
                "saturate" not in nut.lower() or "trans" not in nut.lower()
            ):
                tofat.append(nutp[nnum])
                nonSelected = False
            # 불포화지방
            if "unsaturate" in nut.lower() and "fat" in nut.lower():
                ufat.append(nutp[nnum])
                nonSelected = False
            # 포화지방
            if (
                "saturate" in nut.lower()
                and "fat" in nut.lower()
                and "unsaturate" not in nut.lower()
            ):
                sfat.append(nutp[nnum])
                nonSelected = False
            # 트랜스지방
            if "fat" in nut.lower() and "trans" in nut.lower():
                tfat.append(nutp[nnum])
                nonSelected = False
            # 콜레스테롤
            if "cholesterol" in nut.lower():
                chol.append(nutp[nnum])
                nonSelected = False
            # 단백질
            if "protein" in nut.lower():
                prot.append(nutp[nnum])
                nonSelected = False

            ############################################################################################
            ### % 포함 ###
            if "vitamin a" in nut.lower():
                vita.append(nutp[nnum])
                vita_per.append(nutd[nnum])
                nonSelected = False
            if "vitamin d" in nut.lower():
                try:
                    vitd.append(nutp[nnum])
                    vitd_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "vitamin e" in nut.lower() or "비타민 E" in nut.lower():
                try:
                    vite.append(nutp[nnum])
                    vite_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "vitamin k" in nut.lower() or "비타민 K" in nut.lower():
                try:
                    vitk.append(nutp[nnum])
                    vitk_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "vitamin c" in nut.lower() or "비타민 C" in nut.lower():
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
            ):
                try:
                    biot.append(nutp[nnum])
                    biot_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "iodine" in nut.lower() or "아이오딘" in nut.lower() or "요오드" in nut.lower():
                try:
                    iodi.append(nutp[nnum])
                    iodi_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "copper" in nut.lower() or "구리" in nut.lower():
                try:
                    copp.append(nutp[nnum])
                    copp_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "fluoride" in nut.lower() or "불소" in nut.lower():
                try:
                    fluo.append(nutp[nnum])
                    fluo_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "calcium" in nut.lower() or "칼슘" in nut.lower():
                try:
                    calc.append(nutp[nnum])
                    calc_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "magnesium" in nut.lower() or "마그네슘" in nut.lower():
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
            ):
                try:
                    pota.append(nutp[nnum])
                    pota_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "chromium" in nut.lower() or "크롬" in nut.lower():
                try:
                    chro.append(nutp[nnum])
                    chro_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "iron" in nut.lower() or "철분" in nut.lower():
                try:
                    iron.append(nutp[nnum])
                    iron_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "zinc" in nut.lower() or "아연" in nut.lower():
                try:
                    zinc.append(nutp[nnum])
                    zinc_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "molybdenum" in nut.lower() or "몰리브덴" in nut.lower():
                try:
                    moly.append(nutp[nnum])
                    moly_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "phosphorus" in nut.lower() or "인" in nut.lower():
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
            ):
                try:
                    sele.append(nutp[nnum])
                    sele_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "manganese" in nut.lower() or "망간" in nut.lower():
                try:
                    mang.append(nutp[nnum])
                    mang_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            if "chloride" in nut.lower() or "염소" in nut.lower():
                try:
                    chlo.append(nutp[nnum])
                    chlo_per.append(nutd[nnum])
                except IndexError:
                    pass
                nonSelected = False
            ###################################################
            if "histidine" in nut.lower() or "히스티딘" in nut.lower():
                hist.append(nutp[nnum])
                nonSelected = False
            if "isoleucine" in nut.lower() or "이소류신" in nut.lower():
                isol.append(nutp[nnum])
                nonSelected = False
            if "leucine" in nut.lower() or "류신" in nut.lower():
                leuc.append(nutp[nnum])
                nonSelected = False
            if "lysine" in nut.lower() or "리신" in nut.lower():
                lysi.append(nutp[nnum])
                nonSelected = False
            if "methionine" in nut.lower() or "메타오닌" in nut.lower():
                meth.append(nutp[nnum])
                nonSelected = False
            if "phenylAlanine" in nut.lower() or "페닐알라닌" in nut.lower():
                phen.append(nutp[nnum])
                nonSelected = False
            if "threonine" in nut.lower() or "트레오닌" in nut.lower():
                thre.append(nutp[nnum])
                nonSelected = False
            if "tryptophane" in nut.lower() or "트립토판" in nut.lower():
                tryp.append(nutp[nnum])
                nonSelected = False
            if "valine" in nut.lower() or "발린" in nut.lower():
                vali.append(nutp[nnum])
                nonSelected = False
            if "serine" in nut.lower() or "세린" in nut.lower():
                seri.append(nutp[nnum])
                nonSelected = False
            if "alanine" in nut.lower() or "알라닌" in nut.lower():
                alan.append(nutp[nnum])
                nonSelected = False
            if "arginine" in nut.lower() or "아르기닌" in nut.lower():
                argi.append(nutp[nnum])
                nonSelected = False
            if "asparagine" in nut.lower() or "아스파라긴" in nut.lower():
                aspa.append(nutp[nnum])
                nonSelected = False
            if "cysteine" in nut.lower() or "시스테인" in nut.lower():
                cyst.append(nutp[nnum])
                nonSelected = False
            if "glutamine" in nut.lower() or "글루타민" in nut.lower():
                glut.append(nutp[nnum])
                nonSelected = False
            if "glycine" in nut.lower() or "글리신" in nut.lower():
                glyc.append(nutp[nnum])
                nonSelected = False
            if "proline" in nut.lower() or "프롤린" in nut.lower():
                prol.append(nutp[nnum])
                nonSelected = False
            if "tyrosine" in nut.lower() or "티로신" in nut.lower():
                tyro.append(nutp[nnum])
                nonSelected = False
            if (
                "green Tea" in nut.lower()
                or "녹차추출물" in nut.lower()
                or "녹차" in nut.lower()
            ):
                grnt.append(nutp[nnum])
                nonSelected = False
            if "conjugated linoleic" in nut.lower() or "공액리놀레산" in nut.lower():
                conj.append(nutp[nnum])
                nonSelected = False
            if "garcinia cambogia" in nut.lower() or "가르시니아" in nut.lower():
                garc.append(nutp[nnum])
                nonSelected = False
            if "chitosan" in nut.lower() or "키토산" in nut.lower():
                chit.append(nutp[nnum])
                nonSelected = False
            if "psyllium" in nut.lower() or "차전자피" in nut.lower():
                psyl.append(nutp[nnum])
                nonSelected = False
            if "glucomannan" in nut.lower() or "글루코만난" in nut.lower():
                gluc.append(nutp[nnum])
                nonSelected = False
            if "aloe" in nut.lower() or "알로에" in nut.lower():
                aloe.append(nutp[nnum])
                nonSelected = False
            if "creatine" in nut.lower() or "크레아틴" in nut.lower():
                crea.append(nutp[nnum])
                nonSelected = False
            if "citrulline" in nut.lower() or "시트룰린" in nut.lower():
                citr.append(nutp[nnum])
                nonSelected = False
            if "agmatine" in nut.lower() or "아그마틴" in nut.lower():
                agma.append(nutp[nnum])
                nonSelected = False
            if (
                "beta alanine" in nut.lower()
                or "베타알라닌" in nut.lower()
                or "베타 알라닌" in nut.lower()
            ):
                beta.append(nutp[nnum])
                nonSelected = False
            if "xanthigen" in nut.lower() or "잔티젠" in nut.lower():
                xant.append(nutp[nnum])
                nonSelected = False
            if "taurine" in nut.lower() or "타우린" in nut.lower():
                taur.append(nutp[nnum])
                nonSelected = False
            if "caffeine" in nut.lower() or "카페인" in nut.lower():
                caff.append(nutp[nnum])
                nonSelected = False
            if "carnitine" in nut.lower() or "카르니틴" in nut.lower():
                carn.append(nutp[nnum])
                nonSelected = False
            ############################################################################################

            #                 print(f'선택되어지지 않았는가? => {nonSelected}')
            if nonSelected == True:
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
        ingrd,
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
    )
