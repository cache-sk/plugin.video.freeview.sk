# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies
import re

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


CHANNELS = {
    'markiza':"https://www.markiza.sk/live/1-markiza",
    'doma':"https://www.markiza.sk/live/3-doma",
    'dajto':"https://www.markiza.sk/live/2-dajto",
    'krimi':"https://www.markiza.sk/live/22-krimi"
}
MATCHER = {
    #"source":{"sources":[{"src":"https://cmesk-ott-live-avod-sec.ssl.cdn.cra.cz/8o_qlthSGfa34Xhb4-m3dg==,1713964109/channels/cme-sk-markiza_avod/playlist/slo.m3u8","type":"application/x-mpegurl"}]}
    #'markiza':',"source":{"sources":\[{"src":"(.*)","type":"application/x-mpegurl"}\]},',
    #'default':'{"tracks":{"HLS":\[{"src":"(.*)","type":"application'
    'default':',"source":{"sources":\[{"src":"([^"]+)","type":"application/x-mpegurl"}\]},'
}

BASE = "https://www.markiza.sk/prihlasenie"
ORIGIN = "https://media.cms.markiza.sk/"
HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

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
    content = response.text
    
    matches = re.search('<input type="hidden" name="_do" value="(.+)-loginForm-(.+)">', content)
    if bool(matches):
        _do = matches.group(1) + '-loginForm-' + matches.group(2)
    else:
        return brexit(_addon, _handle, 'do')

    headers.update({'Referer':BASE})
    params = {'email':email, 'password':password, '_do':_do}
    response = session.post(BASE, data=params, headers=headers, allow_redirects=False)

    if response.status_code == 401:
        xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30997))
        xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
        return False
        
    if response.status_code != 302:
        return brexit(_addon, _handle, 'forward')

    response = session.get(CHANNELS[channel], headers=headers)
    content = response.text
    
    matches = re.search('<iframe data-src="([^"]+)".+allowfullscreen.+></iframe>', content)
    if bool(matches):
        iframe = matches.group(1)
    else:
        return brexit(_addon, _handle, 'iframe')

    headers.update({'Referer':CHANNELS[channel]})
    
    response = session.get(iframe, headers=headers)
    
    content = response.content
    try:
        content = content.decode('utf-8')
    except AttributeError:
        pass
        
    final_matcher = MATCHER[channel] if channel in MATCHER else MATCHER['default']
    matches = re.search(final_matcher, content)
    hls = matches.group(1)
    #hls = hls.replace('\/','/')
    headers.update({'Referer':ORIGIN, 'Origin':ORIGIN})


    #note - adaptive nejde, lebo neposiela headre
    uheaders = urlencode(headers)
    li = xbmcgui.ListItem(path=hls+'|'+uheaders)
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.stream_headers',uheaders)
    li.setProperty('inputstream.adaptive.manifest_headers',uheaders)
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
