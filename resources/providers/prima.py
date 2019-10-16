# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 16.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin

from urllib import urlencode


CHANNELS = {
    'prima':'https://prima-ott-live.ssl.cdn.cra.cz/channels/prima_family/playlist/cze/live_hq.m3u8',
    'love':'https://prima-ott-live.ssl.cdn.cra.cz/channels/prima_love/playlist/cze/live_hq.m3u8',
    'krimi':'https://prima-ott-live.ssl.cdn.cra.cz/channels/prima_krimi/playlist/cze/live_hq.m3u8',
    'max':'https://prima-ott-live.ssl.cdn.cra.cz/channels/prima_max/playlist/cze/live_hq.m3u8',
    'cool':'https://prima-ott-live.ssl.cdn.cra.cz/channels/prima_cool/playlist/cze/live_hq.m3u8',
    'zoom':'https://prima-ott-live.ssl.cdn.cra.cz/channels/prima_zoom/playlist/cze/live_hq.m3u8'
}

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, _addon, params):
    raise #403
