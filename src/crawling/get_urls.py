import requests
from bs4 import BeautifulSoup
import pickle, re
from urllib.request import urljoin, build_opener, install_opener, urlretrieve
import json
from wrapt_timeout_decorator import *

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36"
}
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=20)
session.mount("https://", adapter)
session.mount("http://", adapter)
req = session


def get_urls(site_name):
    if site_name == "365Muscle":
        urls = get_urls_365Muscle()
    elif site_name == "iHerb":
        urls = get_urls_iHerb()
    elif site_name == "IronMax":
        urls = get_urls_IronMax()
    elif site_name == "Kingmass":
        urls = get_urls_Kingmass()
    elif site_name == "MonsterMart":
        urls = get_urls_MonsterMart()
    elif site_name == "MyProtein":
        urls = get_urls_MyProtein()
    elif site_name == "Ople":
        urls = get_urls_Ople()
    else:
        urls = get_urls_Coupang()
        # urls += get_options_urls(urls)
    urls = list(dict.fromkeys(urls))
    with open(f"../../data/crawling/urls_{site_name}.pickle", "wb") as f:
        pickle.dump(urls, f)
    return urls


def get_urls_365Muscle():
    # 스포츠 보충제 - 709
    # 호르몬촉진&PCT - 95
    # 다이어트 - 101
    category_codes = ["0001", "0011", "0003"]
    page = 0
    urls = []
    for code in category_codes:
        while True:
            page = page + 1
            url = f"https://365muscle.com/goods/catalog?page={page}&perpage=250&code={code}&popup=&iframe="
            res = req.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            hrefs = [
                i.find("a", {"href": True}).get("onclick")
                for i in soup.find("div", "displayTabContentsContainer").find_all(
                    "li", "goodsDisplayWrap"
                )
                if i.find("a", {"href": True}) is not None
            ]
            hrefs = ["".join(re.findall("\d", u)).strip() for u in hrefs]
            hrefs = [f"https://365muscle.com/goods/view?no={u}" for u in hrefs]
            urls += hrefs
            if not hrefs:
                break
    return urls


def get_urls_IronMax():
    # 프로틴
    # 크레아틴&부스터
    # 아미노산
    # 다이어트
    # 식사대용
    category_codes = ["001", "008", "004", "010", "009"]
    urls = []
    for code in category_codes:
        page = 0
        while True:
            page = page + 1
            ctg = f"http://www.ironmaxx.co.kr/goods/goods_list.php?page={page}&cateCd={code}"
            res = req.get(ctg, headers=headers)
            soup = BeautifulSoup(res.text, "lxml")
            if soup.find("div", {"class", "goods_no_data"}) is not None:
                break
            urls += [
                urljoin(res.url, i.find("div", "item_tit_box").find("a").get("href"))
                for i in soup.find("div", "item_gallery_type").find_all("li")
            ]
    return urls


def get_urls_iHerb():
    urls = []
    page = 0
    while True:
        page = page + 1
        url = f"https://kr.iherb.com/c/Sports-Nutrition?noi=192&p={page}"
        res = req.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "lxml")
        if soup.find("p", {"class": "no-results-found-heading"}) is not None:
            break
        items = soup.find("div", {"class": "products clearfix"}).find_all(
            "div", {"class": "product ga-product"}
        )
        urls += list(
            map(
                lambda x: x.find("div", {"class": "absolute-link-wrapper"})
                .find("a")
                .get("href"),
                items,
            )
        )

    return urls


def get_urls_Kingmass():
    res = req.get(
        "https://kingmassmall.com/product/list.html?cate_no=32", headers=headers
    )
    soup = BeautifulSoup(res.text, "lxml")
    urls = [
        urljoin(res.url, i.find("a").get("href"))
        for i in soup.find("ul", "prdList").find_all("p", "name")
    ]
    return urls


def get_urls_MonsterMart():
    category_name = [
        "supplements",
        "health/diet",
        "health/food-snack",
        "health/organic-vegan",
    ]
    urls = list()
    for category in category_name:
        page = 0
        while True:
            page = page + 1
            url = f"https://www.monstermart.net/{category}/page-{page}/?items_per_page=96&result_ids=pagination_contents&is_ajax=1"
            res = req.get(url, headers=headers)
            if res.status_code == 200:
                try:
                    resj = res.json()
                    html = resj["html"]["pagination_contents"].strip()
                    soup = BeautifulSoup(html, "lxml")
                    href = [
                        u.find("a").get("href")
                        for u in soup.find(
                            "div", {"class": "jq_product_list_grid"}
                        ).find_all("div", {"class": "ty-column3"})
                        if u.find("a") is not None
                    ]
                    urls += href
                except Exception as e:
                    print(url, e)
                    break
            else:
                break
    return urls


def get_urls_MyProtein():
    # 비타민&미네랄, 섬유질&필수지방산, 스포츠 악세사리 제외
    categories = [
        "protein.list",
        "healthy-food-drinks.list",
        "amino-acids.list",
        "creatine.list",
        "weight-management.list",
        "pre-post-workout.list",
        "carbohydrates.list",
    ]
    urls = []
    for ctg in categories:
        page = 0
        while True:
            page = page + 1
            res = req.get(
                f"https://www.myprotein.co.kr/nutrition/{ctg}?pageNumber={page}"
            )
            soup = BeautifulSoup(res.text, "lxml")
            try:
                items = soup.find(
                    "ul", {"class": "productListProducts_products"}
                ).find_all("li", {"class": "productListProducts_product"})
            except AttributeError:
                print(f"\t존재하지않는 페이지")
                break
            href = [
                urljoin(
                    res.url,
                    i.find("a", {"class": "athenaProductBlock_linkImage"}).get("href"),
                )
                for i in items
            ]
            urls += href
    return urls


def get_urls_Ople():
    # 프로틴, 게이너, 아미노산, BCAA, 식사대용, 다이어트
    categories = [70, 71, 72, 73, 74, 75]
    urls = []
    for ctg in categories:
        page = 0
        while True:
            page = page + 1
            url = f"https://www.ople.com/mall5/shop/list.php?ca_id={ctg}&items=100&page={page}"
            print(url)
            res = req.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "lxml")
            if soup.find("div", {"align": "center"}) is not None:
                break
            urls += [
                urljoin(res.url, a.get("href"))
                for a in soup.select("td.item_title > a[href]")
            ]
    return urls


if __name__ == "__main__":
    print(1)
