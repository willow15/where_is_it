import urllib
import json
import ssl
import sqlite3
import time

serviceurl = "https://maps.googleapis.com/maps/api/geocode/json?"
apikey = None # my apikey is secret


conn = sqlite3.connect("geodata.sqlite")
cur = conn.cursor()
cur.executescript('''
    DROP TABLE IF EXISTS Locations;
    CREATE TABLE Locations(address TEXT, geodata TEXT)''')

fh = open("where.data")
for line in fh:
    address = line.strip()

    # fetch address information from the database
    cur.execute("SELECT geodata FROM Locations WHERE address = ?", (address, ))
    try:
        data = cur.fetchone()[0]
        continue
    except:
        pass

    # resolve address if it doesn't exist in the database
    url = serviceurl + urllib.urlencode({"key": apikey, "address": address})
    uh = urllib.urlopen(url)
    data = uh.read()
    try:
        js = json.loads(str(data))
    except:
        continue

    if "status" not in js or (js["status"] !=  "OK" and js["status"] != "ZERO_RESULTS"):
        print "=== Failure To Retrieve ==="
        print data
        continue

    cur.execute('''INSERT INTO Locations(address, geodata)
    VALUES(?, ?)''', (buffer(address), buffer(data)))

conn.commit()
cur.close()
