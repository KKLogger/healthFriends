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
        save_image(site_name, image, num, "product")
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
        mingrd = (
            soup.find("div", {"class": "prodOverviewIngred"}).get_text("|||").strip()
        )
        mingrd = remove_part(mingrd)
        ingr_words = substract_ingredient(mingrd, ingr_list)
        temp["원료성분"] = ingr_words
        temp["url"] = href
    except Exception as e:
        mingrd = None
        ingr_words = None
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
        ingr_words,
    )
