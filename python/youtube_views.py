import requests
import re

data = requests.get('https://socialblade.com/youtube/channel/UCiNV4S9-xDz_HnYdfY80RHA').content.decode('utf-8')
match = re.search('\{"simpleText":"([0-9,]*) views"\}', data)
#print(match.group(1))
