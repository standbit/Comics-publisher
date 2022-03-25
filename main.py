import os
import requests
from urllib.parse import urlparse
from save_comic import download_comic
from os.path import splitext
from dotenv import load_dotenv


def get_file_extension(link):
    link_path = urlparse(link).path
    extension = splitext(link_path)[-1]
    return extension


def fetch_comic():
    url = "https://xkcd.com/353/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    converted_response = response.json()
    comic_link = converted_response["img"]
    comic_name = converted_response["safe_title"]
    extension = get_file_extension(comic_link)
    filename = f"{comic_name}{extension}"
    download_comic(comic_link, filename)
    print(converted_response["alt"])


def main():
    load_dotenv()
    api_token = os.getenv("VK_CLIENT_ID")
    try:
        fetch_comic()
    except requests.exceptions.HTTPError as err:
        print("General Error, incorrect link\n", str(err))
    except requests.ConnectionError as err:
        print("Connection Error. Check Internet connection.\n", str(err))


if __name__ == "__main__":
    main()