from selenium import webdriver
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.options import Options
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


def get_public_as(id_patent):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    full_publication=[]
    try:
        url = "https://worldwide.espacenet.com/patent/search/family/057994253/publication/" + id_patent + "?q=" + id_patent
        driver.get(url=url)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"biblio-also-published-as-content\"]/div[1]/a/span[1]")))
        i = 1
        while True:
            try:
                public_num = driver.find_element_by_xpath("//*[@id=\"biblio-also-published-as-content\"]/div[" + str(i) + "]/a/span[1]").text
            except:
                break
            i += 1
            full_publication.append(public_num)
        return full_publication
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

def parser_loader_new(url,connection):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    try:
        driver.get(url=url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="htmlContent"]')))
        first_patent = driver.find_element_by_xpath("//span[@class='style-scope raw-html']")
        first_patent.click()

        wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class=\'more style-scope classification-viewer\']')))
        full_list = driver.find_element_by_xpath("//div[@class='more style-scope classification-viewer']")
        full_list.click()

        status_patent = driver.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/application-timeline/div/div[9]/div[3]/span').text
        if(status_patent != "Active"):
            return

        name_patent = driver.find_element_by_xpath('/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/h1').text
        '''with connection.cursor() as cursor:
            insert_query = "SELECT Title FROM `patents` WHERE Title = \'" + name_patent + "\'"
            cursor.execute(insert_query)
            nnn = cursor.fetchone()
        if(nnn):
            return'''
        print("[NAME]:" +"\n"+ name_patent)


        id_patent = driver.find_element_by_xpath('/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[2]/section/header/h2').text
        print("[ID]:" +"\n"+ id_patent)

        link_patent = driver.find_element_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[2]/section/header/div/state-modifier[2]/a").get_attribute("href")
        print("[LINK]:" +"\n"+ link_patent)

        print("[STATUS]:" + "\n" + status_patent)

        abstract_patent = driver.find_element_by_xpath('//*[@id="text"]/abstract').text
        print("[ABSTRACT]:" +"\n"+ abstract_patent)

        inventors_list=[]
        i=1
        while True:
            try:
                inventor_patent = driver.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/dl[1]/dd['+str(i)+']/state-modifier').text
                inventors_list.append(inventor_patent)
                i += 1
            except:
                break
        print("[INVENTORS]:")
        for pat in range(len(inventors_list)):
            print(inventors_list[pat])

        assignee_patent = driver.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/dl[1]/dd['+str(i)+']').text
        print("[ASSIGNEE]:" + "\n" + assignee_patent)


        public_list = get_public_as(id_patent=id_patent)
        print("[PUBLIC AS]:")
        for pat in range(len(public_list)):
            print(public_list[pat])

        classes_list=[]
        full_class = []
        first_class = driver.find_elements_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/classification-tree/div/div/div/div[*]/concept-mention/span/state-modifier")
        first_description = driver.find_elements_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/classification-tree/div/div/div/div[*]/concept-mention/span/span")
        full_class.append(first_class[-1].text)
        full_class.append(first_description[-1].text)
        classes_list.append(full_class)
        i=0
        classes_patent = driver.find_elements_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/div/classification-tree[*]/div/div/div/div[*]/concept-mention/span/state-modifier/a")
        for class_ in classes_patent:
            full_class = []
            if(class_.text==""):
                pass
            else:
                full_class.append(class_.text)
                i+=1
                description = driver.find_elements_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/div/classification-tree[" + str(i) + "]/div/div/div/div[*]/concept-mention/span/span")
                full_class.append(description[-1].text)
                classes_list.append(full_class)

        print("[CLASSES]: ")
        for pat in range(len(classes_list)):
            print(classes_list[pat][0] + " - " + classes_list[pat][1])

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
            item1 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[1]/div/div[2]/div[" + str(i) + "]/span[1]").text.replace(" *","")
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
            item1 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div["+str(n)+"]/div/div[2]/div[" + str(i) + "]/span[1]").text.replace(" *","")
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
                item1 = driver.find_element_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[" + str(n+2) + "]/div/div[2]/div[" + str(i) + "]/span[1]").text.replace(" *","")
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
        'inventors': inventors_list,
        'assignee': assignee_patent,
        'public_as': public_list,
        'classes': classes_list,
        'claims': claims_patent,
        'description': description_patent,
        'patent_citations': patent_citations,
        'family_citations': family_citations,
        'cited_by_patent': patent_cited_by,
        'cited_by_family': family_cited_by,
        'documents': simular_document}
        return patent
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

def get_count_patents(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(), options=options)
    driver.maximize_window()
    try:
        driver.get(url=url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="count"]/div[1]/span[1]/span[3]')))

        full_list = driver.find_element_by_xpath('//*[@id="count"]/div[1]/span[1]/span[3]').text
        return full_list.replace(",","")

    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

def insert_assignee(assignee, connection):
    with connection.cursor() as cursor:
        assignee = assignee.replace("\'","\"").replace("`", "\"")
        print(assignee)
        insert_query = "SELECT Name FROM `assignees` WHERE Name = \'" + assignee + "\'"
        cursor.execute(insert_query)
        nnn = cursor.fetchone()
        if (nnn):
            print("УЖЕ ЕСТЬ")
        else:
            print("ВСТАВИТЬ")
            insert1_query = "INSERT INTO `assignees` (Name) VALUES (" + "\'" + assignee + "\'" + ");"
            cursor.execute(insert1_query)
            connection.commit()

def insert_publication_num(num, connection):
    with connection.cursor() as cursor:
        print(num)
        insert_query = "SELECT Name FROM `publication_num` WHERE Name = \'" + num + "\'"
        cursor.execute(insert_query)
        nnn = cursor.fetchone()
        if (nnn):
            print("УЖЕ ЕСТЬ")
        else:
            print("ВСТАВИТЬ")
            insert1_query = "INSERT INTO `publication_num` (Name) VALUES (" + "\'" + num + "\'" + ")"
            cursor.execute(insert1_query)
            connection.commit()

def insert_patent(id,title,link,status,assignee,abstract,claims,description, connection):
    with connection.cursor() as cursor:
        assignee = assignee.replace("\'","\"").replace("`", "\"")
        claims = claims.replace("\'","\"").replace("`", "\"")
        description = description.replace("\'", "\"").replace("`", "\"")
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + id + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_assignee_patent = "SELECT Id FROM `assignees` WHERE Name = \'" + assignee + "\'" + ";"
        cursor.execute(select_assignee_patent)
        assignee_patent = cursor.fetchone()

        search_id_patent = "SELECT Public_numId FROM `patents` WHERE Public_numId = " + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if id_patent:
            print("УЖЕ ЕСТЬ")
        else:

            insert1_query = "INSERT INTO `patents` (Public_numId,Title,Link,Status,AssigneeId,Abstract,Claims,Description) VALUES (" + str(public_num['Id']) + "," + "\'" + title + "\'" + "," + "\'" + link + "\'" + "," + "\'" + status + "\'" + "," + str(assignee_patent['Id']) + "," + "\'" + abstract + "\'" + "," + "\'" + claims + "\'" + "," + "\'" + description + "\'" + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")

def insert_inventors(inventor, connection):
    #Добавить replace
    with connection.cursor() as cursor:
        print(inventor)
        insert_query = "SELECT Name FROM `inventors` WHERE Name = \'" + inventor + "\'"
        cursor.execute(insert_query)
        nnn = cursor.fetchone()
        if (nnn):
            print("УЖЕ ЕСТЬ")
        else:
            print("ВСТАВИТЬ")
            insert1_query = "INSERT INTO `inventors` (Name) VALUES (" + "\'" + inventor + "\'" + ")"
            cursor.execute(insert1_query)
            connection.commit()

def insert_classes(class_name,class_descriprion, connection):
    # Добавить replace описания
    with connection.cursor() as cursor:
        print(class_name + " - " + class_descriprion)
        insert_query = "SELECT Name FROM `classes` WHERE Name = \'" + class_name + "\'"
        cursor.execute(insert_query)
        nnn = cursor.fetchone()
        if (nnn):
            print("УЖЕ ЕСТЬ")
        else:
            print("ВСТАВИТЬ")
            insert1_query = "INSERT INTO `classes` (Name, Description) VALUES (" + "\'" + class_name + "\'" + "," + "\'" + class_descriprion + "\'" + ")"
            cursor.execute(insert1_query)
            connection.commit()

def insert_patent_citations(connection):
    pass
def insert_family_citations(connection):
    pass
def insert_patent_cited_by(connection):
    pass
def insert_family_cited_by(connection):
    pass
def insert_documents(connection):
    pass
def insert_patents_inventors(connection):
    pass
def insert_patents_classes(connection):
    pass
def insert_patents_pc(connection):
    pass
def insert_patents_cited_by(connection):
    pass
def insert_patents_documents(connection):
    pass
def insert_public_as(connection):
    pass

def main():

    print("-------------------------------+")
    print("| ВЫБЕРИТЕ ФУНКЦИЮ             |")
    print("+------------------------------+")
    print("| 1) ПАРСИНГ ПАТЕНТОВ          |\n" +
          "| 2) ЗАПИСЬ В БД               |\n" +
          "| 3) ...                       |\n" +
          "| 4) ...                       |\n" +
          "| 5) ...                       |")
    print("+------------------------------+\n")
    #print("o`nil".replace("`","\""))
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
        print("[подключение к базе данных]")
    except Exception as ex:
        print("[подключение к базе данных не удалось]")
        print(ex)

    while True:
        print("ВВЕДИТЕ НОМЕР: ", end='')
        num = input()

        print("ВЫБРАНА ФУНКЦИЯ: ", end='')
        if num == "1":
            print("ПАРСИНГ ПАТЕНТОВ")
            print("КОЛИЧЕСТВО ПАТЕНТОВ КЛАССА " + cpc + "/" + priority + ": ", end='')
            print(get_count_patents(url=url))

            patent = parser_loader_new(url = url,connection=connection)
        elif num == "2":
            print("ЗАПИСЬ В БД")
            for pat in range(len(patent['patent_citations'])):
                insert_assignee(assignee = patent['patent_citations'][pat][3], connection = connection)
            for pat in range(len(patent['family_citations'])):
                print(patent['family_citations'][pat][3])
                insert_assignee(assignee = patent['family_citations'][pat][3], connection = connection)
            for pat in range(len(patent['cited_by_patent'])):
                print(patent['cited_by_patent'][pat][3])
                insert_assignee(assignee = patent['cited_by_patent'][pat][3], connection = connection)
            for pat in range(len(patent['cited_by_family'])):
                print(patent['cited_by_family'][pat][3])
                insert_assignee(assignee = patent['cited_by_family'][pat][3], connection = connection)
            insert_assignee(assignee=patent['assignee'], connection=connection)

            for pat in range(len(patent['patent_citations'])):
                insert_publication_num(num = patent['patent_citations'][pat][0], connection = connection)
            for pat in range(len(patent['family_citations'])):
                insert_publication_num(num = patent['family_citations'][pat][0], connection = connection)
            for pat in range(len(patent['cited_by_patent'])):
                insert_publication_num(num = patent['cited_by_patent'][pat][0], connection = connection)
            for pat in range(len(patent['cited_by_family'])):
                insert_publication_num(num = patent['cited_by_family'][pat][0], connection = connection)
            for pat in range(len(patent['documents'])):
                insert_publication_num(num = patent['documents'][pat][0], connection = connection)
            for pat in range(len(patent['public_as'])):
                insert_publication_num(num = patent['public_as'][pat], connection = connection)
            insert_publication_num(num=patent['id'], connection=connection)

            insert_patent(id=patent['id'],title=patent['name'],link=patent['link_patent'],status=patent['status'],assignee=patent['assignee'],abstract=patent['abstract'],claims=patent['claims'],description=patent['description'], connection=connection)

            for pat in range(len(patent['inventors'])):
                insert_inventors(inventor = patent['inventors'][pat], connection = connection)

            for pat in range(len(patent['classes'])):
                insert_classes(class_name = patent['classes'][pat][0],class_descriprion = patent['classes'][pat][1], connection = connection)
        else:
            print("НЕИЗВЕСТНО")

if __name__ == "__main__":
    main()