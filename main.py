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
def get_info_patent(path_read,path_desc,path_pub_as,path_write):
    with open(path_read, encoding='utf-8') as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")

    #ПРОВЕРКА СТАТУСА доделать
    status_items = soup.find("div", class_="wrap style-scope application-timeline").find_all("div", class_="event layout horizontal style-scope application-timeline")
    for item in status_items:
        status_text = item.find("div", class_="legal-status style-scope application-timeline")
        if(status_text):
            status_patent = item.find("span", class_="title-text style-scope application-timeline").get_text()
            if(status_patent !="Active"):
                print("ИСКЛЮЧЕНИЕ: СТАТУС ПАТЕНТА НЕ АКТИВЕН" )
                return
            break

    #ОТКРЫТЬ ФАЙЛ С ПАТЕНТОМ
    f = open(path_write, 'w', encoding='utf-8')

    #ИМЯ ПАТЕНТА
    name_patent = soup.find("h1", id = "title").text.strip()
    #ЗАПИСЬ ИМЕНИ ПАТЕНТА В ФАЙЛ
    f.write("[NAME]:" + '\n' + name_patent + '\n')
    #ВЫВОД ИМЕНИ ПАТЕНТА
    print("[NAME]:" + '\n' + name_patent)

    #ID ПАТЕНТА
    id_patent = soup.find("div", class_ = "flex-2 style-scope patent-result").find("h2", id = "pubnum").get_text()
    #ЗАПИСЬ ID ПАТЕНТА В ФАЙЛ
    f.write("[ID]:" + '\n' + id_patent + '\n')
    #ВЫВОД ID ПАТЕНТА
    print("[ID]:" + '\n' + id_patent)

    link_patent = "https://patents.google.com/patent/" + id_patent +"/en"
    #ЗАПИСЬ ССЫЛКИ ПАТЕНТА В ФАЙЛ
    f.write("[LINK]:" + '\n' + link_patent +'\n')
    #ВЫВОД ССЫЛКИ ПАТЕНТА(!!!)
    print("[LINK]:" + '\n' + link_patent)

    # PUBLIC AS ПАТЕНТА доделать
    public_as = ", ".join(get_public_as(id_patent = id_patent, path_pub_as = path_pub_as))
    f.write("[PUBLIC_AS]:" + '\n' + public_as + '\n')
    #ВЫВОД СТАТУСА ПАТЕНТА
    print("[PUBLIC_AS]:" + '\n' + public_as)

    #ЗАПИСЬ СТАТУСА ПАТЕНТА В ФАЙЛ
    f.write("[STATUS]:" + '\n' + status_patent + '\n')
    #ВЫВОД СТАТУСА ПАТЕНТА
    print("[STATUS]:" + '\n' + status_patent)


    #АБСТРАКТ ПАТЕНТА
    abstract_patent = soup.find("div", class_="layout horizontal style-scope patent-text").find("div", class_ = "abstract style-scope patent-text").text.strip()
    #ЗАПИСЬ АБСТРАКТА ПАТЕНТА В ФАЙЛ
    f.write("[ABSTRACT]:" + '\n' + abstract_patent + '\n')
    #ВЫВОД АБСТРАКТА ПАТЕНТА
    print("[ABSTRACT]:" + '\n' + abstract_patent)

    #ИЗОБРИТАТЕЛИ ПАТЕНТА
    inventors_patent = soup.find("dl", class_="important-people style-scope patent-result").find_all("state-modifier", class_="style-scope patent-result")
    inventors = []
    for inventor in inventors_patent:
        inventors.append(inventor.find("a", id="link").get_text())
    inventors_list = ", ".join(inventors)
    #ЗАПИСЬ ИЗОБРИТАТЕЛЕЙ ПАТЕНТА В ФАЙЛ
    f.write("[INVENTORS]:" + '\n' + inventors_list + '\n')
    #ВЫВОД ИЗОБРИТАТЕЛЕЙ ПАТЕНТА
    print("[INVENTORS]:" + '\n' + inventors_list)

    #ОРГАНИЗАЦИЯ ПАТЕНТА
    assignee_items = soup.find_all("dd",class_="style-scope patent-result")
    for assignee in assignee_items:
        if(assignee.find("a", id="link")):
            pass
        else:
            assignee_patent = assignee.text.strip()
            # ЗАПИСЬ ОРГАНИЗАЦИИ ПАТЕНТА В ФАЙЛ
            f.write("[ASSIGNEE]:" + '\n' + assignee_patent + '\n')
            # ВЫВОД ОРГАНИЗАЦИИ ПАТЕНТА
            #print("[ASSIGNEE]:" + '\n' + assignee_patent)
            break


    #ВЫВОД ПЕРВОГО КЛАССА(ПОДПРАВИТЬ КОММЕНТЫ)
    classes_list = []
    full_class=[]
    class_patent = soup.find("div", class_="table style-scope classification-viewer").find("div", class_="flex style-scope classification-tree").find_all("span", id ="target")
    class_item = class_patent[-1].find("a", id="link").get_text()
    class_desc = class_patent[-1].find("span", class_="description style-scope classification-tree").get_text()
    full_class.append(class_item)
    full_class.append(class_desc)
    classes_list.append(full_class)

    #ВЫВОД ОСТАЛЬНЫХ КЛАССОВ
    classes_patent = soup.find("div", class_="table style-scope classification-viewer").find("div", class_="style-scope classification-viewer").find_all("classification-tree", class_="style-scope classification-viewer")
    for classes in classes_patent:
        full_class = []
        classes_item = classes.find("div", class_="layout horizontal wrap style-scope classification-tree").find("div", class_="flex style-scope classification-tree").find_all("span", id ="target")
        class_item = classes_item[-1].find("a", id="link").get_text()
        class_desc = classes_item[-1].find("span", class_="description style-scope classification-tree").get_text()
        full_class.append(class_item)
        full_class.append(class_desc)
        classes_list.append(full_class)
    print("[СLASSES]:")
    f.write("[СLASSES]:" + '\n')
    for i in range(len(classes_list)):
        print(classes_list[i][0] + " - " + classes_list[i][1])
        f.write(classes_list[i][0] + " - " + classes_list[i][1] + '\n')

    # ВЫВОД КЛЕЙМС

    flex_frame = soup.find_all("div", class_="flex flex-width style-scope patent-result")
    claims = flex_frame[1].find("div", class_="layout horizontal style-scope patent-text").find("div", class_="claims style-scope patent-text")
    claims_list=[]
    claims_items = claims.find_all("div", class_="claim style-scope patent-text")
    for item in claims_items:
        claims_list.append(item.text.strip())
    no_dup_list = [el for el, _ in groupby(claims_list)]
    claims_patent = "\n".join(no_dup_list)
    print("[CLAIMS]:")
    f.write("[CLAIMS]:" + '\n')
    print(claims_patent)
    f.write(claims_patent + '\n')

    # ВЫВОД ОПИСАНИЕ
    description_items = soup.find("div", id="wrapper").find("div", id="text").find("div",class_="description style-scope patent-text")
    with open(path_desc, "w", encoding='utf-8') as file:
        file.write(str(description_items))
    with open(path_desc, "r", encoding='utf-8') as file:
        lines = file.readlines()
    description_heads = soup.find("div", id="wrapper").find("div", id="text").find("div",class_="description style-scope patent-text").find_all("heading",class_="style-scope patent-text")
    description_bodies = soup.find("div", id="wrapper").find("div", id="text").find("div",class_="description style-scope patent-text").find_all("div", class_="description-paragraph style-scope patent-text")
    i = 0
    description_patent_list=[]
    while i < len(lines):
        j = 0
        while j < len(description_heads):
            if lines[i] == (str(description_heads[j])+"\n"):
                description_patent_list.append(description_heads[j].text.strip())
            j += 1
        j = 0
        while j < len(description_bodies):

            if lines[i] == (str(description_bodies[j]) + "\n"):
                description_patent_list.append(description_bodies[j].text.strip())
            j += 1
        i += 1
    description_patent = "\n".join(description_patent_list)
    print("[DESCRIPTION]:")
    f.write("[DESCRIPTION]:" + '\n')
    print(description_patent)
    f.write(description_patent + '\n')

    #ВЫВОД ПАТЕНТНЫХ ССЫЛОК
    citations = soup.find("div", class_="footer style-scope patent-result").find("div", class_="table style-scope patent-result").find("div", class_="tbody style-scope patent-result").find_all("div", class_="tr style-scope patent-result")
    patent_citations = []
    family_citations = []
    check = False
    for citation in citations:
        full_info=[]
        if(check == False):
            check_family = citation.find("a")
            if (check_family):
                id_cit_p = citation.find("span", class_="td nowrap style-scope patent-result").find("state-modifier", class_="style-scope patent-result").find("a").get_text()
                other_param_p = citation.find_all("span", class_="td style-scope patent-result")
                prior_date_cit_p = other_param_p[0].text.strip()
                public_date_cit_p = other_param_p[1].text.strip()
                assignee_cit_p = other_param_p[2].text.strip()
                title_cit_p = other_param_p[3].text.strip()
                full_info.append(id_cit_p)
                full_info.append(prior_date_cit_p)
                full_info.append(public_date_cit_p)
                full_info.append(assignee_cit_p)
                full_info.append(title_cit_p)
                patent_citations.append(full_info)
            else:
                check = True
                pass
        else:
            id_cit_f= citation.find("span", class_="td nowrap style-scope patent-result").find("state-modifier",class_="style-scope patent-result").find("a").get_text()
            other_param_f = citation.find_all("span", class_="td style-scope patent-result")
            prior_date_cit_f = other_param_f[0].text.strip()
            public_date_cit_f = other_param_f[1].text.strip()
            assignee_cit_f = other_param_f[2].text.strip()
            title_cit_f = other_param_f[3].text.strip()
            full_info.append(id_cit_f)
            full_info.append(prior_date_cit_f)
            full_info.append(public_date_cit_f)
            full_info.append(assignee_cit_f)
            full_info.append(title_cit_f)
            family_citations.append(full_info)

    f.write("[PATENT_CITATIONS]:" + '\n')
    print("[PATENT_CITATIONS]: ")
    for i in range(len(patent_citations)):
        print(patent_citations[i][0] + " | " + patent_citations[i][1]+ " | " + patent_citations[i][2]+ " | " + patent_citations[i][3]+ " | " + patent_citations[i][4])
        f.write(patent_citations[i][0] + " | " + patent_citations[i][1] + " | " + patent_citations[i][2] + " | " + patent_citations[i][3] + " | " + patent_citations[i][4] + '\n')

    f.write("[PATENT_CITATIONS]:" + '\n')
    print("FAMILY_CITATIONS")
    for i in range(len(family_citations)):
        print(family_citations[i][0] + " | " + family_citations[i][1] + " | " + family_citations[i][2]+ " | " + family_citations[i][3]+ " | " + family_citations[i][4])
        f.write(family_citations[i][0] + " | " + family_citations[i][1] + " | " + family_citations[i][2]+ " | " + family_citations[i][3]+ " | " + family_citations[i][4] + '\n')

    # ВЫВОД ЦИТАТ
    responsive = soup.find_all("div", class_="responsive-table style-scope patent-result")
    num=1
    dl = soup.find("dl", class_="links style-scope patent-result")
    dd = dl.find_all("dd", class_="style-scope patent-result")
    for d in dd:
        a = d.find("a").text.strip()
        if "Non-patent citations" in a:
            num = 2
    cited_by = responsive[num].find("div", class_="table style-scope patent-result").find("div", class_="tbody style-scope patent-result").find_all("div", class_="tr style-scope patent-result")
    patent_cited_by = []
    family_cited_by = []
    check = False
    for cited in cited_by:
        full_info = []
        if (check == False):
            check_family = cited.find("a")
            if (check_family):
                id_cited_p = cited.find("span", class_="td nowrap style-scope patent-result").find("state-modifier", class_="style-scope patent-result").find("a").get_text()
                other_param_p = cited.find_all("span", class_="td style-scope patent-result")
                prior_date_cited_p = other_param_p[0].text.strip()
                public_date_cited_p = other_param_p[1].text.strip()
                assignee_cited_p = other_param_p[2].text.strip()
                title_cited_p = other_param_p[3].text.strip()
                full_info.append(id_cited_p)
                full_info.append(prior_date_cited_p)
                full_info.append(public_date_cited_p)
                full_info.append(assignee_cited_p)
                full_info.append(title_cited_p)
                patent_cited_by.append(full_info)
            else:
                check = True
                pass
        else:
            id_cited_f = cited.find("span", class_="td nowrap style-scope patent-result").find("state-modifier",class_="style-scope patent-result").find("a").get_text()
            other_param_f = cited.find_all("span", class_="td style-scope patent-result")
            prior_date_cited_f = other_param_f[0].text.strip()
            public_date_cited_f = other_param_f[1].text.strip()
            assignee_cited_f = other_param_f[2].text.strip()
            title_cited_f = other_param_f[3].text.strip()
            full_info.append(id_cited_f)
            full_info.append(prior_date_cited_f)
            full_info.append(public_date_cited_f)
            full_info.append(assignee_cited_f)
            full_info.append(title_cited_f)
            family_cited_by.append(full_info)
    f.write("[PATENT_CITED_BY]:" + '\n')
    print("[PATENT_CITED_BY]: ")
    for i in range(len(patent_cited_by)):
        print(patent_cited_by[i][0] + " | " + patent_cited_by[i][1] + " | " + patent_cited_by[i][2] + " | " +
                  patent_cited_by[i][3] + " | " + patent_cited_by[i][4])
        f.write(patent_cited_by[i][0] + " | " + patent_cited_by[i][1] + " | " + patent_cited_by[i][2] + " | " +
                  patent_cited_by[i][3] + " | " + patent_cited_by[i][4] + '\n')
    f.write("[FAMILY_CITED_BY]:" + '\n')
    print("[FAMILY_CITED_BY]: ")
    for i in range(len(family_cited_by)):
        print(family_cited_by[i][0] + " | " + family_cited_by[i][1] + " | " + family_cited_by[i][2] + " | " + family_cited_by[i][3] + " | " + family_cited_by[i][4])
        f.write(family_cited_by[i][0] + " | " + family_cited_by[i][1] + " | " + family_cited_by[i][2] + " | " +family_cited_by[i][3] + " | " + family_cited_by[i][4] + '\n')

    # ВЫВОД ПОХОЖИХ ДОКУМЕНТОВ
    responsive = soup.find_all("div", class_="responsive-table style-scope patent-result")
    trs = responsive[num+1].find("div", class_="table style-scope patent-result").find("div", class_="tbody style-scope patent-result").find_all("div", class_="tr style-scope patent-result")
    documents_patent = []
    for tr in trs:
        full_info = []
        other_param_d = tr.find_all("span", class_="td style-scope patent-result")
        id_document = other_param_d[0].text.strip()
        public_date_d = other_param_d[1].text.strip()
        title_d = other_param_d[2].text.strip()
        full_info.append(id_document)
        full_info.append(public_date_d)
        full_info.append(title_d)
        documents_patent.append(full_info)
    f.write("[DOCUMENTS]:" + '\n')
    print("[DOCUMENTS]: ")
    for i in range(len(documents_patent)):
        print(documents_patent[i][0] + " | " + documents_patent[i][1] + " | " + documents_patent[i][2])
        f.write(documents_patent[i][0] + " | " + documents_patent[i][1] + " | " + documents_patent[i][2] + '\n')
    f.close()

    patent = {'name': name_patent,
              'id': id_patent,
              'link_patent': link_patent,
              'status': status_patent,
              'abstract': abstract_patent,
              'inventors': inventors,
              'assignee': assignee_patent,
              'public_as': public_as,
              'classes': classes_list,
              'claims': claims_patent,
              'description': description_patent,
              'patent_citations': patent_citations,
              'family_citations': family_citations,
              'cited_by_patent': patent_cited_by,
              'cited_by_family': family_cited_by,
              'documents': documents_patent}
    #return patent

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
    print("| 1) УЗНАТЬ КОЛИЧЕСТВО ПАТЕНТОВ|\n" +
          "| 2) ПАРСИНГ ПАТЕНТОВ          |\n" +
          "| 3) СБОР ИНФОРМАЦИИ О ПАТЕНТЕ |\n" +
          "| 4) НОВЫЙ ПАТЕНТНЫЙ ПАРСЕР    |\n" +
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
    '''cpc = "H04N5"
    priority = "low"
    inventors = ""
    assignee = ""
    country = "US"
    date_after = "20150101"
    date_before = "20200909"
    type_date = "priority"
    status = "GRANT"
    lang = "ENGLISH"
    type_ = "PATENT"
    litigation = "l"
    url = "https://patents.google.com/?" + cpc \
          + "%2f" + priority \
          + "&country=" + country \
          + "&before=priority:" + date_before \
          + "&after=priority:" + date_after \
          + "&status=" + status \
          + "&language=" + lang \
          + "&type=" + type_

    if(cpc):
        url = url +"q="+cpc
    else:
        pass
    if()'''

    patents = "patents"
    html_patents = "html_patents"
    info_patents = "info_patents"

    path_patents = patents + "\\" + cpc
    path_html_patents = patents + "\\" + cpc + "\\" + html_patents
    path_info_patents = patents + "\\" + cpc + "\\" + info_patents
    path_html = "C:\\PythonProjects\\selenium_parser\\" + patents + "\\" + cpc + "\\" + html_patents
    path_info = "C:\\PythonProjects\\selenium_parser\\" + patents + "\\" + cpc + "\\" + info_patents

    if not os.path.isdir(patents):
        os.mkdir(patents)
        print("папка " + patents + " создана")
    else:
        print("[папка " + patents + " уже создана]")

    if not os.path.isdir(path_patents):
        os.makedirs(path_patents)
        print("папка " + cpc + " создана")
    else:
        print("[папка " + cpc + " уже создана]")

    if not os.path.isdir(path_html_patents):
        os.makedirs(path_html_patents)
        print("папка " + html_patents + " создана")
    else:
        print("[папка " + html_patents + " уже создана]")

    if not os.path.isdir(path_info_patents):
        os.makedirs(path_info_patents)
        print("папка " + info_patents + " создана")
    else:
        print("[папка " + info_patents + " уже создана]")

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