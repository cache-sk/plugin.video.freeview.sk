import datetime
import time
import io
import os
import skylink
import m3u
import xbmc
import xbmcaddon
import traceback
import string
import random

class SkylinkMonitor(xbmc.Monitor):
    _addon = None
    _profile = ''
    _next_update = 0

    def __init__(self):
        xbmc.Monitor.__init__(self)
        self._addon = xbmcaddon.Addon()
        self._profile = xbmc.translatePath(self._addon.getAddonInfo('profile'))
        try:
            self._profile = self._profile.decode("utf-8")
        except AttributeError:
            pass
        ts = self._addon.getSetting('genepg_next_update')
        self._next_update = datetime.datetime.fromtimestamp(0) if ts == '' else datetime.datetime.fromtimestamp(float(ts))
        #cleanup
        if os.path.exists(self._profile):
            files_to_remove = [f for f in os.listdir(self._profile) if os.path.isfile(os.path.join(self._profile, f)) and f.endswith('.work.xml')]
            for f in files_to_remove:
                os.unlink(os.path.join(self._profile, f))

    def __del__(self):
        print('freeview service destroyed')

    def notify(self, text, error=False):
        try:
            text = text.encode("utf-8") if type(text) is unicode else text
        except:
            pass
        icon = 'DefaultIconError.png' if error else ''
        xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (self._addon.getAddonInfo('name'), text, icon))

    def onSettingsChanged(self):
        self._addon = xbmcaddon.Addon()  # refresh for updated settings!
        if not self.abortRequested():
            self._next_update = datetime.datetime.fromtimestamp(0)
            self.tick()

    def schedule_next(self, seconds):
        dt = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        print('Next freeview update %s' % dt)
        self._next_update = dt

    def update(self):
        gse = 'true' == self._addon.getSetting('genepg')
        if not gse:
            return False

        _playlist = 'special://home/addons/'+self._addon.getAddonInfo('id')+'/resources/playlist.m3u'
        if not os.path.exists(self._profile):
            os.makedirs(self._profile)
            
        workpath = os.path.join(self._profile, get_random_string(8) + 'work.epg.xml')
        path = os.path.join(self._profile, 'epg.xml')

        with io.open(xbmc.translatePath(_playlist), 'r', encoding='utf8') as file:
            m3u_data = file.read()
            file.close()    
        channels = m3u.process(m3u_data)
        now = datetime.datetime.now()
        epg = skylink.get_epg(channels, now, int(self._addon.getSetting('gen_days')))
        skylink.generate_xmltv(channels,epg,workpath)
        if os.path.isfile(path):
            os.unlink(path)
        os.rename(workpath, path)

        return True

    def tick(self):
        if datetime.datetime.now() > self._next_update:
            try:
                self.schedule_next(int(self._addon.getSetting('gen_delay')) * 60 * 60)
                if self.update():
                    self.notify(self._addon.getLocalizedString(30092))
            except Exception as e:
                traceback.print_exc()
                self.notify(str(e), True)

    def save(self):
        self._addon.setSetting('genepg_next_update', str(time.mktime(self._next_update.timetuple())))
        print('Saving freeview next update %s' % self._next_update)

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


if __name__ == '__main__':
    monitor = SkylinkMonitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            monitor.save()
            break
        monitor.tick()
