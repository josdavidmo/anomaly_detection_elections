from scraping import Scraping
import MySQLdb

HOST = 'localhost'
USER = 'root'
PASSWORD = 'root'
DB = 'registraduria'

db = MySQLdb.connect(HOST, USER, PASSWORD, DB)
cursor = db.cursor()

e14 = Scraping()
depts = e14.get_depts()
values = ",".join("('%s')" % ("','".join(dept)) for dept in depts)
query = "INSERT INTO departamento(id, name) VALUES %s" % (values)
cursor.execute(query)
db.commit()
for dept in depts:
    print "Getting for %s" % dept[1]
    muns = e14.get_muns(dept[0])
    values = ",".join("('%s','%s')" % ("','".join(mun), dept[0]) for mun in muns)
    query = "INSERT INTO municipio(id, name, id_departamento) VALUES %s" % (values)
    cursor.execute(query)
    db.commit()
    for mun in muns:
        zones = e14.get_zones(dept[0], mun[0])
        values = ",".join("('%s','%s','%s')" % ("','".join(zone), dept[0], mun[0]) for zone in zones)
        query = "INSERT INTO zona(id, name, id_departamento, id_municipio) VALUES %s" % (values)
        cursor.execute(query)
        db.commit()
        for zone in zones:
            puests = e14.get_puest(dept[0], mun[0], zone[0])
            values = ",".join("('%s','%s','%s','%s')" % ("','".join(puest), dept[0], mun[0], zone[0]) for puest in puests)
            query = "INSERT INTO puesto(id, name, id_departamento, id_municipio, id_zona) VALUES %s" % (values)
            cursor.execute(query)
            db.commit()
            for puest in puests:
                links = e14.get_mes(dept[0], mun[0], zone[0], puest[0])
                if len(links) != 0:
                    values = ",".join("('%s','%s','%s','%s','%s')" % ("','".join(link), dept[0], mun[0], zone[0], puest[0]) for link in links)
                    query = "INSERT INTO mesa(name, doc, id_departamento, id_municipio, id_zona, id_puesto) VALUES %s" % (values)
                    cursor.execute(query)
                    db.commit()
db.close()
