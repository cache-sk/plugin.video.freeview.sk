# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin

import requests
import re
from bs4 import BeautifulSoup
from urllib import urlencode
import inputstreamhelper

def process24(_handle, _addon, params):
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get("https://www.ceskatelevize.cz/")
    response = session.get("https://ct24.ceskatelevize.cz/")
    html = BeautifulSoup(response.content, features="html.parser")
    items = html.find_all('span',{'class':'media-ivysilani-placeholder'},True)
    dataUrl = items[0]['data-url']
    matches = re.search('media_ivysilani:{hash:"([^"]*)"', response.content)
    hsh = matches.group(1)
    
    iframe = dataUrl+'&hash='+hsh
    response = session.get(iframe)
    matches = re.search("wvLicenseProxyUrl: \'(\S*)\',", response.content)
    licence = matches.group(1)


    response = session.post("https://www.ceskatelevize.cz/ivysilani/ajax/get-client-playlist/",data={
        "playlist[0][type]":"channel",
        "playlist[0][id]":"24",
        "requestUrl":"/ivysilani/embed/iFramePlayer.php",
        "requestSource":"iVysilani",
        "type":"html",
        "canPlayDRM":"true"
    }, headers={'x-addr':'127.0.0.1', 'X-Requested-With': 'XMLHttpRequest'})

    data = response.json()['url']
    response = session.get(data)
    playlist = response.json()
    url = playlist['playlist'][0]['streamUrls']['main']

    headers = {'Referer': iframe, 'Origin':'https://www.ceskatelevize.cz'}
    headers.update(HEADERS)

    hencoded = urlencode(headers)
    return {'url':url + '|' + hencoded,'manifest':'mpd', 'licence':licence + '|' + hencoded + '|R{SSM}|', 'drm':'com.widevine.alpha'}

CHANNELS = {
    'ct24':lambda _handle, _addon, params:process24(_handle, _addon, params)
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    data = CHANNELS[channel](_handle, _addon, params)

    is_helper = inputstreamhelper.Helper(data['manifest'], drm=data['drm'])
    if is_helper.check_inputstream():
        playitem = xbmcgui.ListItem(path=data['url'])
        playitem.setProperty('inputstreamaddon', is_helper.inputstream_addon)
        playitem.setProperty('inputstream.adaptive.manifest_type', data['manifest'])
        playitem.setProperty('inputstream.adaptive.license_type', data['drm'])
        playitem.setProperty('inputstream.adaptive.license_key', data['licence'])
        xbmcplugin.setResolvedUrl(_handle, True, playitem)
