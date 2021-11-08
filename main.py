from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import requests
from bs4 import BeautifulSoup
import fileinput
from itertools import groupby
import os
import re
import sys
import mysql.connector
import pymysql
from getpass import getpass
from mysql.connector import connect, Error
from PyQt5.QtWidgets import (QWidget, QGridLayout,
    QPushButton, QApplication)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

def get_patent_id(path, patents, cpc, source_pages, links, i):
    with open(path) as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    items_divs = soup.find_all("search-result-item", class_ = "style-scope search-results")

    urls =[]
    for item in items_divs:
        item_url = item.find("state-modifier", class_="result-title style-scope search-result-item").get("data-result")
        item_url1 = "https://patents.google.com/" + item_url
        urls.append(item_url1)
    path_txt = "C:\\PythonProjects\\selenium_parser\\" + patents + "\\" + cpc + "\\" + links + "\\" + "link_" + str(i) + ".txt"
    with open(path_txt, "w") as file:
        for url in urls:
            file.write(url+"\n")

def get_patents_html(url, page, patents, cpc, source_pages, links):

    i = 0
    while i < page:
        driver = webdriver.Chrome(executable_path="C:\\PythonProjects\\selenium_parser\\googledriver\\chromedriver.exe")
        driver.maximize_window()
        try:
            driver.get(url=url + str(i))
            time.sleep(10)
            path = "C:\\PythonProjects\\selenium_parser\\" + patents + "\\" + cpc +"\\" + source_pages + "\\source_page_" + str(i) + ".html"
            with open(path, "w", encoding='utf-8') as file:
                file.write(driver.page_source)
            get_patent_id(path, patents, cpc, source_pages, links, i)
            i += 1
        except Exception as _ex:
            print(_ex)
        finally:
            driver.close()
            driver.quit()

def class_loader(cpc, links, patents):
    i = 0
    j = 0
    while i < 20:
        driver = webdriver.Chrome(executable_path="C:\\PythonProjects\\selenium_parser\\googledriver\\chromedriver.exe")
        driver.maximize_window()
        try:
            path = "C:\\PythonProjects\\selenium_parser\\" + patents + "\\" + cpc + "\\" + links + "\\link_" + str(i) + ".txt"
            file1 = open(path, "r")
            lines = file1.readlines()
            for line in lines:
                driver.get(url=line)
                time.sleep(10)
                full_list = driver.find_element_by_xpath("//div[@class='more style-scope classification-viewer']")
                full_list.click()
                time.sleep(5)
                path1 = "C:\\PythonProjects\\selenium_parser\\" + patents + "\\" + cpc + "\\" + patents + "\\patent_" + str(j) + ".html"
                with open(path1, "w", encoding='utf-8') as file:
                    file.write(driver.page_source)
                j+=1
            i+=1
        except Exception as _ex:
            print(_ex)
        finally:
            driver.close()
            driver.quit()

def get_public_as(id_patent, path_pub_as):
    driver = webdriver.Chrome(executable_path="C:\\PythonProjects\\selenium_parser\\googledriver\\chromedriver.exe")
    driver.maximize_window()

    try:
        url = "https://worldwide.espacenet.com/patent/search/family/057994253/publication/" + id_patent + "?q=" + id_patent
        driver.get(url=url)
        time.sleep(20)
        with open(path_pub_as, "w", encoding='utf-8') as file:
            file.write(driver.page_source)
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

    with open(path_pub_as, encoding='utf-8') as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    divs=soup.find_all("div", class_="biblio__info-block--1AuMIzL_")
    spans = divs[6].find("span", id="biblio-also-published-as-content").find_all("a", class_="link--1bxNBund publication-number--AQHrdFQI with-focus--3Oly3pBv")
    other_id_patent_list=[]
    for span in spans:
        other_id_patent = span.find("span").text.strip()
        other_id_patent_list.append(other_id_patent)
    return other_id_patent_list

def parser_loader_new(url,connection):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    try:
        driver.get(url=url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="htmlContent"]')))
        full_list = driver.find_element_by_xpath("//span[@class='style-scope raw-html']")
        full_list.click()

        wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class=\'more style-scope classification-viewer\']')))
        full_list1 = driver.find_element_by_xpath("//div[@class='more style-scope classification-viewer']")
        full_list1.click()

        name_patent = driver.find_element_by_xpath('/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/h1')
        print("[NAME]:" +"\n"+ name_patent.text)

        id_patent = driver.find_element_by_xpath('/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[2]/section/header/h2')
        print("[ID]:" +"\n"+ id_patent.text)

        link_patent = driver.find_element_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[2]/section/header/div/state-modifier[2]/a").get_attribute("href")
        print("[LINK]:" +"\n"+ link_patent)

        status_patent = driver.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/application-timeline/div/div[9]/div[3]/span')
        print("[STATUS]:" +"\n"+ status_patent.text)

        abstract_patent = driver.find_element_by_xpath('//*[@id="text"]/abstract')
        print("[ABSTRACT]:" +"\n"+ abstract_patent.text)

        print("[INVENTORS]:" + "\n")
        i=1
        while True:
            try:
                inventors_patent = driver.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/dl[1]/dd['+str(i)+']/state-modifier')
                print(inventors_patent.text)
                i += 1
            except:
                break

        assignee_patent = driver.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/dl[1]/dd['+str(i)+']')
        with connection.cursor() as cursor:
            '''insert_query = "INSERT INTO `assignees` (Name) VALUES (" +"\'" + assignee_patent.text +"\'" + ");"
            cursor.execute(insert_query)
            connection.commit()'''
            insert_query = "SELECT Name FROM `assignees`"
            cursor.execute(insert_query)
            results = cursor.fetchall()
            for row in results:
                if row["Name"] == 'Toronto-Dominion Bank':
                    print('naiden')
            connection.commit()

        print("[ASSIGNEE]:" +"\n"+ assignee_patent.text)

        print("[CLASSES]:" + "\n")
        i=0
        classes_patent = driver.find_elements_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/div/classification-tree[*]/div/div/div/div[*]/concept-mention/span/state-modifier/a")
        for c in classes_patent:
            if(c.text==""):
                pass
            else:
                print(c.text)
                i+=1
                f = driver.find_elements_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/div/classification-tree[" + str(i) + "]/div/div/div/div[*]/concept-mention/span/span")
                print(f[-1].text)

        description_patent = driver.find_element_by_xpath('//*[@id="description"]').text
        print("[DESCRIPTION]:" + "\n" +description_patent)

        claims_patent = driver.find_element_by_xpath('//*[@id="claims"]/patent-text/div').text
        print("[CLAIMS]:" + "\n" + claims_patent)

        patentCitations = driver.find_element_by_xpath('//*[@id="patentCitations"]').text
        pc_count = re.sub('\D', '', patentCitations)
        print(pc_count)
        i=1
        patent_citations = []
        family_citations = []
        check = True
        while i <= int(pc_count)+1:
            full_info = []
            item1 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[1]/div/div[2]/div[" + str(i) + "]/span[1]").text
            item2 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[1]/div/div[2]/div[" + str(i) + "]/span[2]").text
            item3 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[1]/div/div[2]/div[" + str(i) + "]/span[3]").text
            item4 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[1]/div/div[2]/div[" + str(i) + "]/span[4]").text
            item5 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[1]/div/div[2]/div[" + str(i) + "]/span[5]").text
            if (item1 == "Family To Family Citations"):
                check = False
            if(check):
                full_info.append(item1)
                full_info.append(item2)
                full_info.append(item3)
                full_info.append(item4)
                full_info.append(item5)
                patent_citations.append(full_info)
            else:
                if (item1 == "Family To Family Citations"):
                    pass
                else:
                    full_info.append(item1)
                    full_info.append(item2)
                    full_info.append(item3)
                    full_info.append(item4)
                    full_info.append(item5)
                    family_citations.append(full_info)
            i+=1

        print("[PATENT_CITATIONS]: ")
        for pat in range(len(patent_citations)):
            print(patent_citations[pat][0] + " | " + patent_citations[pat][1] + " | " + patent_citations[pat][2] + " | " + patent_citations[pat][3] + " | " + patent_citations[pat][4])

        print("FAMILY_CITATIONS")
        for pat in range(len(family_citations)):
            print(family_citations[pat][0] + " | " + family_citations[pat][1] + " | " + family_citations[pat][2] + " | " + family_citations[pat][3] + " | " + family_citations[pat][4])

        citedBy = driver.find_element_by_xpath('//*[@id="citedBy"]').text
        cb_count = re.sub('\D', '', citedBy)
        print(cb_count)

        nplCitations = driver.find_element_by_xpath("//*[@id=\"nplCitations\"]").text
        if(nplCitations):
            n = 5
        else:
            n = 3
        i = 1
        patent_cited_by = []
        family_cited_by = []
        check = True
        while i <= int(cb_count)+1:
            full_info=[]
            item1 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div["+str(n)+"]/div/div[2]/div[" + str(i) + "]/span[1]").text
            item2 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div["+str(n)+"]/div/div[2]/div[" + str(i) + "]/span[2]").text
            item3 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div["+str(n)+"]/div/div[2]/div[" + str(i) + "]/span[3]").text
            item4 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div["+str(n)+"]/div/div[2]/div[" + str(i) + "]/span[4]").text
            item5 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div["+str(n)+"]/div/div[2]/div[" + str(i) + "]/span[5]").text
            if (item1 == "Family To Family Citations"):
                check = False
            if(check):
                full_info.append(item1)
                full_info.append(item2)
                full_info.append(item3)
                full_info.append(item4)
                full_info.append(item5)
                patent_cited_by.append(full_info)
            else:
                if (item1 == "Family To Family Citations"):
                    pass
                else:
                    full_info.append(item1)
                    full_info.append(item2)
                    full_info.append(item3)
                    full_info.append(item4)
                    full_info.append(item5)
                    family_cited_by.append(full_info)
            i+=1

        print("[PATENT_CITATIONS]: ")
        for pat in range(len(patent_cited_by)):
            print(patent_cited_by[pat][0] + " | " + patent_cited_by[pat][1] + " | " + patent_cited_by[pat][2] + " | " +
                  patent_cited_by[pat][3] + " | " + patent_cited_by[pat][4])

        print("FAMILY_CITATIONS")
        for pat in range(len(family_cited_by)):
            print(family_cited_by[pat][0] + " | " + family_cited_by[pat][1] + " | " + family_cited_by[pat][2] + " | " +
                  family_cited_by[pat][3] + " | " + family_cited_by[pat][4])

        i = 1
        simular_document = []
        while True:
            full_info = []
            try:
                item1 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[" + str(n+2) + "]/div/div[2]/div[" + str(i) + "]/span[1]").text
                item2 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[" + str(n+2) + "]/div/div[2]/div[" + str(i) + "]/span[2]").text
                item3 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[" + str(n+2) + "]/div/div[2]/div[" + str(i) + "]/span[3]").text
                full_info.append(item1)
                full_info.append(item2)
                full_info.append(item3)
                simular_document.append(full_info)
            except:
                break
            i += 1
        print("DOCUMENTS")
        for pat in range(len(simular_document)):
            print(simular_document[pat][0] + " | " + simular_document[pat][1] + " | " + simular_document[pat][2])
        patent = {'name': name_patent,
        'id': id_patent,
        'link_patent': link_patent,
        'status': status_patent,
        'abstract': abstract_patent,
        'inventors': inventors_patent,
        'assignee': assignee_patent,
        'public_as': public_as,
        'classes': classes_list,
        'claims': claims_patent,
        'description': description_patent,
        'patent_citations': patent_citations,
        'family_citations': family_citations,
        'cited_by_patent': patent_cited_by,
        'cited_by_family': family_cited_by,
        'documents': simular_document}



    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()


def parser_loader(count, url, path):
    driver = webdriver.Chrome(executable_path="C:\\PythonProjects\\selenium_parser\\googledriver\\chromedriver.exe")
    driver.maximize_window()
    i = 0
    try:
        driver.get(url=url)
        time.sleep(10)
        full_list = driver.find_element_by_xpath("//span[@class='style-scope raw-html']")
        full_list.click()
        time.sleep(5)
        while i < int(count):
            path_record = path + "\\patents_num_"+str(i)+".html"
            with open(path_record, "w", encoding='utf-8') as file:
                file.write(driver.page_source)
            full_list1 = driver.find_element_by_xpath("//iron-icon[@icon='chevron-right']")
            full_list1.click()
            i+=1
            time.sleep(10)
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()
def get_count_patents(url):
    driver = webdriver.Chrome(executable_path="C:\\PythonProjects\\selenium_parser\\googledriver\\chromedriver.exe")
    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(5)

        full_list = driver.find_element_by_xpath('//*[@id="count"]/div[1]/span[1]/span[3]')
        return full_list.text

    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()


def main():

    print("-------------------------------+")
    print("| ВЫБЕРИТЕ ФУНКЦИЮ             |")
    print("+------------------------------+")
    print("| 1) ПАРСИНГ ПАТЕНТОВ          |\n" +
          "| 2) ...                       |\n" +
          "| 3) ...                       |\n" +
          "| 4) ...                       |\n" +
          "| 5) ...                       |")
    print("+------------------------------+\n")

    cpc = "H04N5"
    priority = "low"
    country = "US"
    date_before = "20200909"
    date_after = "20150101"
    status = "GRANT"
    lang = "ENGLISH"
    type_ = "PATENT"
    url = "https://patents.google.com/?q=CPC%3d" + cpc \
          + "%2f" + priority \
          + "&country=" + country \
          + "&before=priority:" + date_before \
          + "&after=priority:" + date_after \
          + "&status=" + status \
          + "&language=" + lang \
          + "&type=" + type_
    try:
        connection = pymysql.connect(
            host="localhost",
            port = 3306,
            user="monty",
            password="some_pass",
            database="Patents",
            cursorclass=pymysql.cursors.DictCursor
        )
        print("connection")
    except Exception as ex:
        print("not connection")
        print(ex)

    while True:
        print("ВВЕДИТЕ НОМЕР: ", end='')
        num = input()

        print("ВЫБРАНА ФУНКЦИЯ: ", end='')
        if num == "1":
            print("УЗНАТЬ КОЛИЧЕСТВО ПАТЕНТОВ")
            count_patent=get_count_patents(url=url)
            count_patent = str(count_patent).replace(",", "")
            print("КОЛИЧЕСТВО ПАТЕНТОВ: " + str(count_patent))
        elif num == "2":
            print("ПАРСИНГ ПАТЕНТОВ")
            while True:
                print("ВВЕДИТЕ КОЛИЧЕСТВО ПАТЕНТОВ: ", end='')
                count = input()
                if(int(count) > int(count_patent)):
                    print("НЕВЕРНОЕ УСЛОВИЕ")
                else:
                    break
            print("КОЛИЧЕСТВО ПАТЕНТОВ: " + count)
            parser_loader(count = count, url = url, path = path_html)

        elif num == "3":
            i=0
            print("ЗАПИСЬ ИНФОРМАЦИИ В БД")
            print("ВВЕДИТЕ КОЛИЧЕСТВО ПАТЕНТОВ: ", end='')
            count = input()
            patent = {}
            while i < int(count):
                path_read = path_html + "\\patents_num_"+str(i)+".html"
                path_desc = path_patents + "\\temp_desc.txt"
                path_pub_as = path_patents + "\\temp_public_as.html"
                path_write = path_info + "\\info_num_"+str(i)+".txt"
                patent = get_info_patent(path_read=path_read,path_desc = path_desc, path_write = path_write, path_pub_as = path_pub_as)
                #print(patent["inventors"][0])
                i+=1
        elif num == "4":
            print("НОВЫЙ ПАРСИНГ ПАТЕНТОВ")
            parser_loader_new(url = url,connection=connection)
        else:
            print("НЕИЗВЕСТНО")
    '''try:
        connection = pymysql.connect(
            host="localhost",
            port = 3306,
            user="monty",
            password="some_pass",
            database="Patents",
            cursorclass=pymysql.cursors.DictCursor
        )
        print("connection")
    except Exception as ex:
        print("not connection")
        print(ex)
    try:
        with connection.cursor() as cursor:
            insert_query = "INSERT INTO `patents` (title, id_patent, status, abstract, link, description, public_as, claims) VALUES ('hh','hh','hh','hh','hh','hh','hh','hh');"
            cursor.execute(insert_query)
            connection.commit()'''
    '''finally:
        connection.close()'''

    '''listA = [3,45,23,7]
    d = {'dict': listA, 'dictionary': 2}
    print(d)'''
if __name__ == "__main__":
    main()