import requests
from bs4 import BeautifulSoup
from urllib.request import urljoin, build_opener, install_opener, urlretrieve
import re
import pandas as pd
import pickle
from wrapt_timeout_decorator import *
import urllib
import time
import sys
#
# """
# .py import 경로 설정
# """
# sys.path.append("../common")
from preprocessing import *


headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
}
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=20)
session.mount("https://", adapter)
session.mount("http://", adapter)
req = session
ingr_list = get_ingredient_list()


@timeout(6)
def basic_crawling(url):

    result = dict()
    if "&vendorItemId=None" in url:
        url = url.split("?")[0]
    print(f"current url {url}")
    res = req.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    print("=================================================")
    if "현재 판매 중인 상품이 아닙니다." in soup.text:
        return None
    if "본 상품은 만 19세 미만의 청소년이 이용할 수 없습니다." in soup.text:
        return None

    # 제품 사진
    result["사진URL"] = urljoin(
        res.url, soup.find("img", {"class": "prod-image__detail"}).get("src")
    )
    # print(f"제품 사진 : {image}")

    # 브랜드
    result["브랜드"] = soup.find("a", {"class": "prod-brand-name"}).get("data-brand-name")
    # print(f"브랜드 : {brand}")

    # 제품명
    result["제품명"] = soup.find("h2", {"class": "prod-buy-header__title"}).text.strip()
    # print(f"제품명 : {title}")

    # <옵션> : 맛, 용량
    options = soup.find_all("div", {"class": "prod-option__item"})
    option_dict = dict()
    for option in options:
        key = option.find("span", {"class": "title"}).text.strip()
        value = option.find("span", {"class": "value"}).text.strip()
        option_dict[key] = value
    # option = {o.find('span', {'class': 'title'}).text.strip(): o.find('span', {'class': 'value'}).text.strip()
    #           for o in soup.find_all('div', {'class': 'prod-option__item'})}
    # print(f"옵션 : {option}")

    # 맛
    try:
        result["맛"] = option_dict["맛"]
    except:
        result["맛"] = None
    # print(f"맛 : {taste}")

    # 용량
    # option_dict key 값에 조건문에 해당 하는 문자가 있으면, 선택,다수이면 그중 첫번째
    try:
        result["용량"] = option_dict[
            [
                o
                for o in option_dict
                if "용량" in o
                or "중량" in o
                or "정" in o
                or "개당" in o
                or "분량" in o
                or "수량선택" in o
            ][0]
        ]
    except:
        result["용량"] = None
    # print(f"용량 : {volume}")

    # 가격
    stock_flag = False
    try:
        result["가격"] = soup.find("span", {"class": "total-price"}).text.strip()
    except AttributeError:
        if (
            soup.find("div", {"class": "prod-not-find-known__buy__button"}).text.strip()
            == "품절"
        ):
            stock_flag = True
            result["가격"] = None
        else:
            raise KeyboardInterrupt
    # print(f"가격 : {price}")

    # 품절여부
    if not stock_flag:
        result["품절여부"] = (
            True if soup.find("div", {"class": "oos-label"}) is not None else False
        )
    else:
        result["품절여부"] = True
    # print(f"품절여부 : {isOutOfStock}")

    # 상품번호
    try:
        pcode = (
            [
                l.text
                for l in soup.find_all("li", {"class": "prod-attr-item"})
                if "상품번호" in l.text
            ][0]
            .split(":")[-1]
            .strip()
        )
    except:
        code_product = res.url.split("?")[0].split("/")[-1]
        code_item = [
            r.split("=")[-1] for r in res.url.split("?")[1].split("&") if "itemId" in r
        ][0]
        pcode = f"{code_product} - {code_item}"
    # print(f"상품번호 : {pcode}")
    result["상품번호"] = pcode
    # URL (파트너스) -> 보류
    result["URL"] = res.url
    # print(f"URL : {prod_url}")

    # <본문 이미지> : 원료성분, 알러지반응, 영양성분
    code_product = pcode.split("-")[0].strip()
    code_item = pcode.split("-")[1].strip()
    try:
        code_vendor = [
            r.split("=")[-1] for r in res.url.split("&") if "vendorItemId" in r
        ][0]
    except IndexError:
        print(f"\tVendorError 후속처리")
        error_urls.append(u)
        return None
    res_inner = req.get(
        f"https://www.coupang.com/vp/products/{code_product}/items/{code_item}/vendoritems/{code_vendor}",
        headers=headers,
    )
    res_inner.encoding = "utf-8"
    rjson = res_inner.json()
    # detail_images = [urljoin(res.url, d['vendorItemContentDescriptions'][0]['content']) for d in rjson['details'] \
    #      if d['vendorItemContentDescriptions'][0]['detailType'] == 'IMAGE']

    # 원재료명_텍스트
    ingr_text = "/".join(
        [
            r["description"]
            for r in rjson["essentials"]
            if "원재료명" in r["title"] or "내용물" in r["title"]
        ]
    )
    """
    상세 설명 참조 와 같은 단어에서 '조'라는 단어가 포함됨
    """
    # ingr_text = remove_part(ingr_text).strip()
    ingr_words = substract_ingredient(ingr_text, ingr_list)
    result["원료 성분"] = ingr_text
    # print(f"원재료명(텍스트) : {ingr_text}")
    if len(ingr_words) == 0:
        result["원료 성분(단어)"] = None
    if len(ingr_words) <= 2 and "조" in ingr_words:
        result["원료 성분(단어)"] = None
    else:
        result["원료 성분(단어)"] = ingr_words
    """
    위의 '조' 성분 포함 문제 해결을 위한 테스트
    '조'만 포함 된 성분만 따로 저장 
     - 해결 1. 성분에 '조' 하나만 들어 있는 성분은 None 처리
    data/backup 에 넣어둠 
    """
    # 영양성분_텍스트
    nutri_text = "/".join(
        [
            r["description"]
            for r in rjson["essentials"]
            if "영양성분" in r["title"] or "영양정보" in r["title"]
        ]
    )
    result["영양정보"] = nutri_text
    result["단백질(g)"] = substract_word(nutri_text, "단백질", "g")
    result["총 탄수화물(g)"] = substract_word(nutri_text, "탄수화물", "g")
    # print(f"영양성분(텍스트) : {nutri_text}")

    detail_images = []
    pre_dimages = [
        d["vendorItemContentDescriptions"][0]["content"] for d in rjson["details"]
    ]
    for pi in pre_dimages:
        if "<img src=" in pi:
            psoup = BeautifulSoup(pi, "lxml")
            detail_images += [i.get("src") for i in psoup.find_all("img")]
        elif ".jpg" in pi.lower() or ".png" in pi.lower() or ".gif" in pi.lower():
            detail_images.append(urljoin(res.url, pi))
    result["상세설명 이미지"] = detail_images
    # print(f"상세 이미지 : {detail_images}")
    # 원료성분
    # 알러지 반응
    # 영양성분

    return result
