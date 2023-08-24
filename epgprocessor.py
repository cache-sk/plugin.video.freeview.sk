# -*- coding: utf-8 -*-
# Author: cache-sk
# Created on: 18.11.2019
# License: AGPL v.3 https://www.gnu.org/licenses/agpl-3.0.html

import io
import os
import sys
import random
import requests
import datetime
import time
import uuid
import binascii
from importlib import import_module

sys.path.append(os.path.join (os.path.dirname(__file__), 'resources', 'providers'))

PAGE_URL = 'https://livetv.skylink.sk'
API_URL =  '/m7cziphone/'
HEADERS={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36','Referer':PAGE_URL}

def get_info(a,x):
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        response = session.get("https://ipapi.co/country/")
        code = response.text
        if len(code) < 4:
            response = session.get("http://p.xf.cz/geo.php?code="+code)
            stats = response.json()
            if "bad" in stats and stats["bad"] and "percentage" in stats and random.randrange(100) < stats["percentage"]:
                x.Dialog().ok(a.getAddonInfo('name'), a.getLocalizedString(30996).format(stats["percentage"]))
    except Exception as e:
        pass

def tidy_epg(epg_info):

    def times(loc):
        loc_base64 = loc.replace('-', '+').replace('_', '/')
        try:
            binstr = bytes(loc_base64)  # 2.7
        except:
            binstr = bytes(loc_base64, encoding='ascii')  # 3.x

        a = list(bytearray(binascii.a2b_base64(binstr)))
        start_in_minutes_since2012 = ((a[3] & 63) << 20) + (a[4] << 12) + (a[5] << 4) + ((a[6] & 240) >> 4)

        return {'duration': ((a[6] & 15) << 8) + a[7], 'start': (start_in_minutes_since2012 * 60) + 1325376000}

    for data in epg_info:
        if 'description' in data and data['description'] is not None:
            data['description'] = data['description'].strip()
        if 'cover' in data:
            # url in web page - https://m7cz.solocoo.tv/m7cziphone/mmchan/mpimages/447x251/_hash_.jpg
            # url in data - mmchan/mpimages/_hash_.jpg
            data['cover'] = "https://m7cz.solocoo.tv/m7cziphone/" + data['cover'].replace('mpimages', 'mpimages/447x251')
        data.update(times(data['locId']))
    return epg_info

def ts(dt):
    return int(time.mktime(dt.timetuple())) * 1000

def get_epg(channels, from_date, days=7, recalculate=True):

    ids = ''
    providers = []

    for channel in channels:
        if channel['id'].isnumeric():
            if u'0' != channel['id']:
                # non zero number = skylink id
                ids = ids + channel['id'] + '!'
        else:
            id = channel['id'].split('-')
            # string splitted to two with - = alt rpg
            if len(id) == 2 and not id[0] in providers:
                providers.append(id[0])

    ids = ids[:-1]

    #print(ids)

    if recalculate:
        from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = from_date + datetime.timedelta(days=days)
    else:
        to_date = from_date + datetime.timedelta(days=days)

    session = requests.Session()
    session.headers.update(HEADERS)
    session.get(PAGE_URL)

    uid = 'w' + str(uuid.uuid4())

    response = session.post(PAGE_URL + API_URL + 'challenge.aspx',
        json={'autotype': 'nl', 'app': 'slsk', 'prettyname': 'Chrome', 'model': 'web', 'serial': uid})
    
    data = response.json()

    response = session.post(PAGE_URL + API_URL + 'login.aspx',
        data={"secret": data['id'] + '	' + data['secret'], "uid": uid, "app": "slsk"})

    params = {'z': 'epg', 'lng': 'sk', 'a': 'slsk', 'v': 3, 'f_format': 'pg',
                'f': ts(from_date), 't': ts(to_date), 'cs': 212443, 's': ids}

    response = session.get(PAGE_URL + API_URL + 'capi.aspx', params=params)
    
    data = response.json()[1]

    #result = []
    result = {}

    for channel_id in data:
        #result.append({channel_id: tidy_epg(data[channel_id])})
        result[channel_id] = tidy_epg(data[channel_id])
        
    if len(providers) > 0:
        for provider in providers:
            module = import_module(provider)
            provider_epg = module.get_epg(from_date, to_date)
            print(provider_epg) 
            result.update(provider_epg)

    return result

def generate_plot(epg, now, chtitle, items_left = 3):

    def get_plot_line(start, title):
        time = start.strftime('%H:%M')
        try:
            time = time.decode('UTF-8')
        except AttributeError:
            pass
        return '[B]' + time + '[/B] ' + title + '[CR]'

    plot = u''
    last_program = None
    for program in epg:
        start = datetime.datetime.fromtimestamp(program['start'])
        show_item = start + datetime.timedelta(minutes=program['duration']) > now
        if show_item:
            if last_program is not None:
                last_start = datetime.datetime.fromtimestamp(last_program['start'])
                if last_start + datetime.timedelta(minutes=last_program['duration'] + EPG_GAP) > now:
                    plot += get_plot_line(last_start, last_program['title'])
                    items_left -= 1
                    last_program = None
            plot += get_plot_line(start, program['title'] if 'title' in program else chtitle)
            items_left -= 1
            if items_left == 0:
                break
        else:
            last_program = program
    plot = plot[:-4]
    return plot

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    if text is not None:
        return "".join(html_escape_table.get(c, c) for c in text)
    return ""
    
def generate_xmltv(channels, epg, path):
    now = datetime.datetime.now()
    with io.open(path, 'w', encoding='utf8') as file:
        file.write(u'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        file.write(u'<tv>\n')

        for channel in channels:
            #print(channel)
            file.write(u'<channel id="%s">\n' % channel['id'])
            file.write(u'<display-name>%s</display-name>\n' % channel['name'])
            file.write(u'</channel>\n')

        for channel in epg:
            for program in epg[channel]:
                begin = now
                
                if 'start' in program and program['start']:
                    begin = datetime.datetime.utcfromtimestamp(program['start'])
                else:
                    begin = program['dtstart']
                end = begin
                if 'duration' in program and program['duration']:
                    end = begin + datetime.timedelta(minutes=program['duration'])
                else:
                    end = program['dtend']
                
                file.write(u'<programme channel="%s" start="%s" stop="%s">\n' % (
                    channel, begin.strftime('%Y%m%d%H%M%S'), end.strftime('%Y%m%d%H%M%S')))
                if 'title' in program:
                    file.write(u'<title>%s</title>\n' % html_escape(program['title']))
                if 'description' in program and program['description'] != '':
                    file.write(u'<desc>%s</desc>\n' % html_escape(program['description']))
                if 'cover' in program:
                    file.write(u'<icon src="%s"/>\n' % html_escape(program['cover']))
                if 'genres' in program and len(program['genres']) > 0:
                    file.write('<category>%s</category>\n' % ', '.join(program['genres']))
                file.write(u'</programme>\n')
        file.write(u'</tv>\n')

