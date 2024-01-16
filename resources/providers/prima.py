# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 16.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies
from bs4 import BeautifulSoup

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

PROXY_BASE = "http://p.xf.cz:8080" #TODO - to settings?
HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
CHANNELS = ['prima','love','krimi','max','cool','zoom','star','show']


def playcnn(_handle, _addon, params):
    session = requests.Session()
    headers = {}
    headers.update(HEADERS)
    response = session.get('https://api.play-backend.iprima.cz/api/v1/products/id-p650443/play', headers=headers)
    data = response.json()
    if 'streamInfos' in data and data['streamInfos']:
        stream = data['streamInfos'][0]['url']
        stream = stream.replace("_lq", "") #remove lq profile
        li = xbmcgui.ListItem(path=stream)
        li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
        li.setProperty('inputstream','inputstream.adaptive') #kodi 19
        li.setProperty('inputstream.adaptive.manifest_type','hls')
        xbmcplugin.setResolvedUrl(_handle, True, li)
        

def play(_handle, _addon, params):
    channel = params['channel']
    if 'cnn' == channel:
        playcnn(_handle, _addon, params)
    elif not channel in CHANNELS:
        raise #TODO
    else:
        session = requests.Session()
        headers = {}
        headers.update(HEADERS)

        #load index and banner, so page will not be delted
        try:
            response = session.get(PROXY_BASE, headers=headers)
            html = BeautifulSoup(response.content, features="html.parser")
            items = html.find_all('script',{},True)
            for item in items:
                if item.has_attr('src'):
                    response = session.get("http:"+item["src"] if item["src"].startswith("//") else item["src"], headers=headers)
        except:
            pass
        
        li = xbmcgui.ListItem(path=PROXY_BASE + "/iprima.php?ch=" + channel)
        li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
        li.setProperty('inputstream','inputstream.adaptive') #kodi 19
        li.setProperty('inputstream.adaptive.manifest_type','hls')
        xbmcplugin.setResolvedUrl(_handle, True, li)
        