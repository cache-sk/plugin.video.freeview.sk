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


API = 'https://api.ceskatelevize.cz/video/v1/playlist-live/v1/stream-data/channel/'
PARAMS = { 'canPlayDrm':'false', 'streamType':'hls', 'quality':'web', 'maxQualityCount':'5' }

CHANNELS = {
    'ct1':'CH_1',
    'ct2':'CH_2',
    'ct24':'CH_24',
    'ctsport':'CH_4',
    'ctd':'CH_5',
    'ctart':'CH_6',
    'ctdart':[{'channel':'ctd','from':8,'to':20},
              {'channel':'ctart','from':0,'to':8},
              {'channel':'ctart','from':20,'to':24}]
}

SPAPI = 'https://api.ceskatelevize.cz/graphql/'
SPPARAMS = { 'client':'website', 'version':'1.64.1', 'operationName':'LiveBroadcastFind', 'variables':'{}', 'extensions':'{"persistedQuery":{"version":1,"sha256Hash":"cd7619a5186ef6277c1e82179c669e02e3edac97739593bc28fa32df5041d644"}}' }
SPNONE = 'CH_7'
SPCHANNEL = 'ctSportExtra'
SPPREFIX = 'CH_'

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def get_sport_plus_channel(_addon, session):
    response = session.get(SPAPI, params=SPPARAMS)
    data = response.json()
    available = []
    titles = []
    if 'data' in data and data['data'] and 'liveBroadcastFind' in data['data'] and data['data']['liveBroadcastFind']:
        for live in data['data']['liveBroadcastFind']:
            if 'id' in live and live['id'] and 'current' in live and live['current'] and 'channel' in live['current'] and live['current']['channel'] and live['current']['channel'] == SPCHANNEL:
                title = SPCHANNEL
                if 'title' in live['current'] and live['current']['title']:
                    title = live['current']['title']
                available.append(live['id'])
                titles.append(title)
    if len(available) == 1:
        return SPPREFIX + available[0]
    if len(available) > 1:
        index = xbmcgui.Dialog().select(_addon.getAddonInfo('name'), titles)
        if index == -1:
            pass
        else:
            return SPPREFIX + available[index]
    return SPNONE

def play(_handle, _addon, params):
    session = requests.Session()
    session.headers.update(HEADERS)

    channel = params['channel']
    if channel in CHANNELS:
        channel = CHANNELS[channel]
    elif 'ctsportplus' == channel:
        channel = get_sport_plus_channel(_addon, session)
    else:
        raise #TODO
    
    if isinstance(channel,list):
        now = datetime.datetime.now().hour
        for chn in channel:
            if chn['from'] <= now < chn['to'] and chn['channel'] in CHANNELS:
                channel = CHANNELS[chn['channel']]
                break
    if isinstance(channel,list):
        raise 'still list?'
    
    response = session.get(API + channel, params=PARAMS)
    data = response.json()
    if 'streamUrls' in data and data['streamUrls'] and 'main' in data['streamUrls'] and data['streamUrls']['main']:
        li = xbmcgui.ListItem(path=data['streamUrls']['main'])
        li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
        li.setProperty('inputstream','inputstream.adaptive') #kodi 19
        li.setProperty('inputstream.adaptive.manifest_type','hls')
        xbmcplugin.setResolvedUrl(_handle, True, li)
    else:
        raise #TODO
