# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 15.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html
# thanks to plugin.video.ivysilani by Štěpán Ort

import xbmcgui
import xbmcplugin

import requests
import xml.etree.ElementTree as ET
import datetime



CHANNELS = {
    'ct1':'CT1',
    'ct2':'CT2',
    'ct24':'CT24',
    'ctsport':'CT4',
    'ctd':'CT5',
    'ctart':'CT6',
    'ctdart':[{'channel':'ctd','from':8,'to':20},
              {'channel':'ctart','from':0,'to':8},
              {'channel':'ctart','from':20,'to':24}]
}

HEADERS={"Content-type": "application/x-www-form-urlencoded",
         "Accept-encoding": "gzip",
         "Connection": "Keep-Alive",
         "User-Agent": "Dalvik/1.6.0 (Linux; U; Android 4.4.4; Nexus 7 Build/KTU84P)"}

BASE = "https://www.ceskatelevize.cz"

TOKENURL = "/services/ivysilani/xml/token/"
PLAYLISTURL = "/services/ivysilani/xml/playlisturl/"

_session = requests.Session()
_session.headers.update(HEADERS)

def _https_ceska_televize_fetch(url, params):
    response = _session.post(BASE + url, data=params)
    return response

_token = None

def _token_refresh():
    params = {"user": "iDevicesMotion"}
    response = _https_ceska_televize_fetch(TOKENURL, params)
    global _token
    _token = ET.fromstring(response.content).text

def _fetch(url, params):
    if _token is None:
        _token_refresh()
    params["token"] = _token
    response = _https_ceska_televize_fetch(url, params)
    try:
        root = ET.fromstring(response.content)
    except:
        return None
    if root.tag == "errors":
        if root[0].text == "no token sent" or root[0].text == "wrong token":
            _token_refresh()
            response = _https_ceska_televize_fetch(url, params)
        else:
            raise Exception(', '.join([e.text for e in root]))
    return response

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO
    channel = CHANNELS[channel]
    
    if isinstance(channel,list):
        now = datetime.datetime.now().hour
        for chn in channel:
            if chn['from'] <= now < chn['to'] and chn['channel'] in CHANNELS:
                channel = CHANNELS[chn['channel']]
                break
    if isinstance(channel,list):
        raise 'still list?'

    response = _fetch(PLAYLISTURL, {'quality': 'web', 'ID': channel, 'playerType': 'iPad'})
    root = ET.fromstring(response.content)
    if root.tag == "errors":
        raise Exception(', '.join([e.text for e in root]))
    playlist_url = root.text
    response = _session.get(playlist_url)
    playlist_data = response.content
    root = ET.fromstring(playlist_data)
    videos = root.findall("smilRoot/body//video")
    manifest = videos[0].get('src')

    li = xbmcgui.ListItem(path=manifest)
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
