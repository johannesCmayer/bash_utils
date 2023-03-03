import requests
import re

data = requests.get('https://www.youtube.com/@johannesCmayer/about').content.decode('utf-8')
match = re.search('"viewCountText":\{"simpleText":"([0-9,]*) views"\}', data)
print(match.group(1))