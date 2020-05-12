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

def brexit(_addon, word):
    xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30105) + word)
    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
    return False

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    email = xbmcplugin.getSetting(_handle, 'mrkzemail')
    password = xbmcplugin.getSetting(_handle, 'mrkzpassword')

    session = requests.Session()
    headers = {}
    headers.update(HEADERS)
    response = session.get(BASE, headers=headers)
    html = BeautifulSoup(response.content, features="html.parser")
    
    items = html.find_all('input',{'type':'hidden','name':'_token_'},True)
    if len(items) > 0:
        _token_ = items[0]['value']
    else:
        return brexit(_addon, 'token')

    items = html.find_all('input',{'type':'hidden','name':'_do'},True)
    if len(items) > 0:
        _do = items[0]['value']
    else:
        return brexit(_addon, 'do')

    items = html.find_all('input',{'type':'submit','name':'login','class':'btn'},True)
    if len(items) > 0:
        login = items[0]['value']
    else:
        return brexit(_addon, 'login')

    headers.update({'Referer':BASE})
    params = {'email':email, 'password':password, '_token_':_token_, '_do':_do, 'login':login}
    response = session.post(BASE, data=params, headers=headers, allow_redirects=False)

    if response.status_code != 302:
        return brexit(_addon, 'forward')

    #response = session.get(AFTER, headers=headers)
    #headers.update({'Referer':AFTER})
    response = session.get(CHANNELS[channel], headers=headers)
    html = BeautifulSoup(response.content, features="html.parser")
    items = html.find_all('iframe',{'allowfullscreen':''},True)
    if len(items) > 0:
        iframe1 = items[0]['src']
    else:
        return brexit(_addon, 'iframe1')

    headers.update({'Referer':CHANNELS[channel]})
    response = session.get(iframe1, headers=headers)
    html = BeautifulSoup(response.content, features="html.parser")
    items = html.find_all('iframe',{},True)
    if len(items) > 0:
        iframe2 = items[0]['src']
    else:
        return brexit(_addon, 'iframe2')

    headers.update({'Referer':iframe1})
    response = session.get(iframe2, headers=headers)
    matches = re.search("\"hls\": \"(.*)\"", response.content)
    hls = matches.group(1)
    
    headers.update({'Referer':iframe2})

    li = xbmcgui.ListItem(path=hls+'|'+urlencode(headers))
    li.setProperty('inputstreamaddon','inputstream.adaptive')
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
