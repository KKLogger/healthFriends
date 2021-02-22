import requests
from bs4 import BeautifulSoup
import pandas
import re
import pickle

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
}


def get_proxy_list():
    url = "http://spys.one/en/free-proxy-list/"
    data = {"xpp": "1", "xf1": "0", "xf2": "0", "xf4": "0", "xf5": "2"}
    res = requests.post(url, headers=headers, data=data)
    soup = BeautifulSoup(res.content, "html.parser")
    result = list()

    ports = dict()
    script = soup.select_one("body > script")
    for row in script.text.split(";"):
        if "^" in row:
            line = row.split("=")
            ports[line[0]] = line[1].split("^")[0]

    trs = soup.select("tr[onmouseover]")
    for tr in trs:
        print(tr)
        input()
        e_ip = tr.select_one("font.spy14")
        ip = ""
        proxy_type = tr.select_one("font.spy1")
        print(proxy_type.text)
        e_port = tr.select_one("script")
        port = ""
        if e_port is not None:
            re_port = re.compile(r"\(([a-zA-Z0-9]+)\^[a-zA-Z0-9]+\)")
            match = re_port.findall(e_port.text)
            for item in match:
                port = port + ports[item]
        else:
            print("e_port is None")
            continue

        if e_ip is not None:
            for item in e_ip.findAll("script"):
                item.extract()
            ip = e_ip.text
        else:
            print("e_ip is None")
            continue

        # tds = tr.select("td")
        # is_skip = False
        # for td in tds:
        #     e_pct = td.select_one("font > acronym")
        #     if e_pct is not None:
        #         pct = re.sub("([0-9]+)%.*", r"`\1", e_pct.text)
        #         if not pct.isdigit():
        #             is_skip = True
        #     else:
        #         print('e_pct is None')
        #         continue
        # if is_skip:
        #     continue
        result.append({proxy_type: ip + ":" + port})
    return result

