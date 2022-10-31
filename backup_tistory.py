from pathlib import Path
import argparse
import requests
import urllib.request
import json
import re
import imghdr
import os
import tistory_apis

# https://docs.python.org/ko/3/howto/argparse.html
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--access_token", required=True)
parser.add_argument("-n", "--blog_name", required=True)
parser.add_argument("-f", "--filename_type", choices=['title', 'id'], default='title')
args = parser.parse_args()

OUTPUT_TYPE = 'json'
ACCESS_TOKEN = args.access_token
BLOG_NAME = args.blog_name
FILENAME_TYPE = args.filename_type

params_for_post_list = tistory_apis.ParamsForPostList(access_token=ACCESS_TOKEN,
                                                      blog_name=BLOG_NAME,
                                                      output=OUTPUT_TYPE,
                                                      page=1)
# https://requests.readthedocs.io
response = requests.get(url=tistory_apis.BLOG_POST_LIST, params=params_for_post_list.get_params())
if not response.ok:
    response.raise_for_status()

json_result = response.json()
COUNT = int(json_result['tistory']['item']['count'])
TOTAL_COUNT = int(json_result['tistory']['item']['totalCount'])
END_PAGE = TOTAL_COUNT // COUNT + (1 if TOTAL_COUNT % COUNT > 0 else 0)

total_post_ids = []
for page in range(1, END_PAGE + 1):
    params_for_post_list.page = page
    response = requests.get(url=tistory_apis.BLOG_POST_LIST, params=params_for_post_list.get_params())
    json_result = response.json()
    post_ids = [item['id'] for item in json_result['tistory']['item']['posts']]
    total_post_ids += post_ids

Path("posts").mkdir(exist_ok=True)
Path("images").mkdir(exist_ok=True)

# https://docs.python.org/ko/3/library/re.html
# https://softhints.com/match-text-between-two-strings-regex-in-python/
REX_URL = re.compile(pattern="img src=[\"'](http.*?)[\"']")
REPLACE_TABLE = {
    '/': '_'
}

downloaded_count = 0
downloaded_failed_list = []

for post_id in total_post_ids:
    params_for_post_read = tistory_apis.ParamsForPostRead(access_token=ACCESS_TOKEN,
                                                          blog_name=BLOG_NAME,
                                                          output=OUTPUT_TYPE,
                                                          post_id=post_id)
    response = requests.get(url=tistory_apis.BLOG_POST_READ, params=params_for_post_read.get_params())
    json_result = response.json()
    json_object = json.dumps(obj=json_result, indent=4, ensure_ascii=False)
    post_file_name = json_result['tistory']['item'][FILENAME_TYPE]

    for k, v in REPLACE_TABLE.items():
        post_file_name = post_file_name.replace(k, v)

    with open(file=f"posts/{post_file_name}.json", mode="w", encoding="utf-8") as outfile:
        outfile.write(json_object)
        downloaded_count += 1
        print(f"downloaded({downloaded_count}/{TOTAL_COUNT}) post to posts/{post_file_name}.json")

    # https://docs.python.org/ko/3/library/urllib.request.html#urllib.request.urlretrieve
    # https://www.scrapingbee.com/blog/download-image-python/
    content = json_result['tistory']['item']['content']
    image_url_list = REX_URL.findall(content)
    for idx in range(len(image_url_list)):
        image_file_name = f"{post_file_name}_{idx}"
        try:
            urllib.request.urlretrieve(url=image_url_list[idx], filename=f"images/{image_file_name}")
            file_ext = imghdr.what(f"images/{image_file_name}")
            os.rename(f"images/{image_file_name}", f"images/{image_file_name}.{file_ext}")
            print(f"downloaded images/{image_file_name}.{file_ext}")
        except:
            downloaded_failed_list.append((post_file_name, image_url_list[idx]))

for post_file_name, image_url in downloaded_failed_list:
    print(f"image download failed : {post_file_name} - {image_url}")
