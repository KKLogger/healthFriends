import pickle
from crawling import *
import sys
import pandas as pd

if __name__ == "__main__":

    """
    수집 url load
    """
    urls = list()
    with open("option_urls.pickle", "rb") as f:
        while True:
            try:
                urls += pickle.load(f)
            except Exception as e:
                print(e)
                break

    print(f"total urls : {len(urls)}")

    """
    crawling
    120000부터 시작하시면 됩니다.
    """
    start = 120000
    end = 120010
    for current, url in enumerate(urls[start:end]):
        print(f"current progress {current}/{len(urls)}")
        try:
            temp = basic_crawling(url)
        except Exception as e:
            print(f"[in basic_crawling] : {e}")
            temp = None
        if temp is not None:
            with open("basic_df_dict.pickle", "ab") as f:
                pickle.dump(temp, f)
    # crawling result save to xlsx
    result = list()
    with open("basic_df_dict.pickle", "rb") as f:
        while True:
            try:
                temp = pickle.load(f)
                result.append(temp)
            except:
                break
    result = [x for x in result if x is not None]
    basic_df = pd.DataFrame.from_dict(result)
    basic_df.to_excel(f"result_{start}~{end}.xlsx", engine="xlsxwriter")
