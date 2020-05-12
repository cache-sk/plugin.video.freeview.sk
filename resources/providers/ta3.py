# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 11.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests
import re
from urllib import urlencode


CHANNELS = {
    'ta3':'https://embed.livebox.cz/ta3_v2/live-source.js'
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    session = requests.Session()
    session.headers.update(HEADERS)
    response = session.get(CHANNELS[channel])
    matches = re.findall("\"src\" : \"([^}]*)\"", response.content)
    src = None
    for match in matches:
        if '1.smil' in match:
            src = match
            break

    src = src.replace('|','%7C')
    if src.startswith('//'):
        src = 'https:' + src

    li = xbmcgui.ListItem(path=src+'|'+urlencode(HEADERS))
    li.setProperty('inputstreamaddon','inputstream.adaptive')
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)

