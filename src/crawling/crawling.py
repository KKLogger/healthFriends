import requests
from urllib.request import urljoin, build_opener, install_opener, urlretrieve
from crawling_365Muscle import crawling_365Muscle
from crawling_IronMax import crawling_IronMax
from crawling_iHerb import crawling_iHerb
from crawling_Kingmass import crawling_Kingmass
from crawling_MonsterMart import crawling_MonsterMart
from crawling_MyProtein import crawling_MyProtein
from crawling_Ople import crawling_Ople
from bs4 import BeautifulSoup
"""
.py import 경로 설정
"""
sys.path.append('../common')
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


def crawling(site_name, href, num, f_num):
    if site_name == "365Muscle":
        return crawling_365Muscle(site_name, href, num, f_num)
    elif site_name == "IronMax":
        return crawling_IronMax(site_name, href, num, f_num)
    elif site_name == "iHerb":
        return crawling_iHerb(site_name, href, num)
    elif site_name == "Kingmass":
        return crawling_Kingmass(site_name, href, num, f_num)
    elif site_name == "MonsterMart":
        return crawling_MonsterMart(site_name, href, num, f_num)
    elif site_name == "MyProtein":
        return crawling_MyProtein(site_name, href, num, f_num)
    else:
        return crawling_Ople(site_name, href, num)


def calculate_flavor(url, site_name):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
    }
    soup = BeautifulSoup(requests.get(url, headers=headers).text, "lxml")
    try:
        if site_name == "MonsterMart":
            if soup.find_all("td", {"class": "label_flavor"}) is None:
                result = len(
                    [
                        x.strip().replace("\xa0", "")
                        for x in soup.find("select").text.strip().split("\n")
                        if x.strip() != ""
                        and x.strip() != "옵션"
                        and x.strip() != "Flavor"
                    ]
                )
            else:
                result = len(soup.find_all("table", {"id": "label_outer_table"}))
        elif site_name == "365Muscle":
            result = len(
                [
                    x
                    for x in soup.find("table", "goods_option_table")
                    .find("select")
                    .find_all("option")
                    if x.get("value") != ""
                ]
            )
        elif site_name == "IronMax":
            result = len(
                [
                    x.text.strip().replace("\n", "").replace("\r", "")
                    for x in soup.find("div", "item_add_option_box")
                    .find("select")
                    .find_all("option")
                    if x.get("value")
                ]
            )
        elif site_name == "Kingmass":
            result = len(
                [
                    x.text.strip()
                    for x in soup.find("tbody", "xans-product-option")
                    .find("select")
                    .find_all("option")
                    if "*" not in x.get("value")
                ]
            )
        else:
            result = len(
                [
                    x.text
                    for x in soup.find_all(
                        "div", {"class": "productDescription_synopsisContent"}
                    )[-2].find_all("p")
                    if ":" in x.text
                ]
            )
    except:
        result = 1

    return result
