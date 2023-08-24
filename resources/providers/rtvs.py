# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests
import datetime

from dateutil.parser import parse
from dateutil.tz import tzutc, tzlocal

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

CHANNELS = {
    'jednotka':1,
    'dvojka':2,
#    'trojka':3,
    '24':3,
    'online':4,
    'nrsr':5,
    'rtvs':6,
    'sport':15
}

ALTERNATIVE = {
    'jednotka':'https://ocko-live.ssl.cdn.cra.cz/channels/stv1/playlist/cze/live_hd.m3u8',
    'dvojka':'https://ocko-live.ssl.cdn.cra.cz/channels/stv2/playlist/cze/live_hd.m3u8'
}

API_INIT = "https://www.rtvs.sk/televizia/tv"
API = "https://www.rtvs.sk/json/live5f.json"
PARAMS = {'ad':1,'b':'chrome','p':'win','v':'77','f':0,'d':1}
CHANNEL_PARAM = 'c'
HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS:
        raise #TODO
    
    prefer_mpd = xbmcplugin.getSetting(_handle, 'rtvsmpd') == 'true'
    alternative = False #xbmcplugin.getSetting(_handle, 'rtvsalt') == 'true'

    if alternative and channel in ALTERNATIVE:
        li = xbmcgui.ListItem(path=ALTERNATIVE[channel] + '|' + urlencode(HEADERS))
        li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
        li.setProperty('inputstream','inputstream.adaptive') #kodi 19
        li.setProperty('inputstream.adaptive.manifest_type','hls')
        xbmcplugin.setResolvedUrl(_handle, True, li)
    else:
        session = requests.Session()
        session.headers.update(HEADERS)
        session.get(API_INIT)
        params = {CHANNEL_PARAM:CHANNELS[channel]}
        params.update(PARAMS)
        response = session.get(API, params=params)
        data = response.json()
        clip = data['clip']
        sources = clip['sources']
        hls = None
        mpd = None
        for src in sources:
            if src['type'] == "application/dash+xml":
                mpd = src['src'].replace('\n','')
            elif src['type'] == "application/x-mpegurl":
                hls = src['src'].replace('\n','')
        
        headers = urlencode(HEADERS)

        if (prefer_mpd or hls is None) and mpd is not None:
            li = xbmcgui.ListItem(path=mpd + '|' +headers)
            li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
            li.setProperty('inputstream','inputstream.adaptive') #kodi 19
            li.setProperty('inputstream.adaptive.stream_headers',headers)
            li.setProperty('inputstream.adaptive.manifest_type','mpd')
            xbmcplugin.setResolvedUrl(_handle, True, li)
        elif hls is not None:
            li = xbmcgui.ListItem(path=hls + '|' +headers)
            li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
            li.setProperty('inputstream','inputstream.adaptive') #kodi 19
            li.setProperty('inputstream.adaptive.stream_headers',headers)
            li.setProperty('inputstream.adaptive.manifest_type','hls')
            xbmcplugin.setResolvedUrl(_handle, True, li)
        else:
            raise #TODO
            

EPGAPI = 'https://api.rtvs.sk/json/broadcast/v1.1.4/tv/program'
EPGHEADERS = {'X-API-KEY':'2454b377-72d1-4b4a-8e34-d693cd5f787b'}
EPGCHANNELS = [{'id':'rtvs-liveo','channel':'4'},{'id':'rtvs-live','channel':'6'}]
def get_epg(from_date, to_date):
    print("yaaay")
    session = requests.Session()
    session.headers.update(EPGHEADERS)
    epg = {}
    for channel in EPGCHANNELS:
        response = session.get(EPGAPI, params={'datemode':'now-future','channel':channel['channel']})
        data = response.json()
        print(data)
        if 'data' in data and data['data']:
            chdata = []
            for program in data['data']:
                print(program)
                item = {'dtstart':parse(program['air_datetimestart']).astimezone(tzutc()), 'dtend':parse(program['air_datetimestop']).astimezone(tzutc()), 'title':program['name']}
                if 'media' in program and program['media'] and 'images' in program['media'] and program['media']['images'] and len(program['media']['images']) > 0 and 'url' in program['media']['images'][0] and program['media']['images'][0]['url']:
                    item['cover'] = program['media']['images'][0]['url']
                chdata.append(item)
            epg[channel['id']] = chdata
    return epg