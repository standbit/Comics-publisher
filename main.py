import os
import requests
from urllib.parse import urlparse
from save_comic import download_comic
from os.path import splitext
from dotenv import load_dotenv
from pprint import pprint


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


def get_vk_response(token):
    url = "https://api.vk.com/method/groups.get"
    payload = {
        "access_token": token,
        "v": 5.131,
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    converted_response = response.json()
    return converted_response


def get_server_address(token):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {
        "access_token": token,
        "group_id": 212094963,
        "v": 5.131,
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    converted_response = response.json()
    return converted_response


def download_img_to_server(upload_url):
    with open("Python.png", "rb") as file:
        files = {
            "photo": file,  # Вместо ключа "media" скорее всего нужно подставить другое название ключа. Какое конкретно см. в доке API ВК.
            }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
    converted_response = response.json()
    return converted_response


def main():
    load_dotenv()
    # api_token = os.getenv("VK_CLIENT_ID")
    vk_token = os.getenv("VK_ACCESS_TOKEN")
    try:
        # fetch_comic()
        # vk_groups = get_vk_response(vk_token)
        server_url = get_server_address(vk_token)["response"]["upload_url"]
        downloading_result = download_img_to_server(server_url)
        pprint(downloading_result)
    except requests.exceptions.HTTPError as err:
        print("General Error, incorrect link\n", str(err))
    except requests.ConnectionError as err:
        print("Connection Error. Check Internet connection.\n", str(err))


if __name__ == "__main__":
    main()