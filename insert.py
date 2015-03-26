import sys, csv, pymongo
from time import time

conn = pymongo.MongoClient("mongodb://localhost")
db = conn.ews
coll = db.mdm

count = 0
t0 = time()

with open('MDM_AGT.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        doc = {'agt_name' : row['agent_name'],
           'branch' : row['branch'],
           'iata_no' : row['iata_no'],
           'dipc' : row['dipc'],
           'institution' : row['institution'],
           'inv_type' : row['inv_type'],
           'status' : row['status']}
        try:
            count += 1
            coll.insert(doc)
        except:
            print "insert failed - line %d, iata_no %s" % (count, row['iata_no'])
            continue

print "processing time:", round(time()-t0, 3), "s"
print "%d rows data was inserted into MongoDB" % count


