import os
import random
from os.path import splitext
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


def get_file_extension(link):
    link_path = urlparse(link).path
    extension = splitext(link_path)[-1]
    return extension


def get_last_comic_num():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    last_comic_num = response.json()["num"]
    return last_comic_num


def download_comic(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, "wb") as file:
        file.write(response.content)


def fetch_comic():
    first_comic_num = 1
    last_comic_num = int(get_last_comic_num())
    comic_num = random.randint(first_comic_num, last_comic_num)
    url = f"https://xkcd.com/{comic_num}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    converted_response = response.json()
    comments = converted_response["alt"]
    comic_link = converted_response["img"]
    extension = get_file_extension(comic_link)
    comic_name = converted_response["safe_title"]
    filename = f"{comic_name}{extension}"
    download_comic(comic_link, filename)
    return filename, comments


def get_server_link(token):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {
        "access_token": token,
        "group_id": 212094963,
        "v": 5.131,
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    server_link = response.json()["response"]["upload_url"]
    return server_link


def upload_img_to_server(filename, upload_url):
    with open(filename, "rb") as file:
        files = {
            "photo": file,
            }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
    server_response = response.json()
    return server_response


def download_img_to_group(token, server_response):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    payload = {
        "access_token": token,
        "group_id": 212094963,
        "v": 5.131,
        "photo": server_response["photo"],
        "server": server_response["server"],
        "hash": server_response["hash"]
    }
    response = requests.post(
        url,
        params=payload)
    response.raise_for_status()
    vk_response = response.json()
    return vk_response


def publish_comic(token, loaded_result, comments):
    url = "https://api.vk.com/method/wall.post"
    owner_id = loaded_result["response"][0]["owner_id"]
    media_id = loaded_result["response"][0]["id"]
    payload = {
        "owner_id": -212094963,
        "from_group": 1,
        "message": comments,
        "access_token": token,
        "v": 5.131,
        "attachments": f"photo{owner_id}_{media_id}"
        }
    response = requests.post(url, params=payload)
    response.raise_for_status()


def main():
    load_dotenv()
    vk_token = os.getenv("VK_ACCESS_TOKEN")
    try:
        filename, comments = fetch_comic()
        server_link = get_server_link(vk_token)
        server_response = upload_img_to_server(filename, server_link)
        vk_response = download_img_to_group(vk_token, server_response)
        publish_comic(vk_token, vk_response, comments)
        os.remove(f"./{filename}")
    except requests.exceptions.HTTPError as err:
        print("General Error, incorrect link\n", str(err))
    except requests.ConnectionError as err:
        print("Connection Error. Check Internet connection.\n", str(err))
    except OSError as err:
        print("Error: %s - %s." % (err.filename, err.strerror))


if __name__ == "__main__":
    main()
