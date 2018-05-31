from flask import Flask, render_template,request,redirect,url_for # For flask implementation
from pymongo import MongoClient # Database connector
from bson.objectid import ObjectId # For ObjectId to work
from bson import Timestamp
import json
from datetime import datetime, timedelta
##from jinja2 import Template
##from bson.json_util import dumps


##client = MongoClient('localhost', 27017)    #Configure the connection to the database    client = MongoClient('mongodb+srv://paliaso:5Macacos@cluster0-dt4go.mongodb.net/test?retryWrites=true')
client = MongoClient('mongodb+srv://paliaso:5Macacos@cluster0-dt4go.mongodb.net/test?retryWrites=true')

db = client.reqdata    #Select the database
reqs = db.req_data

app = Flask(__name__)
title = "Req Search with Flask"
heading = "Req Search"



@app.route('/')
@app.route('/index')

def index():
##    reqdb = db.req_data
    reqcount = db.req_data.count()
##    lastupdate = db.req_data.find({'timestamp'})
    return render_template('index.html',
                          title='Home',
                           reqcount = reqcount)

@app.route('/mongoreqs', methods=['GET'])
def mongo_reqs():
##    reqdb = db.req_data #Select the collection
##    client = MongoClient()    #Configure the connection to the database
##    db = client.reqdata 
    
##    reqs = dumps(db.req_data.find())
##    timestmp = timedelta(7) #.strptime("%Y-%m-%d %H:%M:%S")
##    timestmp = Timestamp(timestmp)
####    lastweek = timedelta(-7)
##    reqs_1 = reqs.find({ 'dateAdded': {'$gte': timestmp}})
    reqs_1 = reqs.find({})

##    reqs = json.loads(reqs)
    return render_template('mongoreqs.html',
                           title="Reqs in Mongo DB",
                           reqs=reqs_1)


if __name__ == "__main__":
    app.run(debug=True)
