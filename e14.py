# -*- coding: utf-8 -*-
import urllib2, urllib
import zlib
from bs4 import BeautifulSoup

dep_activo = '01'
mun_activo = '001'
zona_activo = '01'
pues_activo = '01'
mydata = [('accion','cambiar_zona'),
          ('dep_activo',dep_activo),
          ('mun_activo',mun_activo),
          ('zona_activo',zona_activo),
          ('corp_activo','presidente'),
          ('token','7256d1299541f77c2892f29802119a730f9f22504bafbf7d5d235cb8337f3482')]
mydata=urllib.urlencode(mydata)
path = 'https://visor.e14digitalizacion.com/e14'
req=urllib2.Request(path, mydata)
req.add_header("authority","visor.e14digitalizacion.com")
req.add_header("method","POST")
req.add_header("path","/e14")
req.add_header("scheme","https")
req.add_header("accept","*/*")
req.add_header("accept-encoding","gzip, deflate, br")
req.add_header("accept-language","es-CO,es-419;q=0.9,es;q=0.8")
req.add_header("content-length","157")
req.add_header("content-type","application/x-www-form-urlencoded; charset=UTF-8")
req.add_header("cookie","__cfduid=d1475524650a2a6994404accd2b2710b21527727497; __cflb=3059022076; cf_clearance=6a2256390cc9b2af4b0d48ea295fb26ad2cd2bfd-1527727501-3600; SESSION=rufr84gc1us50mea6ngtja4s47")
req.add_header("origin","https://visor.e14digitalizacion.com")
req.add_header("referer","https://visor.e14digitalizacion.com/")
req.add_header("user-agent","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36")
req.add_header("x-requested-with","XMLHttpRequest")
page=urllib2.urlopen(req).read()

mydata = [('accion','cargar_mesas'),
          ('dep_activo',dep_activo),
          ('mun_activo',mun_activo),
          ('zona_activo',zona_activo),
          ('pues_activo',pues_activo),
          ('corp_activo','presidente'),
          ('token','7256d1299541f77c2892f29802119a730f9f22504bafbf7d5d235cb8337f3482')]
mydata=urllib.urlencode(mydata)
path = 'https://visor.e14digitalizacion.com/e14'
req=urllib2.Request(path, mydata)
req.add_header("authority","visor.e14digitalizacion.com")
req.add_header("method","POST")
req.add_header("path","/e14")
req.add_header("scheme","https")
req.add_header("accept","*/*")
req.add_header("accept-encoding","gzip, deflate, br")
req.add_header("accept-language","es-CO,es-419;q=0.9,es;q=0.8")
req.add_header("content-length","172")
req.add_header("content-type","application/x-www-form-urlencoded; charset=UTF-8")
req.add_header("cookie","__cfduid=d1475524650a2a6994404accd2b2710b21527727497; __cflb=3059022076; cf_clearance=6a2256390cc9b2af4b0d48ea295fb26ad2cd2bfd-1527727501-3600; SESSION=rufr84gc1us50mea6ngtja4s47")
req.add_header("origin","https://visor.e14digitalizacion.com")
req.add_header("referer","https://visor.e14digitalizacion.com/")
req.add_header("user-agent","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36")
req.add_header("x-requested-with","XMLHttpRequest")
page=urllib2.urlopen(req).read()

soup = BeautifulSoup(zlib.decompress(page, 16+zlib.MAX_WBITS), 'html.parser')
soup = soup.find_all('tbody')[0]
links = soup.find_all(href=True)
file = open("%s_%s_%s_%s/%s_%s_%s_%s.txt" % (dep_activo,mun_activo,zona_activo,pues_activo,"w")
for link in links:
    file.write(link['href'])
file.close()
