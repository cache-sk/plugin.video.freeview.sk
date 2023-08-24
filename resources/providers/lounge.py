# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 23.8.2023
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests.cookies
import re
import random
import base64
import json
import time

try:
    from urllib import urlencode, quote_plus, quote
except ImportError:
    from urllib.parse import urlencode, quote_plus, quote

BASE = 'https://loungetv.cz/ltv-play'

HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36','referer':'https://loungetv.cz','origin':'https://loungetv.cz'}

def play(_handle, _addon, params):
    #check kodi version
    version = xbmc.getInfoLabel('System.BuildVersion')
    matches = re.search('(\d+)*', version)
    version = int(matches.group(1))
    if version < 20:
        xbmcgui.Dialog().ok(_addon.getAddonInfo('name'),_addon.getLocalizedString(30301))
        raise

    #check inputstream helper
    try:
        xbmcaddon.Addon('script.module.inputstreamhelper')
    except:
        xbmcgui.Dialog().ok(_addon.getAddonInfo('name'),_addon.getLocalizedString(30302))
        raise 

    timestamp = time.time()
    session = requests.Session()
    #session.verify = False
    headers = {}
    headers.update(HEADERS)
    response = session.get(BASE, headers=headers)
    content = response.content
    try:
        content = content.decode('utf-8')
    except AttributeError:
        pass
        
    matches = re.search('xmlHttp\.open\(\'POST\', \'([^\s]+)\', false\);', content)
    nextstep = matches.group(1)

    matches = re.search('var customers_token = \'(.+)\';', content)
    customers_token = matches.group(1)
    customers_token = customers_token.strip()
    headers.update({'Authorization':'Bearer '+customers_token})
    
    matches = re.search('var profiles_id = \'(.+)\';', content)
    profiles_id = matches.group(1)
    headers.update({'profilesId':base64.b64encode(profiles_id.encode('utf-8'))})
    
    matches = re.search('var devices_type = \'(.+)\';', content)
    devices_type = matches.group(1)
    headers.update({'devicesType':base64.b64encode(devices_type.encode('utf-8'))})
    
    matches = re.search('var offset = ([0-9]+);', content)
    offset = int(matches.group(1))

    matches = re.search('var version = \'(.+)\';', content)
    version = matches.group(1)
    
    matches = re.search('var edges_id = ([0-9]+);', content)
    edges_id = int(matches.group(1))
    
    matches = re.search('var devices_identification = \'(.+)\';', content)
    devices_identification = matches.group(1)
    
    matches = re.search('var devices_hash = \'(.+)\';', content)
    devices_hash = matches.group(1)
    
    matches = re.search('\'com.widevine.alpha\': \'(.+)\',', content)
    widevine = matches.group(1)
    
    matches = re.search('xmlHttp\.send\(\'(.+)\'\);', content)
    data = matches.group(1)
    
    response = session.post(nextstep, data, headers=headers)
    stream = response.content
    try:
        stream = stream.decode('utf-8')
    except AttributeError:
        pass
    stream = json.loads(stream)
    
    uheaders = urlencode(headers)
    data_drm = {}
    data_drm['timestamp'] = int(timestamp)
    data_drm['offset'] = offset
    data_drm['version'] = version
    data_drm['version'] = version
    data_drm['edges_id'] = edges_id
    data_drm['devices_identification'] = devices_identification
    data_drm['devices_hash'] = devices_hash
    data_drm['rawLicense'] = 'b{SSM}'
    drm_license = widevine + '|' + uheaders + '|' + json.dumps(data_drm) + '|JBrawLicense'

    li = xbmcgui.ListItem(path=stream['response']['url']+'|'+uheaders)
    li.setProperty('inputstream','inputstream.adaptive')
    li.setProperty('inputstream.adaptive.stream_headers',uheaders)
    li.setProperty('inputstream.adaptive.manifest_type','mpd')
    li.setProperty('inputstream.adaptive.license_type','com.widevine.alpha')
    li.setProperty('inputstream.adaptive.license_key',drm_license)
    xbmcplugin.setResolvedUrl(_handle, True, li)
