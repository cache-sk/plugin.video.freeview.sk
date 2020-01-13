# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin

from urllib import urlencode


CHANNELS = {
    'joj':{'src':'https://nn.geo.joj.sk/live/joj-index.m3u8','referer':'https://live.joj.sk/'},
    'plus':{'src':'https://nn.geo.joj.sk/live/jojplus-index.m3u8', 'referer':'https://plus.joj.sk/live'},
    'wau':{'src':'https://nn.geo.joj.sk/live/wau-index.m3u8', 'referer':'https://wau.joj.sk/live'},
    'jojko':{'src':'https://nn.geo.joj.sk/live/rik-index.m3u8', 'referer':'https://jojko.joj.sk/live'}, #http://nn2.joj.sk/hls/rik-540.m3u8
    'family':{'src':'https://nn.geo.joj.sk/live/family-index.m3u8', 'referer':'http://jojfamily.blesk.cz/live'}
}
#alternative - https://ocko-live.ssl.cdn.cra.cz/channels/joj/playlist/cze/live_hd.m3u8

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    channel = CHANNELS[channel]
    headers = {'Referer':channel['referer']}
    headers.update(HEADERS)

    li = xbmcgui.ListItem(path=channel['src']+'|'+urlencode(headers))
    li.setProperty('inputstreamaddon','inputstream.adaptive')
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
