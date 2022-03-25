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
    return converted_response["alt"]


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
            "photo": file,
            }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
    converted_response = response.json()
    return converted_response


def download_img_to_group(token, server_data):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    payload = {
        "access_token": token,
        "group_id": 212094963,
        "v": 5.131,
        "photo": server_data["photo"],
        "server": server_data["server"],
        "hash": server_data["hash"]
    }
    response = requests.post(
        url,
        params=payload)
    response.raise_for_status()
    converted_response = response.json()
    return converted_response


def publish_comic(token, photo_data, comments):
    url = "https://api.vk.com/method/wall.post"
    owner_id = photo_data["response"][0]["owner_id"]
    media_id = photo_data["response"][0]["id"]
    payload = {
        "owner_id": -212094963,
        "from_group": 1,
        "message": comments,
        "access_token": token,
        "v": 5.131,
        "attachments": f"photo{owner_id}_{media_id}"
        }
    r = requests.post(url, params=payload)
    r.raise_for_status()
    return r


def main():
    load_dotenv()
    vk_token = os.getenv("VK_ACCESS_TOKEN")
    try:
        comments = fetch_comic()
        server_url = get_server_address(vk_token)["response"]["upload_url"]
        downloading_result = download_img_to_server(server_url)
        vk_response = download_img_to_group(vk_token, downloading_result)
        print(vk_response["response"][0]["id"], vk_response["response"][0]["owner_id"])
        r = publish_comic(vk_token, vk_response, comments)
        print(r.url, r.status_code)
    except requests.exceptions.HTTPError as err:
        print("General Error, incorrect link\n", str(err))
    except requests.ConnectionError as err:
        print("Connection Error. Check Internet connection.\n", str(err))


if __name__ == "__main__":
    main()