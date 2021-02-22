import requests
from bs4 import BeautifulSoup
import pickle, re
from urllib.request import urljoin, build_opener, install_opener, urlretrieve
import json
from wrapt_timeout_decorator import *

"""
requests setting 
"""
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36"
}
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=20)
session.mount("https://", adapter)
session.mount("http://", adapter)
req = session


def get_urls(option):
    if option == 1:
        urls = get_product_urls()
    else:
        with open("../../data/coupang/product_urls.pickle", "rb") as f:
            urls = pickle.load(f)
    for current, url in enumerate(urls[:]):
        try:
            print(f"{current}/{len(urls)}")
            get_options_urls(url)
        except:
            print("time over")

    result = list()
    with open("../../data/coupang/option_urls.pickle", "rb") as f:
        while True:
            try:
                result += pickle.load(f)
            except Exception as e:
                print(e)
                break
    return result


@timeout(5)
def get_options_urls(url):
    res = req.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")
    if "본 상품은 만 19세 미만의 청소년이 이용할 수 없습니다." in soup.text:
        print("19세 미만 금지")
        return None
    script = [str(i) for i in soup.select("script") if "exports.sdp" in str(i)][0]
    script = [i for i in script.split(";\n")][0].split("exports.sdp =")[1].strip()
    script_dict = json.loads(script)
    if script_dict["options"] is not None:
        extra_options = script_dict["options"]["attributeVendorItemMap"]
        extra_options = [extra_options[j]["vendorItemId"] for j in extra_options]
    else:
        extra_options = [script_dict["vendorItemId"]]
    url_base = url.split("?")[0]
    url_params = url.split("?")[1]
    result = [
        f"{url_base}?{'&'.join([x for x in url_params.split('&') if 'vendorItemId' not in x])}&vendorItemId={extra_option}"
        for extra_option in extra_options
    ]
    with open("../../data/coupang/option_urls.pickle", "ab") as f:
        pickle.dump(result, f)


def get_product_urls():
    params = {
        "listSize": 120,
        "isPriceRange": "false",
        "page": 1,
        "channel": "user",
        "fromComponent": "Y",
        "sorter": "",
        "component": "",
        "rating": 0,
    }
    categories = {
        # 프로틴
        "310724": "복합프로틴파우더",
        "310725": "WPI분리유청",
        "310726": "체중증가용게이너",
        "310727": "느린흡수용카제인",
        "310728": "소고기대두기타",
        "310729": "프로틴바",
        "310730": "프로틴드링크RTD",
        # 크레아틴
        "310731": "크레아틴",
        # 아미노산
        "310733": "복합아미노산",
        "310734": "BCAA",
        "310735": "L아르기닌",
        "310736": "L카르니틴",
        "310737": "L오르니틴",
        "310738": "L글루타민",
        "310739": "L시스테인",
        "310740": "L테아닌",
        "310741": "L라이신",
        "310742": "타우린",
        "310743": "기타아미노산",
        # 기타헬스보조제
        "310744": "기타헬스보조제",
        # 탄수화물 차단제
        "310747": "가르시니아",
        # 체지방 감소제
        "310751": "CLA공액리놀레산",
        "310752": "키토산",
        # 다이어트 쉐이크
        "310759": "다이어트쉐이크",
        # 기타 다이어트 식품
        "310760": "기타다이어트식품",
    }
    order_standards = [
        "bestAsc",
        "salePriceAsc",
        "salePriceDesc",
        "saleCountDesc",
        "latestAsc",
    ]

    result = list()
    for category in categories:
        print(f"카테고리 : {categories[category]}({category})")
        for standard in order_standards:
            print(f"\t정렬기준 : {standard}")
            for page in range(1, 11):
                params["component"] = category  # 카테고리 번호
                params["sorter"] = standard  # 정렬 기준
                params["page"] = page  # 페이지
                url = f"https://www.coupang.com/np/categories/{category}"
                res = req.get(url, headers=headers, params=params)
                print(res.status_code, url)
                soup = BeautifulSoup(res.text, "lxml")
                items = soup.find_all("li", {"class": "baby-product"})
                urls = [
                    urljoin(
                        res.url, l.find("a", {"class": "baby-product-link"}).get("href")
                    )
                    for l in items
                ]
                print(f"\t\tURL 개수 : {len(urls)}")
                result += urls
    result = list(set(result))
    with open(f"../../data/coupang/product_urls.pickle", "wb") as f:
        pickle.dump(result, f)
    return result


if __name__ == "__main__":
    print(len(get_urls(0)))
