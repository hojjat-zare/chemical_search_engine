import requests
from bs4 import BeautifulSoup
import os
def catch_strings(tag):
    answer=""
    for string in tag.stripped_strings:
        answer = answer+string
    return answer
dirname = os.path.dirname(__file__)
file_path = os.path.join(dirname, 'wikipedia periodic table elements links.txt')
links_file=open(file_path,'r')
file_path = os.path.join(dirname, 'main properties.txt')
csv_storing_file = open(file_path,'r')
csv_headers = csv_storing_file.readline().replace('\n','')
csv_headers = csv_headers.split(" && ")
csv_storing_file.close
csv_storing_file = open(file_path,'a')
links = links_file.readlines();
links_file.close
# links = links[:5:]
# print(links)
a = 1
for link in links:
    a+=1
    link = link.replace('\n','')
    html = requests.get(link)
    bs = BeautifulSoup(html.text, 'html.parser')
    properties_table = bs.find('tr',string='Physical properties').parent
    table_rows = properties_table.find_all('tr')
    buffer = {}
    for header in csv_headers:
        buffer[header] = ""
    buffer[csv_headers[0]] = link.split("/")[len(link.split("/"))-1]
    for row in table_rows:
        first = row.find("th")
        second = row.find("td")
        if(first!=None and second!=None):
            first_string = catch_strings(first)
            second_string = catch_strings(second)
            for i in range(1, len(csv_headers)):
                if(csv_headers[i] in first_string):
                    buffer[csv_headers[i]] = second_string
    new_line = ""
    print(buffer)
    for key in buffer:
        if(buffer[key] == ''):
            buffer[key] = "None"
        new_line = new_line + buffer[key] + " && "
    new_line = new_line[:-4:]
    new_line = new_line + "\n"
    # breakpoint()
    csv_storing_file.write(new_line)
    if(a==4):
        break
csv_storing_file.close
