import requests as req
from bs4 import BeautifulSoup
import pickle, re
import pandas as pd
from urllib.request import urljoin, build_opener, install_opener, urlretrieve
import time
import json
import os
from get_urls import get_urls
from crawling import crawling
from crawling import calculate_flavor


def load_url(opt, site_name):
    """
    :param opt: 1. open pickle 2.call function
    :param site_name
    :return: urls
    """
    if opt == 1:
        with open(f"../../data/crawling/urls_{site_name}.pickle", "rb") as f:
            urls = pickle.load(f)
    elif opt == 2:
        urls = get_urls(site_name)
    else:
        print("option codes wrong...")
        urls = []
    urls = list(dict.fromkeys(urls))
    return urls


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Creating directory. " + directory)


"""
:TODO!! 1. 성분표 이미지 ( 텍스트 데이터가 없는 상품에 대해 ) 수집
        2. 성분 전처리 확인
        3. 분류 결과 확인 후 조건 검토
        4. 상품 옵션 별 수집 -> monstermart ingredients_by_options 통해서 옵션 지정 가능
        5.마이프로틴 좌측 성분란에 맛 별로 성분이 존재 
"""

if __name__ == "__main__":
    start = time.time()
    # site_names = ["Ople"]
    site_names = [
        "365Muscle",
        "iHerb",
        # "IronMax",
        # "Kingmass",
        "MonsterMart",
        "MyProtein",
        "Ople",
    ]
    createFolder("data")
    createFolder("image")
    for site_name in site_names:
        createFolder(f"image/{site_name}")
        urls = load_url(2, site_name)
        max_url = len(urls)
        # max_url = 10
        (
            image_list,
            brand_list,
            name_list,
            flavor_list,
            volume_list,
            mingrd_list,
            aingrd_list,
            url_list,
            pcode_list,
            price_list,
            stock_list,
            serv_size_list,
            serv_per_cont_list,
            cal_list,
            fcal_list,
            sod_list,
            tcarb_list,
            dfib_list,
            tsug_list,
            asug_list,
            tofat_list,
            ufat_list,
            sfat_list,
            tfat_list,
            chol_list,
            prot_list,
            vita_list,
            vitd_list,
            vite_list,
            vitk_list,
            vitc_list,
            thim_list,
            ribo_list,
            niac_list,
            pyrd_list,
            folt_list,
            coba_list,
            pant_list,
            biot_list,
            iodi_list,
            copp_list,
            fluo_list,
            calc_list,
            magn_list,
            pota_list,
            chro_list,
            iron_list,
            zinc_list,
            moly_list,
            phos_list,
            sele_list,
            mang_list,
            chlo_list,
            hist_list,
            isol_list,
            leuc_list,
            lysi_list,
            meth_list,
            phen_list,
            thre_list,
            tryp_list,
            vali_list,
            seri_list,
            alan_list,
            argi_list,
            aspa_list,
            cyst_list,
            glut_list,
            glyc_list,
            prol_list,
            tyro_list,
            grnt_list,
            conj_list,
            garc_list,
            chit_list,
            psyl_list,
            gluc_list,
            aloe_list,
            crea_list,
            citr_list,
            agma_list,
            beta_list,
            xant_list,
            taur_list,
            caff_list,
            carn_list,
            vita_per_list,
            vitd_per_list,
            vite_per_list,
            vitk_per_list,
            vitc_per_list,
            thim_per_list,
            ribo_per_list,
            niac_per_list,
            pyrd_per_list,
            folt_per_list,
            coba_per_list,
            pant_per_list,
            biot_per_list,
            iodi_per_list,
            copp_per_list,
            fluo_per_list,
            calc_per_list,
            magn_per_list,
            pota_per_list,
            chro_per_list,
            iron_per_list,
            zinc_per_list,
            moly_per_list,
            phos_per_list,
            sele_per_list,
            mang_per_list,
            chlo_per_list,
            etc_list,
            detail_images_list,
            error,
            ingr_words_list,
        ) = [[] for x in range(117)]
        result = list()
        for n, href in enumerate(urls[:max_url]):
            print(href)
            try:
                if (
                    site_name == "MonsterMart"
                    or site_name == "MyProtein"
                    or site_name == "365Muscle"
                    or site_name == "IronMax"
                    or site_name == "Kingmass"
                ):
                    flavor_num = calculate_flavor(href, site_name)
                    for f_num in range(flavor_num):
                        (
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
                        ) = crawling(site_name, href, n, f_num)
                        if temp != dict():
                            result.append(temp)
                        ingr_words_list.append(ingr_words)
                        image_list.append(image)
                        brand_list.append(brand)
                        name_list.append(name)
                        flavor_list.append(flavor)
                        volume_list.append(volume)
                        mingrd_list.append(mingrd)
                        aingrd_list.append(aingrd)
                        url_list.append(url)
                        pcode_list.append(pcode)
                        price_list.append(price)
                        stock_list.append(stock)
                        serv_size_list.append(serv_size)
                        serv_per_cont_list.append(serv_per_cont)
                        cal_list.append(cal)
                        fcal_list.append(fcal)
                        sod_list.append(sod)
                        tcarb_list.append(tcarb)
                        dfib_list.append(dfib)
                        tsug_list.append(tsug)
                        asug_list.append(asug)
                        tofat_list.append(tofat)
                        ufat_list.append(ufat)
                        sfat_list.append(sfat)
                        tfat_list.append(tfat)
                        chol_list.append(chol)
                        prot_list.append(prot)
                        vita_list.append(vita)
                        vitd_list.append(vitd)
                        vite_list.append(vite)
                        vitk_list.append(vitk)
                        vitc_list.append(vitc)
                        thim_list.append(thim)
                        ribo_list.append(ribo)
                        niac_list.append(niac)
                        pyrd_list.append(pyrd)
                        folt_list.append(folt)
                        coba_list.append(coba)
                        pant_list.append(pant)
                        biot_list.append(biot)
                        iodi_list.append(iodi)
                        copp_list.append(copp)
                        fluo_list.append(fluo)
                        calc_list.append(calc)
                        magn_list.append(magn)
                        pota_list.append(pota)
                        chro_list.append(chro)
                        iron_list.append(iron)
                        zinc_list.append(zinc)
                        moly_list.append(moly)
                        phos_list.append(phos)
                        sele_list.append(sele)
                        mang_list.append(mang)
                        chlo_list.append(chlo)
                        hist_list.append(hist)
                        isol_list.append(isol)
                        leuc_list.append(leuc)
                        lysi_list.append(lysi)
                        meth_list.append(meth)
                        phen_list.append(phen)
                        thre_list.append(thre)
                        tryp_list.append(tryp)
                        vali_list.append(vali)
                        seri_list.append(seri)
                        alan_list.append(alan)
                        argi_list.append(argi)
                        aspa_list.append(aspa)
                        cyst_list.append(cyst)
                        glut_list.append(glut)
                        glyc_list.append(glyc)
                        prol_list.append(prol)
                        tyro_list.append(tyro)
                        grnt_list.append(grnt)
                        conj_list.append(conj)
                        garc_list.append(garc)
                        chit_list.append(chit)
                        psyl_list.append(psyl)
                        gluc_list.append(gluc)
                        aloe_list.append(aloe)
                        crea_list.append(crea)
                        citr_list.append(citr)
                        agma_list.append(agma)
                        beta_list.append(beta)
                        xant_list.append(xant)
                        taur_list.append(taur)
                        caff_list.append(caff)
                        carn_list.append(carn)
                        vita_per_list.append(vita_per)
                        vitd_per_list.append(vitd_per)
                        vite_per_list.append(vite_per)
                        vitk_per_list.append(vitk_per)
                        vitc_per_list.append(vitc_per)
                        thim_per_list.append(thim_per)
                        ribo_per_list.append(ribo_per)
                        niac_per_list.append(niac_per)
                        pyrd_per_list.append(pyrd_per)
                        folt_per_list.append(folt_per)
                        coba_per_list.append(coba_per)
                        pant_per_list.append(pant_per)
                        biot_per_list.append(biot_per)
                        iodi_per_list.append(iodi_per)
                        copp_per_list.append(copp_per)
                        fluo_per_list.append(fluo_per)
                        calc_per_list.append(calc_per)
                        magn_per_list.append(magn_per)
                        pota_per_list.append(pota_per)
                        chro_per_list.append(chro_per)
                        iron_per_list.append(iron_per)
                        zinc_per_list.append(zinc_per)
                        moly_per_list.append(moly_per)
                        phos_per_list.append(phos_per)
                        sele_per_list.append(sele_per)
                        mang_per_list.append(mang_per)
                        chlo_per_list.append(chlo_per)
                        etc_list.append(etc)
                        detail_images_list.append(detail_images)
                else:
                    (
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
                    ) = crawling(site_name, href, n, 0)
                    if temp != dict():
                        result.append(temp)
                    ingr_words_list.append(ingr_words)
                    image_list.append(image)
                    brand_list.append(brand)
                    name_list.append(name)
                    flavor_list.append(flavor)
                    volume_list.append(volume)
                    mingrd_list.append(mingrd)
                    aingrd_list.append(aingrd)
                    url_list.append(url)
                    pcode_list.append(pcode)
                    price_list.append(price)
                    stock_list.append(stock)
                    serv_size_list.append(serv_size)
                    serv_per_cont_list.append(serv_per_cont)
                    cal_list.append(cal)
                    fcal_list.append(fcal)
                    sod_list.append(sod)
                    tcarb_list.append(tcarb)
                    dfib_list.append(dfib)
                    tsug_list.append(tsug)
                    asug_list.append(asug)
                    tofat_list.append(tofat)
                    ufat_list.append(ufat)
                    sfat_list.append(sfat)
                    tfat_list.append(tfat)
                    chol_list.append(chol)
                    prot_list.append(prot)
                    vita_list.append(vita)
                    vitd_list.append(vitd)
                    vite_list.append(vite)
                    vitk_list.append(vitk)
                    vitc_list.append(vitc)
                    thim_list.append(thim)
                    ribo_list.append(ribo)
                    niac_list.append(niac)
                    pyrd_list.append(pyrd)
                    folt_list.append(folt)
                    coba_list.append(coba)
                    pant_list.append(pant)
                    biot_list.append(biot)
                    iodi_list.append(iodi)
                    copp_list.append(copp)
                    fluo_list.append(fluo)
                    calc_list.append(calc)
                    magn_list.append(magn)
                    pota_list.append(pota)
                    chro_list.append(chro)
                    iron_list.append(iron)
                    zinc_list.append(zinc)
                    moly_list.append(moly)
                    phos_list.append(phos)
                    sele_list.append(sele)
                    mang_list.append(mang)
                    chlo_list.append(chlo)
                    hist_list.append(hist)
                    isol_list.append(isol)
                    leuc_list.append(leuc)
                    lysi_list.append(lysi)
                    meth_list.append(meth)
                    phen_list.append(phen)
                    thre_list.append(thre)
                    tryp_list.append(tryp)
                    vali_list.append(vali)
                    seri_list.append(seri)
                    alan_list.append(alan)
                    argi_list.append(argi)
                    aspa_list.append(aspa)
                    cyst_list.append(cyst)
                    glut_list.append(glut)
                    glyc_list.append(glyc)
                    prol_list.append(prol)
                    tyro_list.append(tyro)
                    grnt_list.append(grnt)
                    conj_list.append(conj)
                    garc_list.append(garc)
                    chit_list.append(chit)
                    psyl_list.append(psyl)
                    gluc_list.append(gluc)
                    aloe_list.append(aloe)
                    crea_list.append(crea)
                    citr_list.append(citr)
                    agma_list.append(agma)
                    beta_list.append(beta)
                    xant_list.append(xant)
                    taur_list.append(taur)
                    caff_list.append(caff)
                    carn_list.append(carn)
                    vita_per_list.append(vita_per)
                    vitd_per_list.append(vitd_per)
                    vite_per_list.append(vite_per)
                    vitk_per_list.append(vitk_per)
                    vitc_per_list.append(vitc_per)
                    thim_per_list.append(thim_per)
                    ribo_per_list.append(ribo_per)
                    niac_per_list.append(niac_per)
                    pyrd_per_list.append(pyrd_per)
                    folt_per_list.append(folt_per)
                    coba_per_list.append(coba_per)
                    pant_per_list.append(pant_per)
                    biot_per_list.append(biot_per)
                    iodi_per_list.append(iodi_per)
                    copp_per_list.append(copp_per)
                    fluo_per_list.append(fluo_per)
                    calc_per_list.append(calc_per)
                    magn_per_list.append(magn_per)
                    pota_per_list.append(pota_per)
                    chro_per_list.append(chro_per)
                    iron_per_list.append(iron_per)
                    zinc_per_list.append(zinc_per)
                    moly_per_list.append(moly_per)
                    phos_per_list.append(phos_per)
                    sele_per_list.append(sele_per)
                    mang_per_list.append(mang_per)
                    chlo_per_list.append(chlo_per)
                    etc_list.append(etc)
                    detail_images_list.append(detail_images)
            except KeyboardInterrupt:
                print("\t==== ERROR!")
                error.append(href)
            print(f"{n} / {len(urls)}")
            print("=====================")

        ## save to excel
        df = pd.DataFrame()
        df["사진URL"] = image_list
        df["브랜드"] = brand_list
        df["제품명"] = name_list
        df["맛"] = flavor_list
        df["용량"] = volume_list
        df["원료 성분"] = mingrd_list
        df["원료 성분(단어)"] = ingr_words_list
        df["알러지 반응"] = aingrd_list
        df["URL"] = url_list
        df["제품번호"] = pcode_list
        df["가격"] = price_list
        df["품절여부"] = stock_list
        df["1회제공량"] = serv_size_list
        df["상세설명 이미지"] = detail_images_list
        df["총제공량"] = serv_per_cont_list
        df["칼로리(kcal)"] = cal_list
        df["지방 칼로리(kcal)"] = fcal_list
        df["나트륨(mg)"] = sod_list
        df["총 탄수화물(g)"] = tcarb_list
        df["식이섬유(g)"] = dfib_list
        df["당류(g)"] = tsug_list
        df["첨가당(g)"] = asug_list
        df["총 지방(g)"] = tofat_list
        df["불포화지방(g)"] = ufat_list
        df["포화지방(g)"] = sfat_list
        df["트랜스지방(g)"] = tfat_list
        df["콜레스테롤(mg)"] = chol_list
        df["단백질(g)"] = prot_list
        df["비타민 A(mcg RAE)"] = vita_list
        df["비타민 A(%)"] = vita_per_list
        df["비타민 D(mcg)"] = vitd_list
        df["비타민 D(%)"] = vitd_per_list
        df["비타민 E(mg)"] = vite_list
        df["비타민 E(%)"] = vite_per_list
        df["비타민 K(mcg)"] = vitk_list
        df["비타민 K(%)"] = vitk_per_list
        df["비타민 C(mg)"] = vitc_list
        df["비타민 C(%)"] = vitc_per_list
        df["티아민(mg)"] = thim_list
        df["티아민(%)"] = thim_per_list
        df["리보플라빈(mg)"] = ribo_list
        df["리보플라빈(%)"] = ribo_per_list
        df["니아신(mg)"] = niac_list
        df["니아신(%)"] = niac_per_list
        df["비타민 B6(mg)"] = pyrd_list
        df["비타민 B6(%)"] = pyrd_per_list
        df["엽산(mcg)"] = folt_list
        df["엽산(%)"] = folt_per_list
        df["비타민 B12(mcg)"] = coba_list
        df["비타민 B12(%)"] = coba_per_list
        df["판토텐산(mg)"] = pant_list
        df["판토텐산(%)"] = pant_per_list
        df["비오틴(mcg)"] = biot_list
        df["비오틴(%)"] = biot_per_list
        df["요오드(mcg)"] = iodi_list
        df["요오드(%)"] = iodi_per_list
        df["구리(mg)"] = copp_list
        df["구리(%)"] = copp_per_list
        df["불소(mg)"] = fluo_list
        df["불소(%)"] = fluo_per_list
        df["칼슘(mg)"] = calc_list
        df["칼슘(%)"] = calc_per_list
        df["마그네슘(mg)"] = magn_list
        df["마그네슘(%)"] = magn_per_list
        df["칼륨(mg)"] = pota_list
        df["칼륨(%)"] = pota_per_list
        df["크롬(mcg)"] = chro_list
        df["크롬(%)"] = chro_per_list
        df["철분(mg)"] = iron_list
        df["철분(%)"] = iron_per_list
        df["아연(mg)"] = zinc_list
        df["아연(%)"] = zinc_per_list
        df["몰리브덴(mcg)"] = moly_list
        df["몰리브덴(%)"] = moly_per_list
        df["인(mg)"] = phos_list
        df["phos_%"] = phos_per_list
        df["셀레늄(mcg)"] = sele_list
        df["셀레늄(%)"] = sele_per_list
        df["망간(mg)"] = mang_list
        df["망간(%)"] = mang_per_list
        df["염소(mg)"] = chlo_list
        df["염소(%)"] = chlo_per_list
        df["히스티딘(mg)"] = hist_list
        df["이소류신(mg)"] = isol_list
        df["류신(mg)"] = leuc_list
        df["리신(mg)"] = lysi_list
        df["메타오닌(mg)"] = meth_list
        df["페닐알라닌(mg)"] = phen_list
        df["트레오닌(mg)"] = thre_list
        df["트립토판(mg)"] = tryp_list
        df["발린(mg)"] = vali_list
        df["세린(mg)"] = seri_list
        df["알라닌(mg)"] = alan_list
        df["아르기닌(mg)"] = argi_list
        df["아스파라긴(mg)"] = aspa_list
        df["시스테인(mg)"] = cyst_list
        df["글루타민(mg)"] = glut_list
        df["글리신(mg)"] = glyc_list
        df["프롤린(mg)"] = prol_list
        df["티로신(mg)"] = tyro_list
        df["녹차추출물(mg)"] = grnt_list
        df["공액리놀레산(mg)"] = conj_list
        df["가르시니아(mg)"] = garc_list
        df["키토산(mg)"] = chit_list
        df["차전자피(mg)"] = psyl_list
        df["글루코만난(mg)"] = gluc_list
        df["알로에전잎(mg)"] = aloe_list
        df["크레아틴(mg)"] = crea_list
        df["시트룰린(mg)"] = citr_list
        df["아그마틴(mg)"] = agma_list
        df["베타알라닌(mg)"] = beta_list
        df["잔티젠(mg)"] = xant_list
        df["타우린(mg)"] = taur_list
        df["카페인(mg)"] = caff_list
        df["카르니틴(mg)"] = carn_list
        df["기타성분"] = etc_list
        df.to_excel(f"../../data/crawling/{site_name}.xlsx")
        print("total time : ", time.time() - start)
        with open(f"../../data/crawling/result_{site_name}.json", "w", encoding="utf-8-sig") as f:
            json.dump(result, f, ensure_ascii=False)
