from pymongo import MongoClient
import pprint
from datetime import datetime, timedelta


##client = MongoClient()
client = MongoClient('mongodb+srv://paliaso:5Macacos@cluster0-dt4go.mongodb.net/test?retryWrites=true')
##db = client.testreqs
##db = client.newtest
db = client.reqdata
##db = client.temp

##cursor = db.raw_req_data.find({})
##cursor = db.new_req_data.distinct("Unit.Packet.Payload.ResultSet.Jobs.Job")
##cursor = db.req_data.find()
cursor = db.req_data.find(
    {
        "dateAdded": 
        {
            $gte: new Date((new Date().getTime() - (15 * 24 * 60 * 60 * 1000)))
        }
    }).sort({ "dateAdded": -1 })


##cursor = db.req_data.drop()

##cursor = db.req_data.distinct("req.Question")
##cursor = db.req_data.find()

for document in cursor:
##    pprint.pprint(document)
    print(document)

reqcount = db.req_data.count()
print (client)
print (cursor)
print (db)
print("There are ",reqcount," reqs in the database")

