# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 11.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies
import re
import random

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

# DH_KEY_TOO_SMALL on android fix by https://stackoverflow.com/questions/38015537/python-requests-exceptions-sslerror-dh-key-too-small#76217135
try:
    from urllib3.util import create_urllib3_context
    from urllib3 import PoolManager
    from requests.adapters import HTTPAdapter
    class AddedCipherAdapter(HTTPAdapter):
        def init_poolmanager(self, connections, maxsize, block=False):
            ctx = create_urllib3_context(ciphers=":HIGH:!DH:!aNULL")
            self.poolmanager = PoolManager(num_pools=connections,maxsize=maxsize,block=block,ssl_context=ctx)
except:
    pass

# Detekciu obisiel HereIronman7746/ParrotDevelopers

try: #kodi 19
	import ipaddress
	RANGES = ["212.65.192.0/18", "213.210.128.0/18", "37.48.0.0/18", "62.168.0.0/18",  #tmobile
	          "141.170.128.0/18", "178.77.192.0/18", "213.192.0.0/18", "213.220.192.0/18", #vodafone
	          "83.208.64.0/18", "88.83.160.0/19", "90.176.64.0/18", "85.193.0.0/18"] #o2
	def genip():
		return random.choice([str(ip) for ip in ipaddress.IPv4Network(random.choice(RANGES))])
except ImportError:  #kodi 18 fallback
	def genip():
	    cityint = random.randint(0,7)
	    ip = ""
	    if cityint == 0:
	        ip = '37.235.' + str(random.randint(108,111)) + '.' + str(random.randint(1,254))
	    elif cityint == 1:
	        ip = '46.23.' + str(random.randint(62,63)) + '.' + str(random.randint(1,254))
	    elif cityint == 2:
	        ip = '37.188.231.' + str(random.randint(0,255))
	    elif cityint == 3:
	        ip = '46.29.224.' + str(random.randint(0,255))
	    elif cityint == 4:
	        ip = '46.135.233.' + str(random.randint(0,255))
	    elif cityint == 5:
	        ip = '46.13.' + str(random.randint(91,255)) + '.' + str(random.randint(0,255))
	    elif cityint == 6:
	        ip = '62.209.240.' + str(random.randint(0,255))
	    elif cityint == 7:
	        ip = '46.135.66.' + str(random.randint(0,255))
	    return str(ip)


MEDIA_HOST = 'https://media.cms.nova.cz'
CHANNELS = {
    'nova':MEDIA_HOST+'/embed/nova-live?autoplay=1',
    'novafun':MEDIA_HOST+'/embed/nova-fun-live?autoplay=1',
    'novacinema':MEDIA_HOST+'/embed/nova-cinema-live?autoplay=1',
    'novaaction':MEDIA_HOST+'/embed/nova-action-live?autoplay=1',
    'novalady':MEDIA_HOST+'/embed/nova-lady-live?autoplay=1',
    'novagold':MEDIA_HOST+'/embed/nova-gold-live?autoplay=1',
    'novasport1':MEDIA_HOST+'/embed/nova-sport-1-live?autoplay=any',
    'novasport2':MEDIA_HOST+'/embed/nova-sport-2-live?autoplay=any'
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36','referer':MEDIA_HOST, 'origin':MEDIA_HOST}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    channel = CHANNELS[channel]

    session = requests.Session()
    try:
        # DH_KEY_TOO_SMALL on android fix
        session.mount(MEDIA_HOST, AddedCipherAdapter())
    except:
        pass
    headers = {}
    headers.update(HEADERS)
    headers.update({'X-Forwarded-For':genip()})
    response = session.get(channel, headers=headers)
    content = response.content
    try:
        content = content.decode('utf-8')
    except AttributeError:
        pass
    matches = re.search('{"sources":\[{"src":"([^"]*)","type":"application', content)
    hls = matches.group(1)
    hls = hls.replace('\/','/')

    uheaders = urlencode(headers)
    li = xbmcgui.ListItem(path=hls+'|'+uheaders)
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.stream_headers',uheaders)
    li.setProperty('inputstream.adaptive.manifest_headers',uheaders)
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
