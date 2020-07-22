'''Для запуска скрипта раз в неделю, нужно будет настроить планировщик задач, например cron'''
import requests
from bs4 import BeautifulSoup
import csv


url = 'https://gazoncity.ru/catalog/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'accept': '*/*'
}
HOST = 'https://gazoncity.ru'
FILE = 'gazoncity.csv'


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('ul', class_='pagination').find_all('a')[-2]
    if pagination:
        return int(pagination.get_text())
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='col-md-12 col-sm-12 col-xs-12')
    product = []
    url_product = []

    for url in items:
        url_product.append(HOST + url.find('div', class_='title').find_next('a').get('href'))

    for item in url_product:
        weight = 0
        height, length, width = 0, 0, 0
        soup = BeautifulSoup(requests.get(item).text, 'html.parser')
        product_items = soup.find_all('tr', class_='char')
        title = soup.find(id='pagetitle').get_text()
        price = soup.find('span', class_='price_val').get_text()
        img = HOST + soup.find('li', class_='col-md-1 col-sm-1 item').find_next('img').get('src')
        description = soup.find('div', class_='previewtext').get_text(strip=True)
        for i in product_items:
            name = i.find('td', class_='char_name').get_text(strip=True)
            if 'Упаковка' in name:
                weight = i.find('td', class_='char_value').get_text(strip=True) + 'кг'
            if 'Высота' in name:
                height = i.find('td', class_='char_value').get_text(strip=True)
            elif 'Длина' in name:
                length = i.find('td', class_='char_value').get_text(strip=True)
            elif 'Ширина' in name:
                width = i.find('td', class_='char_value').get_text(strip=True)

        product.append(
                {
                    'title': title,
                    'price': price,
                    'img': img,
                    'height': height,
                    'length': length,
                    'width': width,
                    'weight': weight,
                    'description': description,
            }
            )
    return product


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['название', 'цена', 'url-картинки', 'габариты', 'вес', 'Описание'])
        for item in items:
            writer.writerow(
                [
                    item['title'],
                    item['price'],
                    item['img'],
                    str(item['height'])+str('*')+str(item['length'])+str('*')+str(item['width']),
                    item['weight'],
                    item['description']
                ]
            )


def parser():
    html = get_html(url)
    if html.status_code == 200:
        product = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}')
            html = get_html(url, params={'PAGEN_1': page})
            product.extend(get_content(html.text))
        save_file(product, FILE)
        print(product)
    else:
        print('Error')


parser()
