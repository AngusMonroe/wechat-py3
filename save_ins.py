# -*- coding: utf-8 -*-
import hashlib
import reply
import receive
import media
import web
import requests
from basic import Basic
import ssl
import urllib.request
import urllib.parse
import re
import os
from renewRemind import query

def download(url, local_filename):
    r = requests.get(url, stream=True)
    print("downloading...")
    with open("img/" + local_filename, 'wb') as f:
        print("opened")
        for chunk in r.iter_content(1024):
            if chunk:
                f.write(chunk)
                f.flush()
    return local_filename

url = 'https://www.instagram.com/p/BnRQqAkDstS/?utm_source=ig_share_sheet&igshid=1roesyveap1ga'
r = requests.get(url, params={'__a': 1})
_media = r.json()['graphql']['shortcode_media']
download(_media['display_url'], _media['shortcode'] + '.')
print(r)

# if (
#             (r.headers['content-type'] != 'application/json') or
#             (not 'graphql' in r.json())
# ):
#     print('error')
# else:
#     _media = r.json()['graphql']['shortcode_media']
#     if _media['is_video']:
#         print("video")
#         print('Saved as ' + download(_media['display_url'],
#                                      _media['shortcode'] + '.mp4') + '!')
#         filePath = "img/" + _media['shortcode'] + '.jpg'
#     else:
#         print("image")
#         if _media.get('edge_sidecar_to_children', None):
#             link = 'You should send a link of picture.'
#             print(link)
#             # print('Downloading mutiple images of this post')
#             # for child_node in media['edge_sidecar_to_children']['edges']:
#             #     print('Saved as ' + download(child_node['node']['display_url'],
#             #                                  child_node['node']['shortcode'] + '.jpg') + '!')
#         else:
#             print("1")
#             print('Saved as ' + download(_media['display_url'],
#                                          _media['shortcode'] + '.jpg') + '!')
#             filePath = "img/" + _media['shortcode'] + '.jpg'  # 请按实际填写
