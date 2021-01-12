import urllib.request
import time

opener = urllib.request.build_opener()
opener.addheaders = [
    (
        "User-Agent",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36",
    )
]
urllib.request.install_opener(opener)


def save_image(site_name, urls, num):
    if urls == "":
        return
    urls = urls.split("|")
    for n, url in enumerate(urls):
        try:
            time.sleep(0.2)
            urllib.request.urlretrieve(url, f"image/{site_name}/{num}_{n}.jpg")
        except Exception as e:
            print("error in save_image :", e)
            pass
