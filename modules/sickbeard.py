import cherrypy
import htpc
from urllib import quote
from urllib2 import urlopen
from json import loads
import logging

class Sickbeard:
    def __init__(self):
        self.logger = logging.getLogger('modules.sickbeard')
        htpc.MODULES.append({
            'name': 'Sickbeard',
            'id': 'sickbeard',
            'test': htpc.WEBDIR + 'sickbeard/ping',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'sickbeard_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'sickbeard_name'},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'sickbeard_host'},
                {'type': 'text', 'label': 'Port *', 'name': 'sickbeard_port'},
                {'type': 'text', 'label': 'API key', 'name': 'sickbeard_apikey'},
                {'type': 'text', 'label': 'Basepath (starts with a slash)', 'name': 'sickbeard_basepath'},
                {'type': 'select', 'label': 'View type', 'name': 'sickbeard_view', 'options':[
                    {'name': 'List', 'value': 'list'},
                    {'name': 'Posters', 'value': 'poster'},
                    {'name': 'Banners', 'value': 'banner'}
                ]}
        ]})

    @cherrypy.expose()
    def index(self):
        view = htpc.settings.Settings().get('sickbeard_view', 'list')
        return htpc.LOOKUP.get_template('sickbeard.html').render(scriptname='sickbeard', view=view)

    @cherrypy.expose()
    def view(self, tvdbid):
        if not (tvdbid.isdigit()):
          raise cherrypy.HTTPError("500 Error", "Invalid show ID.")
          self.logger.error("Invalid show ID was supplied: " + str(tvdbid))
          return False

        return htpc.LOOKUP.get_template('sickbeard_view.html').render(scriptname='sickbeard_view', tvdbid=tvdbid)

    @cherrypy.expose()
    def ping(self, sickbeard_host, sickbeard_port, sickbeard_apikey, sickbeard_basepath, **kwargs):
        self.logger.debug("Testing connectivity")
        try:
            if(sickbeard_basepath == ""):
                sickbeard_basepath = "/"
            if not (sickbeard_basepath.endswith('/')):
              sickbeard_basepath += "/"

            url = 'http://' + sickbeard_host + ':' + sickbeard_port + sickbeard_basepath + 'api/' + sickbeard_apikey + '/?cmd='
            self.logger.debug("Trying to contact sickbeard via " + url)
            response = urlopen(url + 'sb.ping', timeout=10).read()
            responseDict = loads(response)
            if responseDict.get('result') == "success":
                cherrypy.response.headers['Content-Type'] = 'application/json'
                return response
        except:
            self.logger.error("Unable to contact sickbeard via " + url)
            return

    @cherrypy.expose()
    def GetShowList(self):
        self.logger.debug("Fetching Show list")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.fetch('shows&sort=name')

    @cherrypy.expose()
    def GetNextAired(self):
        self.logger.debug("Fetching Next Aired Episodes")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.fetch('future')

    @cherrypy.expose()
    def GetBanner(self, tvdbid):
        self.logger.debug("Fetching Banner")
        cherrypy.response.headers['Content-Type'] = 'image/jpeg'
        return self.fetch('show.getbanner&tvdbid=' + tvdbid, True)

    @cherrypy.expose()
    def GetPoster(self, tvdbid):
        self.logger.debug("Fetching Poster")
        cherrypy.response.headers['Content-Type'] = 'image/jpeg'
        return self.fetch('show.getposter&tvdbid=' + tvdbid, True)

    @cherrypy.expose()
    def GetHistory(self, limit=''):
        self.logger.debug("Fetching History")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.fetch('history&limit=' + limit)

    @cherrypy.expose()
    def GetLogs(self):
        self.logger.debug("Fetching Logs")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.fetch('logs&min_level=info')

    @cherrypy.expose()
    def AddShow(self, tvdbid):
        self.logger.debug("Adding a Show")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.fetch('show.addnew&tvdbid=' + tvdbid)

    @cherrypy.expose()
    def GetShow(self, tvdbid):
        self.logger.debug("Fetching Show")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.fetch('show&tvdbid=' + tvdbid)

    @cherrypy.expose()
    def GetSeason(self, tvdbid, season):
        self.logger.debug("Fetching Season")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.fetch('show.seasons&tvdbid=' + tvdbid + '&season=' + season)

    @cherrypy.expose()
    def SearchEpisodeDownload(self, tvdbid, season, episode):
        self.logger.debug("Fetching Episode Downloads")
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return self.fetch('episode.search&tvdbid=' + tvdbid + '&season=' + season + '&episode=' + episode, False, 45)

    @cherrypy.expose()
    def SearchShow(self, query):
        try:
            url = 'http://www.thetvdb.com/api/GetSeries.php?seriesname=' + quote(query)
            return urlopen(url, timeout=10).read()
        except:
            return

    def fetch(self, cmd, img=False, timeout = 10):
        try:
            settings = htpc.settings.Settings()
            host = settings.get('sickbeard_host', '')
            port = str(settings.get('sickbeard_port', ''))
            apikey = settings.get('sickbeard_apikey', '')
            sickbeard_basepath = settings.get('sickbeard_basepath', '/')

            if(sickbeard_basepath == ""):
                sickbeard_basepath = "/"
            if not (sickbeard_basepath.endswith('/')):
              sickbeard_basepath += "/"
            url = 'http://' + host + ':' + str(port) + sickbeard_basepath + 'api/' + apikey + '/?cmd=' + cmd

            self.logger.debug("Fetching information from: " + url)

            return urlopen(url, timeout=timeout).read()
        except:
            self.logger.error("Unable to fetch information from: " + url)
            return
