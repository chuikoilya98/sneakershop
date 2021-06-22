import json
from bs4 import BeautifulSoup
import requests

url = 'https://bizoutmax.ru/index.php?route=module/filterpro/getproducts'
req = requests.get(url)
data = req.content
print(data)

with open('test.html' , 'w', encoding='utf-8') as file :
    file.write(str(data))
