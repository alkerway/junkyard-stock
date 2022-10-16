from bs4 import BeautifulSoup as Soup
import requests
import re
from dateutil import parser
from datetime import datetime

yards = [
    {
        'name': 'Avondale',
        'url': 'https://www.pickapart.co.nz/Avondale-Stock'
    },
    {
        'name': 'Mangere',
        'url': 'https://www.pickapart.co.nz/Mangere-Stock'
    },
    {
        'name': 'Takanini',
        'url': 'https://www.pickapart.co.nz/Takanini-Stock'
    }
]

def getCarInfo(carUrl):
    carHtml = requests.get(carUrl).text
    carSoup = Soup(carHtml, 'html.parser')
    infoTags = carSoup.find_all('div', class_='detail-info')

    date = None
    name = None
    for tag in infoTags:
        tagString = str(tag.string)
        if re.search('[0-9]{1,2} [A-Za-z]{3} [0-9]{4}', tagString):
            date = parser.parse(tagString)
        elif re.search('TCR(10|11|20|21)', tagString):
            name = tagString.replace(',', '')
    
    return {
        'arrivalDate': date,
        'name': name
    }

def getAllCarInfosFromSubpage(seriesUrl):
    subpageHtml = requests.get(seriesUrl).text
    subpageSoup = Soup(subpageHtml, 'html.parser')
    carElements = subpageSoup.find_all('div', class_='car-detail-search')

    carInfos = []
    for car in carElements:
        carLink = car.find('a')
        carInfos.append(getCarInfo(carLink['href']))

    return carInfos

def getCarsInYard(yardUrl):
    htmlResponse = requests.get(yardUrl).text
    document = Soup(htmlResponse, 'html.parser')
    yardUrlBase = '/'.join(yardUrl.split('/')[:3])

    cars = []
    for linkTag in document.find_all('a'):
        linkText = str(linkTag.string)
        if re.search('TCR(10|11|20|21)', linkText):
            fullHref = yardUrlBase + '/' + linkTag['href'][3:]
            modelName = ' '.join(linkText.split(' ')[:-1])
            if '(1)' in linkText:
                carInfo = getCarInfo(fullHref)
                cars.append(carInfo)
            else:
                cars += getAllCarInfosFromSubpage(fullHref)
    
    return cars

for yard in yards:
    print(yard['name'])
    carsInYard = getCarsInYard(yard['url'])
    for car in carsInYard:
        carDate = car['arrivalDate']
        timeDiff = (datetime.now() - carDate).days
        print(f"{car['name'].ljust(19, ' ')} - {timeDiff} days ago")
    print('---')
