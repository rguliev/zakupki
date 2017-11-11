import re, sys, os, csv
import pandas as pd
import numpy as np
from time import time
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import pandas.io.formats.excel

df = pd.DataFrame({
    'Планируемыйгодразмещенияизвещения': ['2017', '2017','2017'],
    'Номер закупки включенной в план закупок': ['0708', '1038', '1325'],
    'Наименование объекта закупки': ['Специализированный продукт детского лечебного питания "Нутриген 75" 500 г. (для детей старше 1 года)', 'Аминофенилмасляная кислота таблетки, 250мг №20','Закупка услуг связи (Управление №13)'],
    'КОД ОКПД2 В ИКЗ ПОЗИЦИИ ПЛАНА ЗАКУПОК': ['10.89:Продукты пищевые прочие, не включенные в другие группировки', '20.14:Вещества химические органические основные прочие','61.10:Услуги телекоммуникационные проводные'],
    'ОБЪЕМ ФИНАНСОВОГО ОБЕСПЕЧЕНИЯ (РУБЛЕЙ)': ['12765816,00', '510207,50','10500,00'],
    'Статус': ['Размещена 10.11.2017', 'Размещена 10.11.2017', 'Размещена 10.11.2017'],
    'ОБЯЗАТЕЛЬНОЕ ОБЩЕСТВЕННОЕ ОБСУЖДЕНИЕ': ['Не проводилось', 'Не проводилось','Не проводилось'],
    'Номер закупки, включенной в план-график': ['011 012', '002','001'],
    'Идентификационный код закупки': ['172500000116250240100107080001089244', '172500000116250240100110380002014244','172500000116250240100113250006110244']
})

pandas.io.formats.excel.header_style = None
writer = pd.ExcelWriter("outputdata_test.xlsx", engine='xlsxwriter')
df.to_excel(writer, sheet_name='Закупки', index=False)
workbook  = writer.book
worksheet = writer.sheets['Закупки']

# Add some cell formats.
format_longtext = workbook.add_format({'text_wrap':True, 'border': 1})
format_header   = workbook.add_format({'text_wrap':True, 'bold': True, 'bg_color':'#66C2FF', 'border': 1})
format_fin      = workbook.add_format({'num_format': '# ##0,00', 'border': 1})

worksheet.set_column('A:I', 15, format_longtext)
worksheet.set_column('C:D', 15, format_longtext)
worksheet.set_column('E:E', 15, format_fin)
worksheet.set_row(0, None, format_header)
writer.save()