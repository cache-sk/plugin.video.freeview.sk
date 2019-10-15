# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 10.10.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

from urlparse import parse_qsl
from importlib import import_module

sys.path.append(os.path.join (os.path.dirname(__file__), 'resources', 'providers'))

_url = sys.argv[0]
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()

def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params and 'provider' in params:
        provider = params['provider']
        module = import_module(provider)
        module.play(_handle, _addon, params)
    else:
        xbmcplugin.endOfDirectory(_handle)
        xbmcgui.Dialog().textviewer(_addon.getAddonInfo('name'), _addon.getLocalizedString(30999))
        destination = xbmcgui.Dialog().browseSingle(3, _addon.getAddonInfo('name'), '')
        if destination is not None and destination:
            try:
                if xbmcvfs.exists(destination + 'playlist.m3u'):
                    if not xbmcgui.Dialog().yesno(_addon.getAddonInfo('name'), _addon.getLocalizedString(30902)):
                        return
                xbmcvfs.copy('special://home/addons/plugin.video.freeview.sk/playlist.m3u', destination + 'playlist.m3u')
                xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30900))
            except Exception as e:
                xbmcgui.Dialog().ok(_addon.getAddonInfo('name'), _addon.getLocalizedString(30901), str(e))
        

if __name__ == '__main__':
    router(sys.argv[2][1:])