from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from lxml import etree
import os
import webbrowser

def scrap_data():
    process = CrawlerProcess(get_project_settings())
    process.crawl('stejka')
    process.crawl('mebli')
    process.start()


def task1():
    print("Task #1")
    root = etree.parse("task1.xml")
    pages = root.xpath("//page")
    print("Number of scrapped documents: %s" % len(pages))
    for page in pages:
        url = page.xpath("@url")[0]
        print("%s" % url)


def task2():
    print("Task #2")
    transform = etree.XSLT(etree.parse("templateTask2.xsl"))
    result = transform(etree.parse("task2.xml"))
    result.write("task2.xhtml", pretty_print=True, encoding="UTF-8")
    webbrowser.open('file://' + os.path.realpath("task2.xhtml"))


if __name__ == '__main__':
    scrap_data() # Scrapping data from sites
    while True:
        print("/" * 50)
        print("Input number of task to execute, or anything else to exit:")
        print("1. Task#1: www.stejka.com")
        print("2. Task#2: www.mebli-lviv.com.ua")
        print("> ", end='', flush=True)
        number = input()
        if number == "1":
            task1()
        elif number == "2":
            task2()
        else:
            break
    print("End of program")
