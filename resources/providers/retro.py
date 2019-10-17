# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin

from urllib import urlencode
import m3u8


CHANNELS = {
    'retro':{'path':'http://stream.mediawork.cz/retrotv/smil:retrotv2.smil/','playlist':'playlist.m3u8'}
}

ALTERNATIVE = {
    'retro':{'path':'http://stream.mediawork.cz/retrotv/retrotvHQ1/','playlist':'playlist.m3u8'} 
}



HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO

    parse_playlist = xbmcplugin.getSetting(_handle, 'retroparse') == 'true'
    alternative = xbmcplugin.getSetting(_handle, 'retroalt') == 'true'

    channel = ALTERNATIVE[channel] if alternative and channel in ALTERNATIVE else CHANNELS[channel]

    if parse_playlist:
        best = None
        streams = m3u8.load(channel['path'] + channel['playlist'], headers=HEADERS)
        for stream in streams.playlists:
            if best is None:
                best = stream
            else:
                if stream.stream_info.bandwidth > best.stream_info.bandwidth:
                    best = stream
        li = xbmcgui.ListItem(path=channel['path']+best.uri+'|'+urlencode(HEADERS))
        xbmcplugin.setResolvedUrl(_handle, True, li)
    else:
        li = xbmcgui.ListItem(path=channel['path']+channel['playlist']+'|'+urlencode(HEADERS))
        li.setProperty('inputstreamaddon','inputstream.adaptive')
        li.setProperty('inputstream.adaptive.manifest_type','hls')
        xbmcplugin.setResolvedUrl(_handle, True, li)


