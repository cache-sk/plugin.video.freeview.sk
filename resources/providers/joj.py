# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmcgui
import xbmcplugin
import requests.cookies
from bs4 import BeautifulSoup
import re
import random

try:
    from urllib import urlencode
    from urllib import quote
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import quote

CHANNELS = {
    'joj':{'base':'https://live.joj.sk', 'iframe':'https://media.joj.sk/', 'fget':False},
    'plus':{'base':'https://plus.joj.sk/live', 'iframe':'https://media.joj.sk/', 'fget':False},
    'wau':{'base':'https://wau.joj.sk/live', 'iframe':'https://media.joj.sk/', 'fget':False},
    'family':{'base':'http://jojfamily.blesk.cz/live', 'iframe':'https://media.joj.sk/', 'fget':True},
    'joj24':{'base':'https://joj24.noviny.sk/', 'iframe':'https://media.joj.sk/', 'fget':False}
}

JOJPLAY = { #mpd alt like https://st02-1.iptv.joj.sk/101-tv-pc.mpd
    'CHANNELS':{
        'joj':'101-tv-pc.m3u8',
        'plus':'102-tv-pc.m3u8',
        'wau':'103-tv-pc.m3u8',
        'jojko':'104-tv-pc.m3u8',
        'jojcinema':'105-tv-pc.m3u8',
        'csfilm':'106-tv-pc.m3u8',
        'cshistory':'107-tv-pc.m3u8',
        'csmystery':'108-tv-pc.m3u8',
        'jojsport':'110-tv-pc.m3u8',
        'joj24':'111-tv-pc.m3u8'
    },
    'BASE': ['https://st01-1.iptv.joj.sk/','https://st02-1.iptv.joj.sk/','https://st03-1.iptv.joj.sk/']
}

FGET = "http://p.xf.cz/fget.php?url="

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}

def brexit(_addon, _handle, word):
    xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30105) + word)
    xbmcplugin.setResolvedUrl(_handle, False, xbmcgui.ListItem())
    return False

def playFromPage(channel):
    if "direct" in channel:
        hls = channel["direct"]
        headers = HEADERS
    else:
        session = requests.Session()
        headers = {}
        headers.update(HEADERS)
        response = session.get(channel['base'], headers=headers)
        html = BeautifulSoup(response.content, features="html.parser")
        
        player = None
        items = html.find_all('iframe',{},True)
        if len(items) > 0:
            for iframe in items:
                if channel['iframe'] in iframe['src']:
                    player = iframe['src']
                    break
        else:
            return brexit(_addon, _handle, 'iframe')

        if player is None:
            return brexit(_addon, _handle, 'iframe')
            
        if channel['fget']:
            #TODO - sooo lazy..
            response = session.get(FGET+quote(player), headers=headers)
        else:
            headers = {'Referer':channel['base']}
            headers.update(HEADERS)
            response = session.get(player, headers=headers)
        
        content = response.content
        try:
            content = content.decode('utf-8')
        except AttributeError:
            pass
        matches = re.search('"hls": "(.*)"', content)
        hls = matches.group(1)
        
        headers = {'Referer':channel['iframe'], 'Origin':channel['iframe']}
        headers.update(HEADERS)

    return {'hls':hls, 'headers':headers}

def playJojPlay(channel):
    return {'hls':random.choice(JOJPLAY["BASE"]) + channel,'headers':HEADERS}

def play(_handle, _addon, params):
    channel = params['channel']
    if not channel in CHANNELS and not channel in JOJPLAY['CHANNELS']:
        raise #TODO

    prefer_jojplay = xbmcplugin.getSetting(_handle, 'prefer_jojplay') == 'true'

    data = (
        playJojPlay(JOJPLAY['CHANNELS'][channel]) if channel in JOJPLAY['CHANNELS'] and prefer_jojplay else 
        playFromPage(CHANNELS[channel]) if channel in CHANNELS else 
        playJojPlay(JOJPLAY['CHANNELS'][channel])
    )
    
    li = xbmcgui.ListItem(path=data['hls']+'|'+urlencode(data['headers']))
    li.setProperty('inputstreamaddon','inputstream.adaptive') #kodi 18
    li.setProperty('inputstream','inputstream.adaptive') #kodi 19
    li.setProperty('inputstream.adaptive.manifest_type','hls')
    xbmcplugin.setResolvedUrl(_handle, True, li)
