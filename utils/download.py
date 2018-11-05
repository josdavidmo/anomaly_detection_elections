import os
import urllib2
from multiprocessing import Pool

import MySQLdb

HOST = 'localhost'
USER = 'root'
PASSWORD = 'root'
DB = 'registraduria'
BATCH_SIZE = 1000


def download_file(args):
    start, length = args
    print "Downloading %s - %s (%s)" % (start, (start + length), os.getpid())
    query = "SELECT * FROM mesa WHERE downloaded = 0 LIMIT %s, %s" % (start, length)
    db = MySQLdb.connect(HOST, USER, PASSWORD, DB)
    cursor = db.cursor()
    cursor.execute(query)
    for document in cursor.fetchall():
        directory = "%s/%s/%s/%s/" % (document[4],
                                      document[5], document[6], document[2])

        if not os.path.exists(directory):
            os.makedirs(directory)
        #print ("INSERT IN directory %s , path %s, file %s" % (
        #    directory + document[1] + ".pdf", document[3].replace("https://visor.e14digitalizacion.com", ""), document[0]))
        opener = urllib2.build_opener()

        opener.addheaders = [("authority", "visor.e14digitalizacion.com"),
                             ("method", "GET"),
                             ("path", document[3].replace(
                                 "https://visor.e14digitalizacion.com", "")),
                             ("scheme", "https"),
                             ("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"),
                             ("accept-encoding", "gzip, deflate, br"),
                             ("accept-language",
                              "es-CO,es;q=0.9,de-DE;q=0.8,de;q=0.7,en-US;q=0.6,en;q=0.5"),
                             ("cookie", "__cfduid=dea37c55781b85fe808ab9ddd963267751527728812; __cflb=1459906015; SESSION=q2jc2cit672m7tmjg01ttsvrg5; cf_clearance=671d9f8efc8f47c4473e0fd70d83ce78292345dd-1527810470-3600"),
                             ("referer", "https://visor.e14digitalizacion.com/"),
                             ("upgrade-insecure-requests", "1"),
                             ("user-agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36")]
        urllib2.install_opener(opener)
        f = urllib2.urlopen(document[3])
        data = f.read()
        with open(directory + document[1] + ".pdf", "wb") as code:
            code.write(data)
        query = "UPDATE mesa SET downloaded = 1 WHERE id_mesa = %s" % (document[0])
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
    db.close()


if __name__ == "__main__":
    db = MySQLdb.connect(HOST, USER, PASSWORD, DB)
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM mesa WHERE downloaded = 0")
    result = cursor.fetchone()
    db.close()
    total = int(result[0])
    args_queue = []
    for start in range(0, total, BATCH_SIZE):
        length = min(BATCH_SIZE, total - start)
        args_queue.append((start, length))
    pool = Pool(8)
    pool.map(download_file, args_queue)
    pool.close()
    pool.join()
