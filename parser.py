import requests
from bs4 import BeautifulSoup
import json

URL = 'https://www.culture.ru/literature/poems'
FILE = 'poems.json'

def get_html(url):
    result = requests.get(url)
    return result

def get_pages_count(html):
    soup = BeautifulSoup(html, 'lxml')
    pagination = soup.find_all('a', {'class': 'pagination_item'})
    if pagination:
        return int(pagination[3].get_text())
    else:
        return 1

def get_data(html):
    soup = BeautifulSoup(html, 'lxml')

    poems = []
    for link in soup.find_all('div', {'class': 'entity-cards_item col'}):
        if link.find('a', {'class': 'card-heading_tag'}):
            tag = link.find('a', {'class': 'card-heading_tag'}).text
        else:
            tag = ""
        poems.append({
            'author': link.find('a', {'class': 'card-heading_subtitle'}).text,
            'tag': tag,
            'title': link.find('a', {'class': 'card-heading_title-link'}).text,
            'href': "https://www.culture.ru" + link.find('a', {'class': 'card-heading_title-link'}).get('href'),

        })


    return poems

def save_file(items, path):
    with open(path, "w") as file:
        json.dump(items, file, indent=2, ensure_ascii=False)

def main():
    html = get_html(URL)
    if html.status_code == 200:
        poems = []
        count_pages = get_pages_count(html.text)
        for page in range(1, count_pages + 1):
            print(f'Парсинг страницы {page} из {count_pages}')
            html = get_html(URL + "?page=" + str(page) +"&limit=45")
            poems.extend(get_data(html.text))
        print(f'Парсинг завершен')
        print(f'Стихов найдено {len(poems)}')
        print(poems)
        save_file(poems, FILE)
    else:
        print("Error")

if __name__ == '__main__' :
    main()