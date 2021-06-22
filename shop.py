from sqlite3.dbapi2 import DateFromTicks
from bs4 import BeautifulSoup
import requests
import re
import sqlite3
from lxml import etree as et
from datetime import datetime
import json


class Database() :

    databasePath = "/Users/ilyachuiko/Desktop/dev/sneakershop/db/sneakerdb.db"

    """CREATE TABLE sneakers (id text , title text, description text , sizes text , photos text, price text)"""
    """CREATE TABLE cities (id text , city text , address text)"""

    def updateProduct(self, productInfo:dict) -> None :
        #проверяем по id , есть ли уже такая запись 
        conn = sqlite3.connect(self.databasePath)
        cursor = conn.cursor()
        
        query = f"""SELECT * FROM sneakers WHERE id = '{productInfo['id']}' """
        request = cursor.execute(query)

        #если записи нет, добавляем
        if len(request.fetchall()) == 0 :
            sizes = ''
            
            for size in productInfo['sizes'] :
                sizes += size 
                sizes += ','

            photos = ''
            
            for photo in productInfo['photos'] :
                photos += photo
                photos += ','

            query = f"""INSERT INTO TABLE sneakers VALUES ('{productInfo['id']}', '{productInfo['title']}', '{productInfo['description']}' , '{sizes}','{photos}', '{productInfo['price']}' )"""

            cursor.execute(query)
            conn.commit()
        #если запись есть, обновляем
        else:
            sizes = ''
            
            for size in productInfo['sizes'] :
                sizes += size 
                sizes += ','

            query = f"""UPDATE sneakers SET sizes = '{sizes}' WHERE '{productInfo['id']}'"""

            cursor.execute(query)
            conn.commit()
  
class CreateXml() :

    jsonFilename = '/Users/ilyachuiko/Desktop/dev/sneakershop/producty.json'

    #Настройки выгрузки Авито
    allowEmail = 'Да'
    managerName = 'Иван Алексеев'
    contactPhone = '89995862639'
    address = 'Россия, Челябинская область, Челябинск, Ленина улица , 18'
    category = 'Одежда, обувь, аксессуары'
    goodsType = 'Мужская одежда'
    apparel = 'Обувь'
    condition = 'Новое'

    #Данная выгрузка подходит также и под Яндекс Объявления
    def avito(self) -> None :
        exportFilename = '/Users/ilyachuiko/Desktop/dev/sneakershop/avitoExport.xml'
        root = et.Element('Ads', formatVersion="3", target="Avito.ru")
        
        with open(self.jsonFilename, 'r') as file:
            data = json.loads(file.read())

            for item in data :

                ad = et.SubElement(root, 'Ad')
                
                productId  = et.SubElement(ad, 'Id')
                productId.text = data[item]['id']
                avitoId = et.SubElement(ad, 'AvitoId')
                avitoId.text = data[item]['id']

                allowEmail = et.SubElement(ad, 'AllowEmail')
                allowEmail.text = self.allowEmail

                managerName = et.SubElement(ad, 'ManagerName')
                managerName.text = self.managerName

                contactPhone = et.SubElement(ad, 'ContactPhone')
                contactPhone.text = self.contactPhone

                address = et.SubElement(ad, 'Address')
                address.text = self.address

                category = et.SubElement(ad, 'Category')
                category.text = self.category

                goodsType = et.SubElement(ad, 'GoodsType')
                goodsType.text = self.goodsType

                apparel = et.SubElement(ad, 'Apparel')
                apparel.text = self.apparel

                size = et.SubElement(ad, 'Size')
                size.text = data[item]['sizes'][0]

                condition = et.SubElement(ad, 'Condition')
                condition.text = self.condition

                title = et.SubElement(ad, 'Title')
                title.text = data[item]['title']

                description = et.SubElement(ad, 'Description')
                description.text = data[item]['description']

                price = et.SubElement(ad, 'Price')
                price.text = str(data[item]['price'])

                images = et.SubElement(ad, 'Images')
                imageList = data[item]['photos']
                for image in imageList :
                    tag = et.SubElement(images, 'Image' , url=image)

        tree = et.ElementTree(root)
        tree.write(exportFilename, pretty_print=True, xml_declaration=True,   encoding="utf-8")
        print('ready')
        #print (et.tostring(root, pretty_print=True).decode("utf-8")) 


class Parser() :

    headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'    
        }

    descriptionText = 'В объявлении указан наименьший размер! Остальные размеры также в наличии ! Если вы не нашли ваш размер, напишите нам, мы подберем подходящий или предложим другой вариант кроссовок! Также у нас есть скидки постоянным покупаетлям и сезонные акции!'
    additionalPrice = 700

    txtFilename = '/Users/ilyachuiko/Desktop/dev/sneakershop/links.txt'
    jsonFilename = '/Users/ilyachuiko/Desktop/dev/sneakershop/products.json'

    def getPagesCount(self, string:str) :
        index = string.rfind(')')
        newIndex = index - 2
        pagesCount = int(string[newIndex:index])

        return pagesCount

    def getProductsList(self, url:str) -> list :
        html = requests.get(url, headers=self.headers)
        html.encoding = 'utf-8'
        soup = BeautifulSoup(html.text, 'lxml')

        cards = soup.find_all('div', id='grid-image-block')
        links = []

        #getting all pages
        pageString = soup.find('div', class_='results').text
        pagesCount = self.getPagesCount(pageString)

        for card in cards :
            link = card.find('a')['href']
            links.append(link)

        for i in range(pagesCount + 1):
            if i <= 1 :
                continue
            else:
                pageUrl = f'{url}?page={str(i)}#category_id=1&path=1789_1&sort=p.sort_order&order=DESC&limit=60&min_price=0'
                print(pageUrl)
                html = requests.get(pageUrl, headers=self.headers)
                html.encoding = 'utf-8'
                soup = BeautifulSoup(html.text, 'lxml')

                cards = soup.find_all('div', id='grid-image-block')

                for card in cards :
                    link = card.find('a')['href']
                    links.append(link)

        with open(self.txtFilename, 'w') as file :

            for elem in links :
                string = elem + '\n'
                file.write(string)
        print('ready getLinks')
        
        return links
    
    def createDescription(self, url:str) -> str :
        
        html = requests.get(url, headers=self.headers)
        html.encoding = 'utf-8'
        soup = BeautifulSoup(html.text, 'lxml')


        seasons = soup.find_all('div', class_='attributes_name')
        preSeason = seasons[1].find('label', class_='attributes_text')
        season = preSeason.text
        seasonText = 'Сезон: ' + season
        material = seasons[2].find('label', class_='attributes_text')
        preMaterial = material.text
        materialText = 'Материал : ' + preMaterial

        descriptionText = seasonText + '\n' + materialText + '\n\n'
        description = soup.find('div', class_='tab-content').text
        descriptionText += description + '\n'
        descriptionText += self.descriptionText

        return descriptionText

    def getInfoFromPage(self, url:str) -> dict :
        html = requests.get(url, headers=self.headers)
        html.encoding = 'utf-8'
        soup = BeautifulSoup(html.text, 'lxml')

        #финальные значения, которые записываются в базу, идут с названием product

        indexId = url.rfind('=')
        productId = url[indexId + 1:]
        
        breadcrumbs = soup.find('div', class_='breadcrumb')
        title  = breadcrumbs.find_all('a')
        productTitle = title[-1].text
        
        productPhotos = []
        

        photoTable = soup.find('div', class_='product-info')
        photos = photoTable.find_all('img')
            
        for photo in photos :
            if photo['src'][0] == 'i' :
                link = 'https://bizoutmax.ru/' + photo['src']
                productPhotos.append(link)
            elif photo['src'][0] == '/' :
                continue
            else : 
                productPhotos.append(photo['src'])
        
        productSizes = []
        sizeTable = soup.find('div', class_='option')
        sizes = sizeTable.find_all('label')

        for size in sizes :
            productSizes.append(size.text[0:2])
        
        productDescription = self.createDescription(url)

        price = soup.find('span', class_='price-default')

        defaultPrice = ''

        for i in price.text :
            try :
                k = int(i)
                defaultPrice += str(k)
            except ValueError:
                exception = ''
        
        
        productPrice = int(defaultPrice) + self.additionalPrice
    
        productInfo = {
            'id' : productId, #str
            'title' : productTitle, #str
            'price' : productPrice, #str
            'description' : productDescription, #str
            'sizes' : productSizes, #list
            'photos' : productPhotos, #list
        }
        print(f'ready product {productId}')

        return productInfo

    def startParser(self) :
        
        #products = {}

        with open(self.txtFilename, 'r') as file :
            for url in file :
                print(url)
                info = self.getInfoFromPage(url)
                with open(self.jsonFilename, 'r') as filet :
                    data = json.loads(filet.read())
                    tovar = info['id']
                    data[tovar] = info

                with open(self.jsonFilename, 'w') as filed :
                    products = json.dumps(data)
                    filed.write(products)
                
aww = Parser()
aww.getProductsList(url='https://bizoutmax.ru/krossovki_katalog/muzhskie_krossovki_katalog/')
#aww.getInfoFromPage('https://bizoutmax.ru/index.php?route=product/product&path=1789_1_117&product_id=23754')
#aww.createDescription('https://bizoutmax.ru/index.php?route=product/product&path=1789_1_1790&product_id=24313')
#aww.createDescription('https://bizoutmax.ru/index.php?route=product/product&path=1789_1_1790&product_id=24257')
#av = CreateXml()
#av.avito()
#aww.startParser()