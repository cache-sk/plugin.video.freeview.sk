# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 09.02.2023
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


CHANNELS = {
    'ntv1':{'hls':'https://ntv1.akamaized.net/hls/live/2014075/NASA-NTV1-HLS/master.m3u8'},
    'ntv2':{'hls':'https://ntv2.akamaized.net/hls/live/2013923/NASA-NTV2-HLS/master.m3u8'}
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    channel = CHANNELS[channel]

    li = xbmcgui.ListItem(path=channel['hls']+'|'+urlencode(HEADERS))
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
