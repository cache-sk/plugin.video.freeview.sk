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

# Detekciu obisiel HereIronman7746/ParrotDevelopers

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

CHANNELS = {
    'nova': 'https://media.cms.nova.cz/embed/nova-live?autoplay=1',
    'novafun': 'https://media.cms.nova.cz/embed/nova-fun-live?autoplay=1',
    'novagold': 'https://media.cms.nova.cz/embed/nova-gold-live?autoplay=1',
    'novaaction': 'https://media.cms.nova.cz/embed/nova-action-live?autoplay=1',
    #'novacinema': 'https://media.cms.nova.cz/embed/nova-cinema-live?autoplay=1',
    'novalady': 'https://media.cms.nova.cz/embed/nova-lady-live?autoplay=1'
}

#ERROR: Nova Cinema nefunguje, neviem preco ;'(

HEADERS= {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36','referer':'https://media.cms.nova.cz/',
    'X-Forwarded-For': genip()
}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    channel = CHANNELS[channel]

    session = requests.Session()
    headers = {}
    headers.update(HEADERS)
    response = session.get(channel, headers=headers)
    content = response.content
    try:
        content = content.decode('utf-8')
    except AttributeError:
        pass
    matches = re.search('{"tracks":{"HLS":\[{"src":"([^"]*)","lang":"cze","type":"application', content)
    hls = matches.group(1)
    hls = hls.replace('\/','/')

    uheaders = urlencode(headers)
    li = xbmcgui.ListItem(path=hls+'|'+uheaders)
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.stream_headers',uheaders)
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
