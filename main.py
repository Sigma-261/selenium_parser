from selenium import webdriver
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import wget
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
from colorama import init
import urllib
import pandas as pd
from openpyxl import load_workbook
from termcolor import colored
init()
#from colorama import Fore, Back, Style

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
        wait = WebDriverWait(driver, 100)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class=\'more style-scope classification-viewer\']')))
        full_list = driver.find_element_by_xpath("//div[@class='more style-scope classification-viewer']")
        full_list.click()

        id_patent = driver.find_element_by_xpath('/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[2]/section/header/h2').text

        status_patent = driver.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/application-timeline/div/div[9]/div[3]/span').text
        print(colored("[проверка статуса и id патента]", 'blue'))
        print(colored("[ID]: ", 'green') + id_patent)
        print(colored("[STATUS]: ", 'green'),end='')
        if(status_patent != "Active"):
            print(colored(status_patent, 'red'))
            return
        else:
            print(colored(status_patent, 'green'))
        print(colored("[DB]: ", 'green'), end='')

        '''with connection.cursor() as cursor:
                    insert_query = "SELECT Title FROM `patents` WHERE Title = \'" + name_patent + "\'"
                    cursor.execute(insert_query)
                    nnn = cursor.fetchone()
                if(nnn):
                    return'''

        if (id_patent == "US1082499B2"):
            print(colored("Уже существует", 'red'))
            return
        else:
            print(colored("Добавлено", 'green'))

        name_patent = driver.find_element_by_xpath('/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/h1').text
        print(colored("[NAME]: ", 'green') +"\n"+ name_patent)

        link_patent = driver.find_element_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[2]/section/header/div/state-modifier[2]/a").get_attribute("href")
        print(colored("[LINK]: ", 'green') +"\n"+ link_patent)

        abstract_patent = driver.find_element_by_xpath('//*[@id="text"]/abstract').text
        print(colored("[ABSTRACT]: ", 'green') +"\n"+ abstract_patent)

        inventor_patent=[]
        i=1
        while True:
            try:
                inventor_list = driver.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/dl[1]/dd['+str(i)+']/state-modifier').text
                inventor_patent.append(inventor_list)
                i += 1
            except:
                break
        print(colored("[INVENTORS]:", 'green'))
        for pat in range(len(inventor_patent)):
            print(inventor_patent[pat])

        assignee_patent = driver.find_element_by_xpath('//*[@id="wrapper"]/div[1]/div[2]/section/dl[1]/dd['+str(i)+']').text
        print(colored("[ASSIGNEE]: ", 'green') + "\n" + assignee_patent)


        public_as_patent = get_public_as(id_patent=id_patent)
        print(colored("[PUBLIC AS]: ", 'green'))
        for pat in range(len(public_as_patent)):
            print(public_as_patent[pat])


        # переработать(возможно)
        classes_patent=[]
        full_class = []
        first_class = driver.find_elements_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/classification-tree/div/div/div/div[*]/concept-mention/span/state-modifier")
        first_description = driver.find_elements_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/classification-tree/div/div/div/div[*]/concept-mention/span/span")
        full_class.append(first_class[-1].text)
        full_class.append(first_description[-1].text)
        classes_patent.append(full_class)
        i=0
        classes_list = driver.find_elements_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/div/classification-tree[*]/div/div/div/div[*]/concept-mention/span/state-modifier/a")
        for class_ in classes_list:
            full_class = []
            if(class_.text==""):
                pass
            else:
                full_class.append(class_.text)
                i+=1
                description = driver.find_elements_by_xpath("/html/body/search-app/search-result/search-ui/div/div/div/div/div/result-container/patent-result/div/div/div/div[1]/div[1]/section[3]/classification-viewer/div/div/classification-tree[" + str(i) + "]/div/div/div/div[*]/concept-mention/span/span")
                full_class.append(description[-1].text)
                classes_patent.append(full_class)

        print(colored("[CLASSES]: ", 'green'))
        for pat in range(len(classes_patent)):
            print(classes_patent[pat][0] + " - " + classes_patent[pat][1])

        description_patent = driver.find_element_by_xpath('//*[@id="description"]').text
        print(colored("[DESCRIPTION]: ", 'green') + "\n" +description_patent)

        claims_patent = driver.find_element_by_xpath('//*[@id="claims"]/patent-text/div').text
        print(colored("[CLAIMS]:", 'green') + "\n" + claims_patent)


        # переработать(возможно)
        citations = driver.find_elements_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[1]/div/div[2]/div[*]/span")
        i=0
        patent_citations = []
        family_citations = []
        check = True
        while True:
            try:
                full_info=[]
                if(check):
                    for n in range(0, 5):
                        if(citations[n + i].text == 'Family To Family Citations'):
                            check = False
                            break
                        else:
                            full_info.append(citations[n + i].text)
                    if (check):
                        patent_citations.append(full_info)
                else:
                    for n in range(0, 5):
                        full_info.append(citations[n + i].text)
                    family_citations.append(full_info)
            except:
                break
            i+=5

        '''patentCitations = driver.find_element_by_xpath('//*[@id="patentCitations"]').text
        pc_count = re.sub('\D', '', patentCitations)
        print(pc_count)
        i=1
        patent_citations = []
        family_citations = []
        check = True
        while i <= int(pc_count)+1:
            full_info = []
            #//*[@id="wrapper"]/div[3]/div[1]/div/div[2]/div[*]/span
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
            i+=1'''

        print(colored("[PATENT_CITATIONS]: ", 'green'))
        for pat in range(len(patent_citations)):
            print(patent_citations[pat][0] + " | " + patent_citations[pat][1] + " | " + patent_citations[pat][2] + " | " + patent_citations[pat][3] + " | " + patent_citations[pat][4])

        print(colored("[FAMILY_CITATIONS]", 'green'))
        for pat in range(len(family_citations)):
            print(family_citations[pat][0] + " | " + family_citations[pat][1] + " | " + family_citations[pat][2] + " | " + family_citations[pat][3] + " | " + family_citations[pat][4])

        nplCitations = driver.find_element_by_xpath("//*[@id=\"nplCitations\"]").text
        if(nplCitations):
            n5 = 5
        else:
            n5 = 3
        # переработать(возможно)
        '//*[@id="wrapper"]/div[3]/div[5]/div/div[2]/div[*]/span'
        cited_by = driver.find_elements_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[" + str(n5) + "]/div/div[2]/div[*]/span")
        i = 0
        patent_cited_by = []
        family_cited_by = []
        check = True
        while True:
            try:
                full_info = []
                if (check):
                    for n in range(0, 5):
                        if (cited_by[n + i].text == 'Family To Family Citations'):
                            check = False
                            break
                        else:
                            full_info.append(cited_by[n + i].text)
                    if (check):
                        patent_cited_by.append(full_info)
                else:
                    for n in range(0, 5):
                        full_info.append(cited_by[n + i].text)
                    family_cited_by.append(full_info)
            except:
                break
            i += 5


        '''citedBy = driver.find_element_by_xpath('//*[@id="citedBy"]').text
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
            i+=1'''

        print(colored("[PATENT_CITED_BY]: ", 'green'))
        for pat in range(len(patent_cited_by)):
            print(patent_cited_by[pat][0] + " | " + patent_cited_by[pat][1] + " | " + patent_cited_by[pat][2] + " | " +
                  patent_cited_by[pat][3] + " | " + patent_cited_by[pat][4])

        print(colored("[FAMILY_CITED_BY]: ", 'green'))
        for pat in range(len(family_cited_by)):
            print(family_cited_by[pat][0] + " | " + family_cited_by[pat][1] + " | " + family_cited_by[pat][2] + " | " +
                  family_cited_by[pat][3] + " | " + family_cited_by[pat][4])

        # переработать(возможно)
        simular_documents = driver.find_elements_by_xpath("//*[@id=\"wrapper\"]/div[3]/div[" + str(n5+2) + "]/div/div[2]/div[*]/span")
        i = 0
        documents_patent = []
        while True:
            try:
                full_info = []
                for n in range(0, 3):
                    full_info.append(simular_documents[n + i].text)
                documents_patent.append(full_info)
            except:
                break
            i += 3
        print(colored("[DOCUMENTS]: ", 'green'))
        for pat in range(len(documents_patent)):
            print(documents_patent[pat][0] + " | " + documents_patent[pat][1] + " | " + documents_patent[pat][2])

        patent = {'name': name_patent,
        'id': id_patent,
        'link_patent': link_patent,
        'status': status_patent,
        'abstract': abstract_patent,
        'inventors': inventor_patent,
        'assignee': assignee_patent,
        'public_as': public_as_patent,
        'classes': classes_patent,
        'claims': claims_patent,
        'description': description_patent,
        'patent_citations': patent_citations,
        'family_citations': family_citations,
        'patent_cited_by': patent_cited_by,
        'family_cited_by': family_cited_by,
        'documents': documents_patent}

        return patent
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

'''def parser_test(url,connection,count):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(), options=options)
    driver.maximize_window()
    try:
        driver.get(url=url)
        wait = WebDriverWait(driver, 100)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="htmlContent"]')))
        first_patent = driver.find_element_by_xpath("//span[@class='style-scope raw-html']")
        first_patent.click()
        i = 1
        while i < int(count):
            wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@class=\'more style-scope classification-viewer\']')))
            full_list = driver.find_element_by_xpath("//div[@class='more style-scope classification-viewer']")
            full_list.click()

            wait.until(EC.element_to_be_clickable((By.XPATH, 'html/body/search-app/search-result/search-ui/div/search-header/div/header/div/div[3]/result-nav/div/state-modifier[1]/a/span')))
            number_result = driver.find_element_by_xpath("/html/body/search-app/search-result/search-ui/div/search-header/div/header/div/div[3]/result-nav/div/state-modifier[1]/a/span").text
            print(number_result)
            time.sleep(20)
            next_result = driver.find_element_by_xpath("/html/body/search-app/search-result/search-ui/div/search-header/div/header/div/div[3]/result-nav/div/state-modifier[3]/a/iron-icon")
            next_result.click()

            i+=1
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()'''

def parser_test(url):
    #options = Options()
    #options.headless = True
    #driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(), options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    try:

        #i = 1
        driver.get(url=url)
        while True:
            f = open('text4.txt', 'a', encoding="utf-8")
            #list_patent1 = []
            wait = WebDriverWait(driver, 100)
            wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/search-app/search-results/search-ui/div/div/div[2]/div/div/div[1]/section')))
            links = driver.find_elements_by_xpath('/html/body/search-app/search-results/search-ui/div/div/div[2]/div/div/div[1]/section/search-result-item[*]/article/state-modifier/a/h3/raw-html/span')
            #lll=0
            for link in links:
                f.write(link.text + '\n')
                #lll+=1
            f.close()
            '''with open('text4.txt', 'r') as filehandle:
                filecontents = filehandle.readlines()
                for line in filecontents:
                    list_patent1.append(line)
            print(str(i)+": "+str(lll) +', ' + str(len(list_patent1)))'''
            try:
                next_result = driver.find_element_by_xpath('/html/body/search-app/search-results/search-ui/div/div/div[2]/div/div/div[1]/div[5]/search-paging/state-modifier[3]/a')
                next_result.click()
            except:
                break
            #i+=1

    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

def parser_test1(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(), options=options)
    driver.maximize_window()
    try:
        driver.get(url=url)
        wait = WebDriverWait(driver, 100)
        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div/div/div/div/div[1]/table/tbody/tr[8]/td[4]/a')))
        next_result = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div/div[1]/table/tbody/tr[8]/td[2]/span/span[1]')
        next_result.click()
        time.sleep(5)
        next_result4 = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div/div[1]/table/tbody/tr[13]/td[2]/span/span[1]')
        next_result4.click()
        time.sleep(5)
        next_result5 = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div/div[1]/table/tbody/tr[21]/td[2]/span/span[1]')
        next_result5.click()
        names = []
        i=27
        while True:
            time.sleep(5)
            next_result2 = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div/div[1]/table/tbody/tr['+str(i)+']')
            next_result = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div/div[1]/table/tbody/tr['+str(i)+']/td[2]')
            next_result1 = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div/div[1]/table/tbody/tr['+str(i)+']/td[4]').text
            if('H04N 5' in next_result1):
                next_result1 = next_result1.replace(" ","").replace("/","%2f")
                names.append(next_result1)
                print(next_result1)
                if (next_result2.get_attribute('aria-expanded') == 'false'):
                    next_result.click()
            elif ('H04N 7' in next_result1):
                return names
            else:
                pass

            i += 1
        '''links = driver.find_elements_by_xpath('/html/body/div[3]/div/div/div/div/div[1]/table/tbody/tr[*]/td[4]/a')
        for link in links:
            print(link.text)'''
    except Exception as _ex:
        print(_ex)
    finally:
        driver.close()
        driver.quit()

def parser_test2(url):
    #options = Options()
    #options.headless = True
    #driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(), options=options)
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.maximize_window()
    try:

        #i = 1
        driver.get(url=url)

        wait = WebDriverWait(driver, 100)
        '''        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/search-app/search-results/search-ui/div/div/div[2]/div/div/div[1]/div[2]/div[1]/span[2]/a')))
        next_result1 = driver.find_element_by_xpath('//*[@id="count"]/div[1]/span[2]/iron-icon')
        next_result1.click()
        time.sleep(5)'''
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="count"]/div[1]/span[2]/a')))
        next_result1 = driver.find_element_by_xpath('//*[@id="count"]/div[1]/span[2]/a')
        next_result1.click()
        time.sleep(20)
        #next_result = driver.find_element_by_xpath('//*[@id="count"]/div[1]/span[2]/a')
        #t = next_result.get_attribute('href')
        #return t

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
        y = 'https://patents.google.com/xhr/query?url=q%3DCPC%253dH04N5%252f14%252flow%26country%3DUS%26before%3Dpriority%3A20200909%26after%3Dpriority%3A20150101%26status%3DGRANT%26language%3DENGLISH%26type%3DPATENT&exp=&download=true&download_format=xlsx'
        r = requests.post(y, headers=headers)  # делаем запрос
        print(r)


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
        wait = WebDriverWait(driver, 100)
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
def insert_patent_citations(pc_num,pc_pri_d,pc_pub_d,pc_ass_d,pc_title, connection):
    with connection.cursor() as cursor:
        assignee = pc_ass_d.replace("\'","\"").replace("`", "\"")
        title = pc_title.replace("\'","\"").replace("`", "\"")
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + pc_num + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_assignee_patent = "SELECT Id FROM `assignees` WHERE Name = \'" + assignee + "\'" + ";"
        cursor.execute(select_assignee_patent)
        assignee_patent = cursor.fetchone()

        search_id_patent = "SELECT Public_numId FROM `patent_citations` WHERE Public_numId = " + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if id_patent:
            print("УЖЕ ЕСТЬ")
        else:
            insert1_query = "INSERT INTO `patent_citations` (Public_numId,Priority_date,Publication_date,AssigneeId,Title) VALUES (" + str(public_num['Id']) + "," + "\'" + pc_pri_d + "\'" + "," + "\'" + pc_pub_d + "\'" + "," + str(assignee_patent['Id']) + "," + "\'" + title + "\'"  + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_family_citations(fc_num,fc_pri_d,fc_pub_d,fc_ass_d,fc_title, connection):
    with connection.cursor() as cursor:
        assignee = fc_ass_d.replace("\'","\"").replace("`", "\"")
        title = fc_title.replace("\'","\"").replace("`", "\"")
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + fc_num + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_assignee_patent = "SELECT Id FROM `assignees` WHERE Name = \'" + assignee + "\'" + ";"
        cursor.execute(select_assignee_patent)
        assignee_patent = cursor.fetchone()

        search_id_patent = "SELECT Public_numId FROM `family_citations` WHERE Public_numId = " + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if id_patent:
            print("УЖЕ ЕСТЬ")
        else:
            insert1_query = "INSERT INTO `family_citations` (Public_numId,Priority_date,Publication_date,AssigneeId,Title) VALUES (" + str(public_num['Id']) + "," + "\'" + fc_pri_d + "\'" + "," + "\'" + fc_pub_d + "\'" + "," + str(assignee_patent['Id']) + "," + "\'" + title + "\'"  + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_patent_cited_by(pcb_num,pcb_pri_d,pcb_pub_d,pcb_ass_d,pcb_title, connection):
    with connection.cursor() as cursor:
        assignee = pcb_ass_d.replace("\'","\"").replace("`", "\"")
        title = pcb_title.replace("\'","\"").replace("`", "\"")
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + pcb_num + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_assignee_patent = "SELECT Id FROM `assignees` WHERE Name = \'" + assignee + "\'" + ";"
        cursor.execute(select_assignee_patent)
        assignee_patent = cursor.fetchone()

        search_id_patent = "SELECT Public_numId FROM `patent_cited_by` WHERE Public_numId = " + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if id_patent:
            print("УЖЕ ЕСТЬ")
        else:
            insert1_query = "INSERT INTO `patent_cited_by` (Public_numId,Priority_date,Publication_date,AssigneeId,Title) VALUES (" + str(public_num['Id']) + "," + "\'" + pcb_pri_d + "\'" + "," + "\'" + pcb_pub_d + "\'" + "," + str(assignee_patent['Id']) + "," + "\'" + title + "\'"  + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_family_cited_by(fcb_num,fcb_pri_d,fcb_pub_d,fcb_ass_d,fcb_title, connection):
    with connection.cursor() as cursor:
        assignee = fcb_ass_d.replace("\'","\"").replace("`", "\"")
        title = fcb_title.replace("\'","\"").replace("`", "\"")
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + fcb_num + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_assignee_patent = "SELECT Id FROM `assignees` WHERE Name = \'" + assignee + "\'" + ";"
        cursor.execute(select_assignee_patent)
        assignee_patent = cursor.fetchone()

        search_id_patent = "SELECT Public_numId FROM `family_cited_by` WHERE Public_numId = " + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if id_patent:
            print("УЖЕ ЕСТЬ")
        else:
            insert1_query = "INSERT INTO `family_cited_by` (Public_numId,Priority_date,Publication_date,AssigneeId,Title) VALUES (" + str(public_num['Id']) + "," + "\'" + fcb_pri_d + "\'" + "," + "\'" + fcb_pub_d + "\'" + "," + str(assignee_patent['Id']) + "," + "\'" + title + "\'"  + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_documents(doc_num,pub_d,title,connection):
    with connection.cursor() as cursor:
        title = title.replace("\'","\"").replace("`", "\"")
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + doc_num + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        search_id_patent = "SELECT Public_numId FROM `documents` WHERE Public_numId = " + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if id_patent:
            print("УЖЕ ЕСТЬ")
        else:
            insert1_query = "INSERT INTO `documents` (Public_numId,Publication_date,Title) VALUES (" + str(public_num['Id']) + "," + "\'" + pub_d + "\'"  + "," + "\'" + title + "\'"  + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_patents_inventors(patent_id, inventor,connection):
    inventor = inventor.replace("\'", "\"").replace("`", "\"")
    with connection.cursor() as cursor:
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + patent_id + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_public_num1 = "SELECT Id FROM `inventors` WHERE Name = \'" + inventor + "\'" + ";"
        cursor.execute(select_public_num1)
        public_num1 = cursor.fetchone()

        search_id_patent = "SELECT InventorsId, PatentsId FROM `patents_of_inventors` WHERE InventorsId = " + str(public_num1['Id']) + " AND " + "PatentsId =" +str(public_num['Id'])+ ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if (id_patent):
            print("УЖЕ ЕСТЬ")
        else:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            insert1_query = "INSERT INTO `patents_of_inventors` (InventorsId,PatentsId) VALUES (" + str(public_num1['Id']) + "," + str(public_num['Id']) + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_patents_classes(patent_id, class_,connection):
    with connection.cursor() as cursor:
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + patent_id + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_public_num1 = "SELECT Id FROM `classes` WHERE Name = \'" + class_ + "\'" + ";"
        cursor.execute(select_public_num1)
        public_num1 = cursor.fetchone()

        search_id_patent = "SELECT ClassesId, PatentsId FROM `patents_of_classes` WHERE ClassesId = " + str(public_num1['Id']) + " AND " + "PatentsId =" +str(public_num['Id'])+ ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if (id_patent):
            print("УЖЕ ЕСТЬ")
        else:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            insert1_query = "INSERT INTO `patents_of_classes` (ClassesId,PatentsId) VALUES (" + str(public_num1['Id']) + "," + str(public_num['Id']) + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_patents_pc(patent_id, patent_citation, connection):
    with connection.cursor() as cursor:
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + patent_id + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_public_num1 = "SELECT Id FROM `publication_num` WHERE Name = \'" + patent_citation + "\'" + ";"
        cursor.execute(select_public_num1)
        public_num1 = cursor.fetchone()

        select_public_num2 = "SELECT Id FROM `patent_citations` WHERE Public_numId = \'" + str(public_num1['Id']) + "\'" + ";"
        cursor.execute(select_public_num2)
        public_num2 = cursor.fetchone()

        search_id_patent = "SELECT pcId, PatentsId FROM `patents_of_pc` WHERE pcId = " + str(public_num2['Id']) + " AND " + "PatentsId =" + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if (id_patent):
            print("УЖЕ ЕСТЬ")
        else:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            insert1_query = "INSERT INTO `patents_of_pc` (pcId,PatentsId) VALUES (" + str(public_num2['Id']) + "," + str(public_num['Id']) + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_patents_fc(patent_id, family_citation, connection):
    with connection.cursor() as cursor:
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + patent_id + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_public_num1 = "SELECT Id FROM `publication_num` WHERE Name = \'" + family_citation + "\'" + ";"
        cursor.execute(select_public_num1)
        public_num1 = cursor.fetchone()

        select_public_num2 = "SELECT Id FROM `family_citations` WHERE Public_numId = \'" + str(public_num1['Id']) + "\'" + ";"
        cursor.execute(select_public_num2)
        public_num2 = cursor.fetchone()

        search_id_patent = "SELECT fcId, PatentsId FROM `patents_of_fc` WHERE fcId = " + str(public_num2['Id']) + " AND " + "PatentsId =" + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if (id_patent):
            print("УЖЕ ЕСТЬ")
        else:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            insert1_query = "INSERT INTO `patents_of_fc` (fcId,PatentsId) VALUES (" + str(public_num2['Id']) + "," + str(public_num['Id']) + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_patents_pcb(patent_id, cited_by_patent,connection):
    with connection.cursor() as cursor:
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + patent_id + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_public_num1 = "SELECT Id FROM `publication_num` WHERE Name = \'" + cited_by_patent + "\'" + ";"
        cursor.execute(select_public_num1)
        public_num1 = cursor.fetchone()

        select_public_num2 = "SELECT Id FROM `patent_cited_by` WHERE Public_numId = \'" + str(public_num1['Id']) + "\'" + ";"
        cursor.execute(select_public_num2)
        public_num2 = cursor.fetchone()

        search_id_patent = "SELECT pcbId, PatentsId FROM `patents_of_pcb` WHERE pcbId = " + str(public_num2['Id']) + " AND " + "PatentsId =" + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if (id_patent):
            print("УЖЕ ЕСТЬ")
        else:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            insert1_query = "INSERT INTO `patents_of_pcb` (pcbId,PatentsId) VALUES (" + str(public_num2['Id']) + "," + str(public_num['Id']) + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_patents_fcb(patent_id, cited_by_family,connection):
    with connection.cursor() as cursor:
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + patent_id + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_public_num1 = "SELECT Id FROM `publication_num` WHERE Name = \'" + cited_by_family + "\'" + ";"
        cursor.execute(select_public_num1)
        public_num1 = cursor.fetchone()

        select_public_num2 = "SELECT Id FROM `family_cited_by` WHERE Public_numId = \'" + str(public_num1['Id']) + "\'" + ";"
        cursor.execute(select_public_num2)
        public_num2 = cursor.fetchone()

        search_id_patent = "SELECT fcbId, PatentsId FROM `patents_of_fcb` WHERE fcbId = " + str(public_num2['Id']) + " AND " + "PatentsId =" + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if (id_patent):
            print("УЖЕ ЕСТЬ")
        else:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            insert1_query = "INSERT INTO `patents_of_fcb` (fcbId,PatentsId) VALUES (" + str(public_num2['Id']) + "," + str(public_num['Id']) + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_patents_documents(patent_id, document, connection):
    with connection.cursor() as cursor:
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + patent_id + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_public_num1 = "SELECT Id FROM `publication_num` WHERE Name = \'" + document + "\'" + ";"
        cursor.execute(select_public_num1)
        public_num1 = cursor.fetchone()

        select_public_num2 = "SELECT Id FROM `documents` WHERE Public_numId = \'" + str(public_num1['Id']) + "\'" + ";"
        cursor.execute(select_public_num2)
        public_num2 = cursor.fetchone()

        search_id_patent = "SELECT DocumentsId, PatentsId FROM `patents_of_documents` WHERE DocumentsId = " + str(public_num2['Id']) + " AND " + "PatentsId =" + str(public_num['Id']) + ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if (id_patent):
            print("УЖЕ ЕСТЬ")
        else:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            insert1_query = "INSERT INTO `patents_of_documents` (DocumentsId,PatentsId) VALUES (" + str(public_num2['Id']) + "," + str(public_num['Id']) + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")
def insert_public_as(patent_id, public_as,connection):
    with connection.cursor() as cursor:
        select_public_num = "SELECT Id FROM `publication_num` WHERE Name = \'" + patent_id + "\'" + ";"
        cursor.execute(select_public_num)
        public_num = cursor.fetchone()

        select_public_num1 = "SELECT Id FROM `publication_num` WHERE Name = \'" + public_as + "\'" + ";"
        cursor.execute(select_public_num1)
        public_num1 = cursor.fetchone()

        search_id_patent = "SELECT PublicationId, PatentsId FROM `public_as` WHERE PublicationId = " + str(public_num1['Id']) + " AND " + "PatentsId =" +str(public_num['Id'])+ ";"
        cursor.execute(search_id_patent)
        id_patent = cursor.fetchone()
        if (id_patent):
            print("УЖЕ ЕСТЬ")
        else:
            cursor.execute("SET FOREIGN_KEY_CHECKS=0")
            insert1_query = "INSERT INTO `public_as` (PublicationId,PatentsId) VALUES (" + str(public_num1['Id']) + "," + str(public_num['Id']) + ")" + ";"
            cursor.execute(insert1_query)
            connection.commit()
            print("ВСТАВИТЬ")

def get_doc_patents(cpc):
    headers = {
        'authority': 'patents.google.com',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'x-client-data': 'CJW2yQEIpbbJAQjBtskBCKmdygEIk9vKAQjq8ssBCO/yywEInvnLAQjmhMwBCLWFzAEI/4XMAQjLicwBCI6NzAEYqqnKAQ==',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'referer': 'https://patents.google.com/xhr/query?url=q%3DCPC%253d'+cpc+'%252f14%252flow%26country%3DUS%26before%3Dpriority%3A20200909%26after%3Dpriority%3A20150101%26status%3DGRANT%26language%3DENGLISH%26type%3DPATENT&exp=&download=true&download_format=xlsx',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': 'CONSENT=YES+RU.ru+20180311-09-0; ANID=AHWqTUnhydZcNb0Bi9Z2Dol2Fzbfl1sluC1hnyrtfzPNgmk9q2DbO2NGogTpoolK; OGP=-19022591:; __Secure-1PSIDCC=AJi4QfF9uhf29mMsiIaTG7SvO9xaxgz5_i7tJy7kCzsrH1lkOYq8TnvxOwPAweVM-NcPHuXv; HSID=AUf9kWdpkVfcIEwHj; SSID=AHQOR7k5hrQrcWDy2; APISID=rHXMcwYERlmkcJC8/AJ_lEhLnHtSeK12Ee; SAPISID=lneiZkJX8MbzsnpN/AmfmLHsatBHuKK1i_; __Secure-1PAPISID=lneiZkJX8MbzsnpN/AmfmLHsatBHuKK1i_; __Secure-3PAPISID=lneiZkJX8MbzsnpN/AmfmLHsatBHuKK1i_; _ga=GA1.3.1424021396.1631281732; OGPC=19022622-1:; SID=DQgzj7EJRUqoydE9cRjzg5mrgmbgHb0Zo4b6T08xNRiMRKig1NpV0kG5k22OlYKBOHT0cg.; __Secure-1PSID=DQgzj7EJRUqoydE9cRjzg5mrgmbgHb0Zo4b6T08xNRiMRKigLOqnIwPV83QDwfidVBYS8Q.; __Secure-3PSID=DQgzj7EJRUqoydE9cRjzg5mrgmbgHb0Zo4b6T08xNRiMRKigCpoBWLxXnj_r4kRMMohdhw.; S=sso=Pq1sbhI3Cxt7QJFCnYy9FxiGnyuyFlrA; SEARCH_SAMESITE=CgQIg5QB; NID=511=P6MxVTrB07JPZAPoX1ISDORTKkng_1yGNdL6TfmdzbyEuUDchoXgxDB3kM4TMuykPV8VdP4dctB2SKjLrUmmu6Xk1V9CCR-lXhVQwKgpO4f5ZHJ7DFGNv52RziIlr4aT8jXwEEB3N8rUlqXDPk5Bv3jv2AyMSsS9cTvZ9zhTOZdAqfnxIbAmLbUrjLLHKZJeudoT0IkcyIfa2UbNAQbTwdw5MOrFMiXQ-rzeyW9ouXB1UWGi3WCXLpEe70wXn38PKBIImo1PQBS7GaC1qbNL_bDCl68Yt6TcJIEiZoluGiJ2P1BnoOnNenSTbFEVTUsTgpcXG3Y4PatPS6ESXR1Jl--TUmkOCidOA9QHyrwxo6ibMlNUxCW25nke_OYwdedJHdOdpnGlRLg73TQMiybm5MPHL7lCwySAmPPTiDFNVhjvNvEPW0oxhdkzc4Hc4YLw-PZZpAEod9zRGX0qTg; 1P_JAR=2021-11-16-19; SIDCC=AJi4QfGGwRvULEgLIhz7vaDrPkLZva7ep6afDZkFkwBD3MY3vlGf96n9hH-HPJjtC1t3-K_3muhl; __Secure-3PSIDCC=AJi4QfERPdkXEUEQzGAAyXJbehDh1EIb_A-d7zzxvNba8fVbmSlA93b9lcTvSLXDvBUAi4pAmeg',
    }

    params = (
        ('url',
         'q=CPC%3d'+cpc+'%2flow&country=US&before=priority:20200909&after=priority:20150101&status=GRANT&language=ENGLISH&type=PATENT'),
        ('exp', ''),
        ('download', 'true'),
        ('download_format', 'xlsx')
    )

    response = requests.get('https://patents.google.com/xhr/query', headers=headers, params=params)
    print(response)
    open(cpc+'.xlsx', "wb").write(response.content)

def get_id_patents(cpc):
    wb = load_workbook(cpc+'.xlsx')
    ws = wb.active
    colC = ws['A']
    for row in colC:
        if (row.value == 'id' or row.value == 'search URL:' or row.value ==None):
            continue
        else:
            print(row.value.replace("-",""))

def main():
    print("---------------------------------------+")
    print("| ВЫБЕРИТЕ ФУНКЦИЮ                     |")
    print("+--------------------------------------+")
    print("| 1) ПАРСИНГ ПАТЕНТОВ                  |\n" +
          "| 2) ЗАПИСЬ В БД                       |\n" +
          "| 3) ПОЛУЧНИЕ ДОКУМЕНТОВ С ID ПАТЕНТОВ |\n" +
          "| 4) ПОЛУЧНИЕ ID ПАТЕНТОВ              |\n" +
          "| 5) ...                               |")
    print("+--------------------------------------+\n")
    cpc = "H04N5"
    priority = "low"
    country = "US"
    date_before = "20200909"
    date_after = "20150101"
    status = "GRANT"
    lang = "ENGLISH"
    type_ = "PATENT"
    url = "https://patents.google.com/patent/US10571666B2/en?q=CPC%3d" + cpc \
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
        print(colored("[подключение к базе данных]", 'green'))
    except Exception as ex:
        print(colored("[подключение к базе данных не удалось]", 'red'))
        print(ex)

    while True:
        print("ВВЕДИТЕ НОМЕР: ", end='')
        num = input()

        print("ВЫБРАНА ФУНКЦИЯ: ", end='')
        if num == "1":
            print("ПАРСИНГ ПАТЕНТОВ")
            url ='https://patents.google.com/patent/US10824999B2/en?q=CPC%3dH04N5%2flow&country=US&before=priority:20200909&after=priority:20150101&status=GRANT&language=ENGLISH&type=PATENT'
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

            for pat in range(len(patent['patent_citations'])):
                insert_patent_citations(pc_num=patent['patent_citations'][pat][0],pc_pri_d=patent['patent_citations'][pat][1],pc_pub_d=patent['patent_citations'][pat][2],pc_ass_d=patent['patent_citations'][pat][3],pc_title=patent['patent_citations'][pat][4], connection=connection)
            for pat in range(len(patent['family_citations'])):
                insert_family_citations(fc_num=patent['family_citations'][pat][0],
                                    fc_pri_d=patent['family_citations'][pat][1],
                                    fc_pub_d=patent['family_citations'][pat][2],
                                    fc_ass_d=patent['family_citations'][pat][3],
                                    fc_title=patent['family_citations'][pat][4], connection=connection)
            for pat in range(len(patent['cited_by_patent'])):
                insert_patent_cited_by(pcb_num=patent['cited_by_patent'][pat][0],
                                       pcb_pri_d=patent['cited_by_patent'][pat][1],
                                       pcb_pub_d=patent['cited_by_patent'][pat][2],
                                       pcb_ass_d=patent['cited_by_patent'][pat][3],
                                       pcb_title=patent['cited_by_patent'][pat][4], connection=connection)
            for pat in range(len(patent['cited_by_family'])):
                insert_family_cited_by(fcb_num=patent['cited_by_family'][pat][0],
                                    fcb_pri_d=patent['cited_by_family'][pat][1],
                                    fcb_pub_d=patent['cited_by_family'][pat][2],
                                    fcb_ass_d=patent['cited_by_family'][pat][3],
                                    fcb_title=patent['cited_by_family'][pat][4], connection=connection)
            for pat in range(len(patent['documents'])):
                insert_documents(doc_num=patent['documents'][pat][0],
                                    pub_d=patent['documents'][pat][1],
                                    title=patent['documents'][pat][2],connection=connection)
            for pat in range(len(patent['inventors'])):
                insert_patents_inventors(patent_id=patent['id'], inventor = patent['inventors'][pat], connection = connection)
            for pat in range(len(patent['classes'])):
                insert_patents_classes(patent_id=patent['id'], class_ = patent['classes'][pat][0], connection = connection)
            for pat in range(len(patent['patent_citations'])):
                insert_patents_pc(patent_id=patent['id'], patent_citation = patent['patent_citations'][pat][0], connection = connection)
            for pat in range(len(patent['family_citations'])):
                insert_patents_fc(patent_id=patent['id'], family_citation = patent['family_citations'][pat][0], connection = connection)
            for pat in range(len(patent['cited_by_patent'])):
                insert_patents_pcb(patent_id=patent['id'], cited_by_patent = patent['cited_by_patent'][pat][0], connection = connection)
            for pat in range(len(patent['cited_by_family'])):
                insert_patents_fcb(patent_id=patent['id'], cited_by_family = patent['cited_by_family'][pat][0], connection = connection)
            for pat in range(len(patent['documents'])):
                insert_patents_documents(patent_id=patent['id'], document = patent['documents'][pat][0], connection = connection)
            for pat in range(len(patent['public_as'])):
                insert_public_as(patent_id=patent['id'], public_as = patent['public_as'][pat], connection = connection)
        elif num == "3":
            print("ПОЛУЧНИЕ ДОКУМЕНТОВ С ID ПАТЕНТОВ")
            get_doc_patents(cpc=cpc)
        elif num == "4":
            print("ПОЛУЧНИЕ ID ПАТЕНТОВ")
            get_id_patents(cpc=cpc)

        else:
            print(colored("НЕИЗВЕСТНО", 'red'))


if __name__ == "__main__":
    main()