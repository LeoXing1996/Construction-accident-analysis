import re
# import requests
# from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep



class getText:
    # 已经阵亡 url 无法正常访问了
    # 嘤嘤嘤
    def __init__(self, url, keyWord, folder=None):
        self.url = url
        self.pattern = re.compile(keyWord)
        self.summary = []
        self.driver = None
        if folder is None:
            self.folder = 'text/'

    def __setup(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)
        sleep(3)

    def __containKeyWord(self, text):
        res = self.pattern.search(text)
        if res is None:
            return False
        else:
            return True

    def __getInfo(self, acc_summary):

        info_table = self.driver.find_elements_by_tag_name('tr')[9:]

        for info in info_table:
            info_text = info.text
            try:
                if info_text.split()[0].isdigit():
                    if self.__containKeyWord(info_text):
                        info_url = info.find_element_by_tag_name('a').get_property('href')
                        acc_summary.append([
                            info_text.split()[1],
                            info_url
                        ])
            except:
                pass

    def downloadSummary(self):
        self.__setup()
        nextPageButton = self.driver.find_element_by_id('ctl00_lbtPageDown')
        scroll_js = "window.scrollTo(0,1000)"

        pages = 1
        # count = 5

        while nextPageButton.get_property('href') != '':
        # while count>0 :
            print('正在获取第 %d 页' % pages)
            pages += 1

            self.__getInfo(self.summary)
            self.driver.execute_script(scroll_js)
            sleep(1)

            nextPageButton.click()
            nextPageButton = self.driver.find_element_by_id('ctl00_lbtPageDown')
            # count -= 1

        print('获取完毕')

    def saveText(self):

        print('===========================================')
        print('开始保存')

        count = 1
        for sum in self.summary:
            url = sum[1]
            self.driver.get(url)
            text = self.driver.find_elements_by_tag_name('p')[1:]
            tarPath = self.folder + str(count) + '.txt'
            with open(tarPath, 'w', encoding='utf-8') as file:
                for t in text:
                    # if t.text == '':
                    #     pass
                    # else:
                    file.write(t.text + '\n')
            count += 1

        self.driver.close()
        print('保存完毕')

if __name__ == '__main__':

    url = 'http://ginfo.mohurd.gov.cn/'
    keyWord = '事故'
    spider = getText(url, keyWord)
    spider.downloadSummary()
    spider.saveText()
