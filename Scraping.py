import requests
from bs4 import BeautifulSoup


url = 'https://gazoncity.ru/catalog/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'accept': '*/*'
}
HOST = 'https://gazoncity.ru'

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


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


def parse():
    html = get_html(url)
    if html.status_code == 200:
        product = get_content(html.text)
        return product
    else:
        print('Error')

print(parse())