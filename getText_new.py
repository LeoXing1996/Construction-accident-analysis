import re
import os
import requests
# from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

isJan = 0
isOth = 1
isDec = 2

class getText:

    def __init__(self, url, folder=None):
        self.urlBase = url
        self.driver = None
        self.SUMMARY = []
        self.ACCIDENT = []
        self.status = None # 保存是否正常启动

        if folder is None:
            self.folderSum = 'text/Summary/'
            self.folderAcc = 'text/Accident/'
        else :
            self.folderSum, self.folderAcc = folder

    def __setup(self):
        # todo 鉴于住建部网站时常 gg 增设网站监测与自动退出机制 防止报错
        url = self.urlBase + 'index.html'
        print('启动中，请稍后......')

        if self.driver is None:
            self.driver = webdriver.Chrome()
        self.driver.get(url)
        sleep(3)

    def __makedir(self):
        if os.path.exists(self.folderAcc) == False:
            os.makedirs(self.folderAcc)
        if os.path.exists(self.folderSum) == False:
            os.makedirs(self.folderSum)

    def __isSummary(self, title):

        return [False, True][title[0].isdigit()]

    def __getTotalPages(self):

        # re.sub(pattern, repl, string, count=0, flags=0)
        # 在字符串 string 中找到匹配正则表达式 pattern 的所有子串，
        # 用另一个字符串 repl 进行替换。如果没有找到匹配 pattern 的串，
        # 则返回未被修改的 string。Repl 既可以是字符串也可以是一个函数。

        totalPages = self.driver.find_elements_by_tag_name('span')[3]
        return int(re.sub('\D', '', totalPages.text))

    def __getInfo(self):

        target = self.driver.find_elements_by_tag_name('table')[3]
        target = target.find_elements_by_tag_name('table')[-1]
        tar_url = target.find_elements_by_tag_name('a')

        for title in tar_url:
            title_text = title.text
            title_url = title.get_property('href')
            if self.__isSummary(title_text):
                self.SUMMARY.append([title_text, title_url])
                print('SUMMARY:', title_text, title_url)
            else:
                self.ACCIDENT.append([title_text, title_url])
                print('ACCIDENT:', title_text, title_url)

    def __getAccessory(self):
        xpath_arr = [
            '/html/body/table/tbody/tr[2]/td/table[2]/tbody[2]/tr[2]/td/table/tbody/tr[8]/td/table/tbody/tr/td/div[2]/table/tbody/tr[1]/td[2]/a',
            '/html/body/table/tbody/tr[2]/td/table[2]/tbody[2]/tr[2]/td/table/tbody/tr[8]/td/table/tbody/tr/td/div[2]/table/tbody/tr[2]/td[2]/a',
            '/html/body/table/tbody/tr[2]/td/table[2]/tbody[2]/tr[2]/td/table/tbody/tr[8]/td/table/tbody/tr/td/div[2]/table/tbody/tr[3]/td[2]/a'
        ]

        for xpath in xpath_arr:

            try:
                accessory = self.driver.find_element_by_xpath(xpath)
                xlsURL = accessory.get_property('href')
                xlsNAME = accessory.text
            except:
                continue

            print('     开始下载 《%s》 ' % xlsNAME, end='')
            r = requests.get(xlsURL)

            for errTimes in range(3):
                print('正在尝试第 %d \\3 次...' % (errTimes + 1), end='')
                if r.status_code == 200:
                    print('下载成功! ')
                    break
                else:
                    r = requests.get(xlsURL)
            if r.status_code == 200:
                with open(self.folderSum + xlsNAME + '.xls', 'wb') as xls:
                    xls.write(r.content)
            else:
                print('\n     下载失败, 请查看日志')
                with open('failLog.txt', 'a') as log:
                    log.write(xlsNAME + '    ' + xlsURL)

    def __getSummaryContent(self, tarPath):
        #  获取 Summary 形式的所有文本

        par = self.driver.find_elements_by_tag_name('p')
        with open(tarPath, 'w', encoding='utf-8') as file:
            for p in par[1:]:
                t_text = p.text.strip()
                if t_text.split('：') == '附件':
                    break
                else:
                    file.write(p.text + '\n')
        print('     文本已保存到 %s' % tarPath)

    def __getSummary(self):
        print('开始保存统计数据')
        monthPattern = re.compile(r'\d+年\d+月')
        yearPattern = re.compile(r'\d+年.*年')
        quarterPattern = re.compile(r'\d+年.*季度')
        patterns = [monthPattern, yearPattern, quarterPattern]

        count = 1
        for title, url in self.SUMMARY:
            print('正在保存第 %d/%d 组.....' % (count, len(self.SUMMARY)))
            fileName = str(count)
            for p in patterns:
                res = p.search(title)
                if res is not None:
                    fileName = res.group()
                    break

            tarPath = self.folderSum + fileName + '.txt'
            self.driver.get(url)
            self.__getSummaryContent(tarPath)
            self.__getAccessory()
            count += 1
            sleep(1)

    def __getAccident(self):

        print('开始事故数据保存')

        count = 1
        for title, url in self.ACCIDENT:
            print('正在保存第 %d/%d 条《%s》.....' % (count, len(self.ACCIDENT), title), end='')

            self.driver.get(url)
            text = self.driver.find_elements_by_tag_name('p')[1:]
            tarPath = self.folderAcc + str(count) + '.txt'
            with open(tarPath, 'w', encoding='utf-8') as file:
                for t in text:
                    file.write(t.text + '\n')
            count += 1
            print('已保存到 %d.txt' % count)
            sleep(1)

        print('\n事故文本保存完成')

    def downloadText(self):
        # todo 从文件中加载 以及 断线重下
        self.__setup()
        totalPages = self.__getTotalPages()

        for p in range(totalPages):

            print('正在获取第 ',p+1 , ' 页: ')
            self.__getInfo()

            url = self.urlBase + 'index_' + str(p+2) + '.html'
            self.driver.get(url)
            sleep(0.5)
        print('获取完毕!    共获取：')
        print('     事故数据：%d' % len(self.ACCIDENT))
        print('     统计数据：%d' % len(self.SUMMARY))

        with open('ACC.txt','w', encoding='utf-8') as file:
            for text, url in self.ACCIDENT:
                file.write(text + '     ' + url)
        with open('SUM.txt','w', encoding='utf-8') as file:
            for text, url in self.SUMMARY:
                file.write(text + '     ' + url)

    def saveText(self):

        if self.SUMMARY == [] and self.ACCIDENT == []:
            return

        print('开始保存')
        self.__makedir()
        self.__getAccident()
        self.__getSummary()
        print('保存完毕')
        self.driver.close()

if __name__ == '__main__':
    url = 'http://www.mohurd.gov.cn/zlaq/cftb/zfhcxjsbcftb/'
    textSpider = getText(url)
    textSpider.downloadText()
    textSpider.saveText()