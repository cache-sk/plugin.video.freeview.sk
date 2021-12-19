# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 11.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies
import re

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

##### NOTE - dokial nepridem na to ako obist geolokaciu, tak nefunkcne!


CHANNELS = {
    'novafun':'https://media.cms.nova.cz/embed/nova-fun-live?autoplay=1',
    'novalady':'https://media.cms.nova.cz/embed/nova-lady-live?autoplay=1'
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36','referer':'https://media.cms.nova.cz/'}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    channel = CHANNELS[channel]

    session = requests.Session()
    headers = {}
    headers.update(HEADERS)
    response = session.get(channel, headers=headers)
    content = response.content
    try:
        content = content.decode('utf-8')
    except AttributeError:
        pass
    matches = re.search('{"tracks":{"HLS":\[{"src":"([^"]*)","lang":"cze","type":"application', content)
    hls = matches.group(1)
    hls = hls.replace('\/','/')

    uheaders = urlencode(headers)
    li = xbmcgui.ListItem(path=hls+'|'+uheaders)
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.stream_headers',uheaders)
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
