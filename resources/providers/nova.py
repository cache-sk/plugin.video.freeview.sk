# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 11.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin

from urllib import urlencode


CHANNELS = {
    'nova':{'hls':'https://nova-live.ssl.cdn.cra.cz/channels/nova_avod/playlist.m3u8'},
    'nova2':{'hls':'https://nova-live.ssl.cdn.cra.cz/channels/nova_2_avod/playlist.m3u8'},
    'cinema':{'hls':'https://nova-live.ssl.cdn.cra.cz/channels/nova_cinema_avod/playlist.m3u8'},
    'action':{'hls':'https://nova-live.ssl.cdn.cra.cz/channels/nova_action_avod/playlist.m3u8'},
    'gold':{'hls':'https://nova-live.ssl.cdn.cra.cz/channels/nova_gold_avod/playlist.m3u8'}
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    channel = CHANNELS[channel]

    li = xbmcgui.ListItem(path=channel['hls']+'|'+urlencode(HEADERS))
    li.setProperty('inputstreamaddon','inputstream.adaptive')
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
