import re, sys, os
import pandas as pd
import numpy as np
from time import time
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

# Base url for walking. Set items_on_page as big as possible to reduce number of requests.
url_prefix = 'http://zakupki.gov.ru/epz/purchaseplanfz44/purchasePlanStructuredCard/plan-position-search.html?plan-number=201701482000039002&pageSize=50&page='

# Find total number of pages
def get_num_of_pages():
    response = urlopen(url_prefix + '1')
    data = response.read().decode()

    # Num of items in a single page
    soup = BeautifulSoup(data, "html.parser")
    last_href = soup.find('ul', {'class': 'paging'}).find_all('li')[-1].find('a').get('href')
    n = re.sub("[^0-9]", "", last_href)

    total = soup.find('p', {'class':'allRecords'}).find('strong').text
    total = re.sub("[^0-9]", "", total)    
    return {'num_of_pages':int(n), 'num_of_items':int(total)}

# Parse single file 
def parse_single_page(page):
    def clear_str(x):
        clr_str = re.sub("<br>"," ",x.text)
        clr_str = re.sub("<br/>"," ",clr_str)
        clr_str = re.sub("\n","",clr_str)
        clr_str = re.sub('  +',' ', clr_str)
        return clr_str.strip()
    response = urlopen(url_prefix + str(page))
    content = response.read().decode()
    # Get all items on the page
    soup = BeautifulSoup(content, "html.parser")
    cols = soup.find_all('th')
    headers = list(map(clear_str, cols))
    for row in soup.find_all('tr'):
        row_class = row.get('class')
        if row_class is not None and ('headTable' in row_class or 'displayNone' in row_class):
            row.decompose()
    rows = soup.find_all('tr')
    if len(rows) % 2:
        raise('The page has even number of rows!')
    nrows = len(rows)//2
    df =  pd.DataFrame(index=list(range(nrows)), columns=headers)
    for i in range(nrows):
        vals = list(map(clear_str, rows[2*i].find_all('td'))) + list(map(clear_str, rows[2*i+1].find_all('td')))
        df.iloc[i] = vals
    return df

counts  = get_num_of_pages()

start = time()
t1 = time()
df = parse_single_page(1)
t2 = time()
print('Page 1 done! by', t2 - t1)
for i in range(2,counts['num_of_pages']+1):
    t1 = time()
    df = df.append(parse_single_page(i))
    t2 = time()
    print('Page',i,'done! by', t2 - t1)
finish = time()
print("Total time is",finish - start)
df.to_csv('outputdata.csv', sep=';',decimal=',', index=False)
print("Total time is",time() - finish)
print(counts)