import sys

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = 'https://news.kbs.co.kr'
MAIN_PAGE_URL = 'https://news.kbs.co.kr/news/pc/main/main.html'


def fetch_headlines():
    response = requests.get(MAIN_PAGE_URL, timeout=10)
    response.raise_for_status()
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')
    container = soup.find('div', class_='main-page-head-line')
    if not container:
        return []

    headlines = []
    for link in container.find_all('a', href=True):
        title_tag = link.find(class_='title')
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        summary_tag = link.find(class_='news-txt')
        summary = summary_tag.get_text(strip=True) if summary_tag else ''
        url = urljoin(BASE_URL, link['href'])

        headlines.append({
            'title': title,
            'summary': summary,
            'url': url,
        })

    return headlines


def main():
    try:
        headlines = fetch_headlines()
    except requests.RequestException as exc:
        print(f'뉴스를 가져오는 동안 오류가 발생했습니다: {exc}')
        return

    if not headlines:
        print('헤드라인 뉴스를 찾을 수 없습니다.')
        return

    for index, item in enumerate(headlines, 1):
        print(f'{index}. {item["title"]}')
        if item['summary']:
            print(f'   - 요약: {item["summary"]}')
        print(f'   - 링크: {item["url"]}')


if __name__ == '__main__':
    main()
