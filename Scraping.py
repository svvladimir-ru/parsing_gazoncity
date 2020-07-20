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

    for item in items:
        product.append({
            'title': item.find('div', class_='title').get_text(strip=True),
            'price': item.find('span', class_='price_val').get_text(),
            'img': HOST + item.find('a', class_='blink').get('href'),
            'description': item.find('div', class_='description').get_text(strip=True).replace('Для перехода в карточку товара с подробным описанием кликните по заголовку', ''),
        })
    return product


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['название', 'цена', 'url-картинки', 'Описание(вес, габариты)'])
        for item in items:
            writer.writerow(
                [
                    item['title'],
                    item['price'],
                    item['img'],
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
