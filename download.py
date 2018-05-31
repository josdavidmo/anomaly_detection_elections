import urllib.request
files = ["01_001_01_01/01_001_01_01.txt"]
for file in files:
    file = open(file,"r")
    for line in file.readlines():
        opener = urllib.request.build_opener()
        opener.addheaders = [("authority","visor.e14digitalizacion.com"),
                            ("method","GET"),
                            ("path",line.replace("\n","").replace("https://visor.e14digitalizacion.com","")),
                            ("scheme","https"),
                            ("accept","text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"),
                            ("accept-encoding","gzip, deflate, br"),
                            ("accept-language","es-CO,es-419;q=0.9,es;q=0.8"),
                            ("cookie","__cfduid=d1475524650a2a6994404accd2b2710b21527727497; __cflb=3059022076; cf_clearance=6a2256390cc9b2af4b0d48ea295fb26ad2cd2bfd-1527727501-3600; SESSION=rufr84gc1us50mea6ngtja4s47"),
                            ("referer","https://visor.e14digitalizacion.com/"),
                            ("upgrade-insecure-requests","1"),
                            ("user-agent","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36")]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(line.replace("\n",""), "01_001_01_01/"+line.replace("\n","").replace("https://visor.e14digitalizacion.com/e14_divulgacion/01/001/001/PRE/",""))
    file.close()
