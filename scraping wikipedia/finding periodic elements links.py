import requests
from bs4 import BeautifulSoup
html = requests.get('https://en.wikipedia.org/wiki/Periodic_table')
bs = BeautifulSoup(html.text, 'html.parser')
nameList = bs.body.find('div',id='micro-periodic-table-title')
periodic_table = nameList.next_sibling.next_sibling
elements_link=periodic_table.find_all('a')
print(len(elements_link))
for link in elements_link:
    print('https://en.wikipedia.org'+link['href'])
# print(nameList.parent.contents[3])
