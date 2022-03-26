from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def get_last_comic_num():
    url = "https://xkcd.com/"
    response = requests.get(url)
    response.raise_for_status()
    html_content = BeautifulSoup(response.text, "lxml")
    last_comic_url = html_content.body.select('a[href^="https://xkcd.com/2"]')[0].text
    last_comic_num = urlparse(last_comic_url).path.split("/")[1]
    return last_comic_num