# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies
from urllib import urlencode
from bs4 import BeautifulSoup
import re

CHANNELS = {
    'markiza':"https://videoarchiv.markiza.sk/live/1-markiza",
    'doma':"https://videoarchiv.markiza.sk/live/3-doma",
    'dajto':"https://videoarchiv.markiza.sk/live/2-dajto"
}

#get https://moja.markiza.sk/
#post https://moja.markiza.sk/ + username, password, token
#get https://videoarchiv.markiza.sk/live/1-markiza
#get iframe https://videoarchiv.markiza.sk/api/v1/user/live?v=17dfc9ea-d1f3-43aa-be1e-2113124278a4&ch=1&back_url=https%3A%2F%2Fvideoarchiv.markiza.sk%2Flive%2F1-markiza
#get iframe https://media.cms.markiza.sk/embed/7OxIqexEHtt?autoplay=1
#get hls

BASE = "https://moja.markiza.sk/"
AFTER = "https://moja.markiza.sk/profil"
HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, channel, email, password):
    if not channel in CHANNELS:
        raise #TODO
    session = requests.Session()
    headers = {}
    headers.update(HEADERS)
    response = session.get(BASE, headers=headers)
    html = BeautifulSoup(response.text, features="html.parser")
    
    items = html.find_all('input',{'type':'hidden','name':'_token_'},True)
    _token_ = items[0]['value']

    items = html.find_all('input',{'type':'hidden','name':'_do'},True)
    _do = items[0]['value']

    items = html.find_all('input',{'type':'submit','name':'login','class':'btn'},True)
    login = items[0]['value']

    headers.update({'Referer':BASE})
    params = {'email':email, 'password':password, '_token_':_token_, '_do':_do, 'login':login}
    response = session.post(BASE, data=params, headers=headers, allow_redirects=False)

    if response.status_code != 302:
        print(response)
        print(response.status_code)
        #print(response.text)
        raise #TODO

    #response = session.get(AFTER, headers=headers)
    #headers.update({'Referer':AFTER})
    response = session.get(CHANNELS[channel], headers=headers)
    html = BeautifulSoup(response.text, features="html.parser")
    items = html.find_all('iframe',{'allowfullscreen':''},True)
    iframe1 = items[0]['src']
    print(iframe1)

    headers.update({'Referer':CHANNELS[channel]})
    response = session.get(iframe1, headers=headers)
    html = BeautifulSoup(response.text, features="html.parser")
    items = html.find_all('iframe',{},True)
    iframe2 = items[0]['src']
    print(iframe2)

    headers.update({'Referer':iframe1})
    response = session.get(iframe2, headers=headers)
    print(response.text)
    print(response.request)
    print(response.request.headers)
    print(response.request.url)
    print(response.request.body)
    matches = re.search("\"hls\": \"(.*)\"", response.text)
    hls = matches.group(1)
    
    headers.update({'Referer':iframe2})

    li = xbmcgui.ListItem(path=hls+'|'+urlencode(headers))
    li.setProperty('inputstreamaddon','inputstream.adaptive')
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
