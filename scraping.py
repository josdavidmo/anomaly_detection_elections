# -*- coding: utf-8 -*-
import urllib2
import urllib
import zlib
from bs4 import BeautifulSoup


class Scraping:
    """docstring for Scraping."""

    def __init__(self):
        self.PATH = 'visor.e14digitalizacion.com'
        self.COOKIE = '__cfduid=dea37c55781b85fe808ab9ddd963267751527728812; __cflb=1459906015; cf_clearance=65734bd144cd0785d48d5a255801a0a2b2b21cd7-1527728817-3600; SESSION=q2jc2cit672m7tmjg01ttsvrg5'
        self.TOKEN = 'a53ba4a90df6f048c67eaf708a42b3bc3154b3285d280171a7d58000c0e11105'
        self.CONTENT_LENGTH_DEPT = "128"
        self.CONTENT_LENGTH_MUN = "135"
        self.CONTENT_LENGTH_ZONE = "147"
        self.CONTENT_LENGTH_PUEST = "157"
        self.CONTENT_LENGTH_MES = "172"
        self.ACTION_MES = 'cargar_mesas'
        self.ACTION_PUEST = 'cambiar_zona'
        self.ACTION_ZONE = 'cambiar_municipio'
        self.ACTION_MUN = 'cambiar_departamento'
        self.ACTION_DEPT = 'cargar_departamentos_select'
        self.USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'

    def __get_data__(self, data, content_length):
        req = urllib2.Request("https://%s/e14" % (self.PATH), data)
        req.add_header("authority", self.PATH)
        req.add_header("method", "POST")
        req.add_header("path", "/e14")
        req.add_header("scheme", "https")
        req.add_header("accept", "*/*")
        req.add_header("accept-encoding", "gzip, deflate, br")
        req.add_header("accept-language", "es-CO,es;q=0.9,de-DE;q=0.8,de;q=0.7,en-US;q=0.6,en;q=0.5")
        req.add_header("content-length", content_length)
        req.add_header("content-type", "application/x-www-form-urlencoded; charset=UTF-8")
        req.add_header("cookie", self.COOKIE)
        req.add_header("origin", "https://%s" % (self.PATH))
        req.add_header("referer", "https://%s/" % (self.PATH))
        req.add_header("user-agent", self.USER_AGENT)
        req.add_header("x-requested-with", "XMLHttpRequest")
        page = urllib2.urlopen(req).read()
        return page

    def get_depts(self):
        mydata = [('accion', self.ACTION_DEPT),
                  ('corp_activo', 'presidente'),
                  ('token', self.TOKEN)]
        mydata = urllib.urlencode(mydata)
        page = self.__get_data__(mydata, self.CONTENT_LENGTH_DEPT)
        soup = BeautifulSoup(zlib.decompress(
            page, 16 + zlib.MAX_WBITS), 'html.parser')
        soup = soup.find_all('option')
        dept = [["%02d" % (int(option['value'])), option.text] for option in soup]
        return dept

    def get_muns(self, dept_id):
        mydata = [('accion', self.ACTION_MUN),
                  ('dep_activo', dept_id),
                  ('corp_activo', 'presidente'),
                  ('token', self.TOKEN)]
        mydata = urllib.urlencode(mydata)
        page = self.__get_data__(mydata, self.CONTENT_LENGTH_MUN)
        soup = BeautifulSoup(zlib.decompress(
            page, 16 + zlib.MAX_WBITS), 'html.parser')
        soup = soup.find_all('option')
        mun = [["%03d" % (int(option['value'])), option.text] for option in soup]
        return mun

    def get_zones(self, dept_id, mun_id):
        mydata = [('accion', self.ACTION_ZONE),
                  ('dep_activo', dept_id),
                  ('mun_activo', mun_id),
                  ('corp_activo', 'presidente'),
                  ('token', self.TOKEN)]
        mydata = urllib.urlencode(mydata)
        page = self.__get_data__(mydata, self.CONTENT_LENGTH_ZONE)
        soup = BeautifulSoup(zlib.decompress(
            page, 16 + zlib.MAX_WBITS), 'html.parser')
        soup = soup.find_all('option')
        zones = [["%02d" % (int(option['value'])), option.text] for option in soup if option['value'] != u'-1']
        return zones

    def get_puest(self, dept_id, mun_id, zone_id):
        mydata = [('accion', self.ACTION_PUEST),
                  ('dep_activo', dept_id),
                  ('mun_activo', mun_id),
                  ('zona_activo', zone_id),
                  ('corp_activo', 'presidente'),
                  ('token', self.TOKEN)]
        mydata = urllib.urlencode(mydata)
        page = self.__get_data__(mydata, self.CONTENT_LENGTH_PUEST)
        soup = BeautifulSoup(zlib.decompress(
            page, 16 + zlib.MAX_WBITS), 'html.parser')
        soup = soup.find_all('option')
        puest = [["%02d" % (int(option['value'])), option.text] for option in soup if option['value'] != u'-1']
        return puest

    def get_mes(self, dept_id, mun_id, zone_id, puest_id):
        mydata = [('accion', self.ACTION_MES),
                  ('dep_activo', dept_id),
                  ('mun_activo', mun_id),
                  ('zona_activo', zone_id),
                  ('pues_activo', puest_id),
                  ('corp_activo', 'presidente'),
                  ('token', self.TOKEN)]
        mydata = urllib.urlencode(mydata)
        page = self.__get_data__(mydata, self.CONTENT_LENGTH_MES)
        soup = BeautifulSoup(zlib.decompress(
            page, 16 + zlib.MAX_WBITS), 'html.parser')
        soup = soup.find_all('tbody')[0]
        links = soup.find_all(href=True)
        mes = [link['href'] for link in links]
        return mes
