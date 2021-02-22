import pickle
from crawling import *
import sys
import pandas as pd

if __name__ == "__main__":

    """
    수집 url load
    """
    urls = list()
    with open("../../data/coupang/option_urls.pickle", "rb") as f:
        while True:
            try:
                urls += pickle.load(f)
            except Exception as e:
                print(e)
                break
    # 이미 수집된 df 를 가지고 url 불러오기
    # df = pd.read_excel('../data/url.xlsx')
    # urls = df['URL']
    # urls = list(set(urls))

    print(f"total urls : {len(urls)}")

    """
    crawling
    """
    for current, url in enumerate(urls[112900:]):
        print(f"current progress {current}/{len(urls)}")
        try:
            temp = basic_crawling(url)
        except Exception as e:
            print(f"[in basic_crawling] : {e}")
            temp = None
        if temp is not None:
            with open("../../data/coupang/basic_df_dict.pickle", "ab") as f:
                pickle.dump(temp, f)
    """
    df 에서 url로 중복제거가 필요
    """
    ## crawling result save to xlsx
    # result = list()
    # with open("../data/basic_df_dict.pickle", "rb") as f:
    #     while True:
    #         try:
    #             temp = pickle.load(f)
    #             result.append(temp)
    #         except:
    #             break
    # result = [x for x in result if x is not None]
    # basic_df = pd.DataFrame.from_dict(result)
    # basic_df.to_excel("../data/fin_result.xlsx", engine="xlsxwriter")
