# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 16.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies
from urllib import urlencode
from bs4 import BeautifulSoup

PROXY_BASE = "http://p.xf.cz" #TODO - to settings?
HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
CHANNELS = ['prima','love','krimi','max','cool','zoom']


def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    session = requests.Session()
    headers = {}
    headers.update(HEADERS)

    #load index and banner, so page will not be delted
    response = session.get(PROXY_BASE, headers=headers)
    html = BeautifulSoup(response.text, features="html.parser")
    items = html.find_all('script',{},True)
    for item in items:
        if item.has_attr('src'):
            response = session.get("http:"+item["src"] if item["src"].startswith("//") else item["src"], headers=headers)

    li = xbmcgui.ListItem(path=PROXY_BASE + "/iprima.php?ch=" + channel)
    li.setProperty('inputstreamaddon','inputstream.adaptive')
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)