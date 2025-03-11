import requests
import xmltodict
from bs4 import BeautifulSoup
from celery import Celery, Task

app = Celery("test", broker="redis://0.0.0.0:6379/0", backend="redis://0.0.0.0:6379/0")


BASE_URL = "https://zakupki.gov.ru"
SEARCH_URL = BASE_URL + "/epz/order/extendedsearch/results.html?fz44=on&pageNumber={}"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"
}


class FetchGOVLinksTask(Task):
    """Класс Celery-задачи для получения ссылок на тендеры"""

    name = "test.FetchGOVLinksTask"

    def run(self, page_number):
        """Функция получает ссылки на печатные формы тендеров с указанной страницы."""
        try:
            response = requests.get(
                SEARCH_URL.format(page_number), headers=HEADERS, timeout=10
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            links = [
                BASE_URL + link["href"]
                for link in soup.find_all("a", href=True)
                if "printForm/view.html?regNumber=" in link["href"]
            ]
            for link in links:
                fetch_eis_data_task.delay(link)
            print(f"Ссылки на страничке {page_number} собраны")
        except requests.exceptions.RequestException as e:
            print(e)


class FetchEISDataTask(Task):
    """Класс Celery-задачи для получения даты публикации тендера"""

    name = "test.FetchEISDataTask"

    def run(self, link_url):
        """Функция получает дату публикации из XML-формы тендера."""
        try:
            xml_url = link_url.replace("view.html", "viewXml.html")
            response = requests.get(url=xml_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            xml_data = xmltodict.parse(response.text)
            xml_data_0 = list(xml_data.values())[0]
            data = xml_data_0.get("commonInfo", {}).get("publishDTInEIS", None)
            return f"\n{xml_url} - {data}"
        except requests.exceptions.RequestException as e:
            print(e)


fetch_gov_links_task = app.register_task(FetchGOVLinksTask())
fetch_eis_data_task = app.register_task(FetchEISDataTask())

if __name__ == "__main__":
    for page in range(1, 3):
        fetch_gov_links_task.delay(page)
