from flask import Flask, render_template,request,redirect,url_for # For flask implementation
from pymongo import MongoClient # Database connector
from bson.objectid import ObjectId # For ObjectId to work

client = MongoClient('localhost', 27017)    #Configure the connection to the database
db = client.reqdata    #Select the database
##reqs = db.req_data.find()

app = Flask(__name__)
title = "Req Search with Flask"
heading = "Req Search"



@app.route('/')
@app.route('/index')

def index():
##    reqdb = db.req_data
    reqcount = db.req_data.count()
    return render_template('index.html',
                          title='Home',
                           reqcount = reqcount)

@app.route('/mongoreqs', methods=['GET'])
def mongo_reqs():
##    reqdb = db.req_data #Select the collection
##    client = MongoClient()    #Configure the connection to the database
##    db = client.reqdata 
    reqs = db.req_data.find({})
    return render_template('mongoreqs.html',
                           title="Reqs in Mongo DB",
                           reqs=reqs)


if __name__ == "__main__":
    app.run(debug=True)
