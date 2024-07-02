import requests
from bs4 import BeautifulSoup
import csv
from tqdm import tqdm
import re

def sanitize_filename(name):
    return re.sub(r'[^\w-]', '_', name)

def get_categories():
    categories = []
    response = requests.get('https://www.microwavejournal.com/')
    if response.status_code != 200:
        raise Exception("Failed to load the webpage")

    bs = BeautifulSoup(response.text, 'html.parser')
    for i in bs.find(class_='navigation').find_all(class_='level1-li'):
        if 'Channels' in i.find('a')['data-eventlabel']:
            num = 0
            for j in i.find(class_='level2').find_all(class_='level2-li'):
                href = j.find('a')['href']
                id_match = re.search(r'\d+', href)
                if id_match:
                    categories.append((num, j.find('a')['data-eventlabel'][6:j.find('a')['data-eventlabel'].find('|')], id_match.group()))
                    num += 1
    return categories

def get_titles(bs):
    return bs.find_all(class_='headline article-summary__headline')

def get_date(bs):
    return bs.find_all(class_='date article-summary__post-date')

def get_full_text(bs):
    return bs.find_all(class_='abstract article-summary__teaser')

def get_links(bs):
    return bs.find_all(class_='headline article-summary__headline')

def parse(pages, id, name):
    data = []

    for page in tqdm(range(1, pages + 1)):
        response = requests.get(f'https://www.microwavejournal.com/articles/topic/{id}?page={page}')
        if response.status_code != 200:
            print(f"Невозможно загрузить страницу {page}")
            continue

        bs = BeautifulSoup(response.text, 'html.parser')
        titles, date, full_text, links = get_titles(bs), get_date(bs), get_full_text(bs), get_links(bs)

        for i in range(len(titles)):
            title = titles[i].find('a').text
            date_text = date[i].text
            link = links[i].find('a')['href']

            if i < len(full_text):
                full_text_p = full_text[i].find('p')
                if full_text_p:
                    full_text_content = full_text_p.text
                else:
                    full_text_content = "N/A"
            else:
                full_text_content = "N/A"

            data.append([title, date_text, full_text_content, link])

    sanitized_name = sanitize_filename(name)
    with open(f'{sanitized_name}.csv', 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['title', 'date', 'full_text', 'link'])
        csv_writer.writerows(data)

if __name__ == '__main__':
    print('Выберите категорию, статьи которой вы хотите спарсить:')

    categories = get_categories()
    for category in categories:
        print(f'{category[0]} - {category[1]}')

    choice = int(input(f'Отправьте цифру от 0 до {categories[-1][0]}, чтобы выбрать желаемую статью\n'))
    pages = int(input('Введите количество желаемых страниц, которые вы хотите спарсить:\n'))
    print('Пожалуйста, подождите...')
    parse(pages, categories[choice][2], categories[choice][1])
    print(f'Парсинг завершен! Файл {sanitize_filename(categories[choice][1])}.csv сохранен в вашу корневую директорию.')