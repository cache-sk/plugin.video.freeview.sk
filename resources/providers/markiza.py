# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies
from bs4 import BeautifulSoup
import re

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


CHANNELS = {
    'markiza':"https://videoarchiv.markiza.sk/live/1-markiza",
    'doma':"https://videoarchiv.markiza.sk/live/3-doma",
    'dajto':"https://videoarchiv.markiza.sk/live/2-dajto",
    'krimi':"https://videoarchiv.markiza.sk/live/22-krimi"
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

RETRIES = 10 #means 1 + 10

def brexit(_addon, _handle, word):
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
        return brexit(_addon, _handle, 'token')

    items = html.find_all('input',{'type':'hidden','name':'_do'},True)
    if len(items) > 0:
        _do = items[0]['value']
    else:
        return brexit(_addon, _handle, 'do')

    items = html.find_all('input',{'type':'submit','name':'login','class':'btn'},True)
    if len(items) > 0:
        login = items[0]['value']
    else:
        return brexit(_addon, _handle, 'login')

    headers.update({'Referer':BASE})
    params = {'email':email, 'password':password, '_token_':_token_, '_do':_do, 'login':login}
    response = session.post(BASE, data=params, headers=headers, allow_redirects=False)

    if response.status_code != 302:
        return brexit(_addon, _handle, 'forward')

    #response = session.get(AFTER, headers=headers)
    #headers.update({'Referer':AFTER})
    response = session.get(CHANNELS[channel], headers=headers)
    html = BeautifulSoup(response.content, features="html.parser")
    items = html.find_all('iframe',{'allowfullscreen':''},True)
    for i in items:
        if 'videoarchiv' in i['src']:
            iframe1 = i['src']
    if iframe1 is None:
        return brexit(_addon, _handle, 'iframe1')

    headers.update({'Referer':CHANNELS[channel]})
    
    attempt = 0
    iframe2 = None
    pDialog = None
    
    while iframe2 is None and attempt < RETRIES:
        attempt = attempt+1
        if attempt == 2:
            pDialog = xbmcgui.DialogProgress()
            pDialog.create(_addon.getAddonInfo('name'), _addon.getLocalizedString(30997))
        if attempt > 1:    
            pDialog.update(int(round((attempt)*(100/RETRIES))), '')
        response = session.get(iframe1, headers=headers)
        html = BeautifulSoup(response.content, features="html.parser")
        items = html.find_all('iframe',{},True)
        for i in items:
            if 'media' in i['src']:
                iframe2 = i['src']
    if pDialog is not None:
        pDialog.close()
        
    if iframe2 is None:
        return brexit(_addon, _handle, 'iframe2')

    headers.update({'Referer':iframe1})
    response = session.get(iframe2, headers=headers)
    content = response.content
    try:
        content = content.decode('utf-8')
    except AttributeError:
        pass
    matches = re.search('{"tracks":{"HLS":\[{"src":"(.*)","type":"application', content)
    hls = matches.group(1)
    hls = hls.replace('\/','/')
    headers.update({'Referer':iframe2})

    #note - adaptive nejde, lebo neposiela headre
    uheaders = urlencode(headers)
    li = xbmcgui.ListItem(path=hls+'|'+uheaders)
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.stream_headers',uheaders)
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
