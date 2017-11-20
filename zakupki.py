import re, csv
import pandas as pd
from time import time
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import pandas.io.formats.excel

# Clear html element
def clear_str(x):
    clr_str = re.sub("<br>"," ",x.text)
    clr_str = re.sub("<br/>"," ",clr_str)
    clr_str = re.sub("Просмотреть","",clr_str)
    clr_str = re.sub("\n","",clr_str)
    clr_str = re.sub('  +',' ', clr_str)
    return clr_str.strip()

base_url = 'http://zakupki.gov.ru/epz/purchaseplanfz44/purchasePlanStructuredCard/plan-position-search.html'
parameters = {'plan-number':'201701482000039002', 'pageSize':'50'}
url_prefix = base_url + '?' + '&'.join(["%s=%s"%(k,v) for k,v in parameters.items()]) + '&page='

# Find total number of pages
response = urlopen(url_prefix + '1')
data = response.read().decode()
soup = BeautifulSoup(data, "html.parser")
# Get num of pages
last_href = soup.find('ul', {'class': 'paging'}).find_all('li')[-1].find('a').get('href')
num_of_pages = int(re.sub("[^0-9]", "", last_href))
# Get num of items
num_of_items = soup.find('p', {'class':'allRecords'}).find('strong').text
num_of_items = int(re.sub("[^0-9]", "", num_of_items))
# Get headers
headers = list(map(clear_str, soup.find_all('th')))

df =  pd.DataFrame(index=list(range(num_of_items)), columns=headers)
start = time()
for i in range(1,3):#num_of_pages+1):
    t1 = time()
    response = urlopen(url_prefix + str(i))
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
    for j in range(nrows):
        vals = list(map(clear_str, rows[2*j].find_all('td'))) + list(map(clear_str, rows[2*j+1].find_all('td')))
        df.iloc[50*(i-1) + j] = vals
    t2 = time()
    print('Page',i,'done! by', t2 - t1)
finish = time()
print("Total time is",finish - start)
#df.to_csv('outputdata.csv', sep=';',decimal=',', index=False, quoting=csv.QUOTE_ALL)
pandas.io.formats.excel.header_style = None
writer = pd.ExcelWriter("outputdata.xlsx", engine='xlsxwriter')
df.to_excel(writer, sheet_name='Закупки', index=False)
workbook  = writer.book
worksheet = writer.sheets['Закупки']

# Add some cell formats.
format_header   = workbook.add_format({'border': 1, "font_name": "Times New Roman", "font_size":10, 'text_wrap':True, 'bold': True, 'bg_color':'#66C2FF'})
format_year     = workbook.add_format({'border': 1, "font_name": "Times New Roman", "font_size":10})
format_number   = workbook.add_format({'border': 1, "font_name": "Times New Roman", "font_size":10})
format_name     = workbook.add_format({'border': 1, "font_name": "Times New Roman", "font_size":10, 'text_wrap':True})
format_code     = workbook.add_format({'border': 1, "font_name": "Times New Roman", "font_size":10, 'text_wrap':True})
format_money    = workbook.add_format({'border': 1, "font_name": "Times New Roman", "font_size":10, 'num_format': '# ##0,00'})
format_status   = workbook.add_format({'border': 1, "font_name": "Times New Roman", "font_size":10, 'text_wrap':True})
format_discuss  = workbook.add_format({'border': 1, "font_name": "Times New Roman", "font_size":10})
format_position = workbook.add_format({'border': 1, "font_name": "Times New Roman", "font_size":10, 'text_wrap':True})
format_id       = workbook.add_format({'border': 1, "font_name": "Times New Roman", "font_size":10})

# Apply formating
worksheet.set_column('A:A', 11, format_year)
worksheet.set_column('B:B', 11, format_number)
worksheet.set_column('C:C', 25, format_name)
worksheet.set_column('D:D', 25, format_code)
worksheet.set_column('E:E', 16, format_money)
worksheet.set_column('F:F', 10, format_status)
worksheet.set_column('G:G', 17, format_discuss)
worksheet.set_column('H:H', 11, format_position)
worksheet.set_column('I:I', 37, format_id)
worksheet.set_row(0, None, format_header)
worksheet.autofilter(0, 0, num_of_items+1,8)
writer.save()
print("Writing time is",time() - finish)
