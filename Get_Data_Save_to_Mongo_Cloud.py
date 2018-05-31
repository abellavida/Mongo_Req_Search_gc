
import httplib2
import tkinter as tk
from tkinter import filedialog
from tkinter import Tcl
import xml.etree.ElementTree as ET
from io import StringIO
import sqlite3
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import form
import datetime
##from app import db, models
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
import json
from json import dumps
from collections import OrderedDict
from xmljson import BadgerFish
from xmljson import parker, Parker
from xml.etree.ElementTree import tostring, fromstring
from bson.json_util import loads
from bson.objectid import ObjectId

##from models import QIDMapping, TG_Results

http = httplib2.Http()
headers = {'Content-Type':'application/x-www-form-urlencoded'}
url = """http://import.brassring.com/WebRouter/WebRouter.asmx/route"""

#body = open("c:/Pyfiles/Web API Scripts/Canada_Stage_Test_2.txt", 'r')
##kxa_out = open("c:/TEST/ResponseXML/Data_out.xml", 'w')

input_xml=''
kxa_output = []

#xml_in = body.read()



def get_data(input_xml):
    tg_data = []
    input_xml = ("inputXml=%s" %input_xml)
##    print (input_xml)
    
    response, content = http.request(uri=url, method='POST', headers=headers, body=input_xml)
    
    kxa_output = str(content)
##    print ("Content", content)
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()

    out_xml = root.text
    out_xml = out_xml.encode('ascii', 'ignore')

    save_to_mongo(out_xml)
    

def save_to_mongo(content):
##    client = MongoClient()
##    client = MongoClient("192.168.1.169", 27107)
    client = MongoClient('mongodb+srv://paliaso:5Macacos@cluster0-dt4go.mongodb.net/test?retryWrites=true')
    dbtemp = client.temp
    timestmp = datetime.datetime.utcnow()
    
    xmlread = content.decode('ascii')
    xmlread = fromstring(xmlread)

    newfile = dumps(parker.data(xmlread))
    data = loads(newfile)
    result = dbtemp.new_req_data.insert_one(data)

    db=client.reqdata
    
    cursor = dbtemp.new_req_data.distinct("Unit.Packet.Payload.ResultSet.Jobs.Job")
    for document in cursor:
        newreq = { "dateAdded": timestmp,
                   "req" : document}
        db.req_data.insert_one(newreq)
    dbtemp.new_req_data.drop()
    print("New Reqs Added")


def move_to_archive():
##    client = MongoClient()
##    client = MongoClient('mongodb://paliaso:5Macacos@mycluster0-shard-00-00.mongodb.net:27017,mycluster0-shard-00-01.mongodb.net:27017,mycluster0-shard-00-02.mongodb.net:27017/admin?ssl=true&replicaSet=Mycluster0-shard-0&authSource=admin')
    client = MongoClient('mongodb+srv://paliaso:5Macacos@cluster0-dt4go.mongodb.net/test?retryWrites=true')
    db=client.reqdata
    dbarchive=client.reqarchive

    source = db.req_data.find()
    destination = dbarchive.req_archive
    dest_ids = dbarchive.req_archive.distinct("_id", {}, {})

    for doc in source:
        source_id = doc.get("_id")
        if source_id in dest_ids:
            pass
        else:
            destination.insert(doc)

    db.req_data.drop()
    print("req table dropped")


def X_save_to_mongo(q_id, q_tag, q_text):
    client = MongoClient()
    db = client.testreqs
    timestmp = datetime.datetime.now().strftime("%Y-%d-%d %H:%M:%S")

    result = db.raw_req_data.insert_one(
        {
            "req":
            {
                "qid": q_id,
                "tag": q_tag,
                "text": q_text,
                "timestamp": timestmp
                }
            }
   )

def main():

    root = tk.Tk()
    root.withdraw()
    
    xfile = filedialog.askopenfilename(parent=root)
##    input_xml = filename.read()
##    print (xfile)

    move_to_archive()
    print("Archived")    

##    with open("//home//jc//Documents//XML Files//FGB_Prod_Input.xml", "r") as xfile:
    if xfile != None:
        page = 1
        while (page < 101):
            tree = ET.parse(xfile)
            xroot = tree.getroot()
            for fpage in xroot.iter('PageNumber'):
                fpage.text = str(page)
            xmlfile = ET.tostring(xroot)
            xmlfile = xmlfile.decode('ascii', 'ignore')
##            print(xmlfile)

##            input_xml = open(xmlfile)
##            r = input_xml.read()
            get_data(xmlfile)
##            print (page)
            page +=1

    else:
        print ("had to pass")    

    

if __name__ == '__main__':
    main()

    
#body.close()
#kxa_out.close()

