import re, sys, os
import pandas as pd
import numpy as np
from time import time
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

# Base url for walking. Set items_on_page as big as possible to reduce number of requests.
url_prefix = 'http://zakupki.gov.ru/epz/purchaseplanfz44/purchasePlanStructuredCard/plan-position-search.html?plan-number=201701482000039002&pageSize=50&page='

# Clear html element
def clear_str(x):
    clr_str = re.sub("<br>"," ",x.text)
    clr_str = re.sub("<br/>"," ",clr_str)
    clr_str = re.sub("\n","",clr_str)
    clr_str = re.sub('  +',' ', clr_str)
    return clr_str.strip()

# Find total number of pages
def get_presets():
    response = urlopen(url_prefix + '1')
    data = response.read().decode()
    soup = BeautifulSoup(data, "html.parser")
    # Get num of pages
    last_href = soup.find('ul', {'class': 'paging'}).find_all('li')[-1].find('a').get('href')
    npages = re.sub("[^0-9]", "", last_href)
    # Get num of items
    nitems = soup.find('p', {'class':'allRecords'}).find('strong').text
    nitems = re.sub("[^0-9]", "", nitems)
    # Get headers
    headers = list(map(clear_str, soup.find_all('th')))
    return {'num_of_pages':int(npages), 'num_of_items':int(nitems), 'headers':headers}

# Parse single file 
def parse_single_page(page):
    response = urlopen(url_prefix + str(page))
    content = response.read().decode()
    # Get all items on the page
    soup = BeautifulSoup(content, "html.parser")
    for row in soup.find_all('tr'):
        row_class = row.get('class')
        if row_class is not None and ('headTable' in row_class or 'displayNone' in row_class):
            row.decompose()
    rows = soup.find_all('tr')
    if len(rows) % 2:
        raise('The page has even number of rows!')
    nrows = len(rows)//2
    for i in range(nrows):
        vals = list(map(clear_str, rows[2*i].find_all('td'))) + list(map(clear_str, rows[2*i+1].find_all('td')))
        df.iloc[50*(page-1) + i] = vals
    return True

presets  = get_presets()
df =  pd.DataFrame(index=list(range(presets['num_of_items'])), columns=presets['headers'])
start = time()
for i in range(1,presets['num_of_pages']+1):
    t1 = time()
    parse_single_page(i)
    t2 = time()
    print('Page',i,'done! by', t2 - t1)
finish = time()
print("Total time is",finish - start)
df.to_csv('outputdata.csv', sep=';',decimal=',', index=False)
print("Total time is",time() - finish)
#print(counts)