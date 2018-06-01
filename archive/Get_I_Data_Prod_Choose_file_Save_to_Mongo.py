
import httplib2
import tkinter as tk
from tkinter import filedialog
from tkinter import Tcl
import xml.etree.ElementTree as ET
from io import StringIO
import sqlite3
from flask import render_template, flash, redirect, session, url_for, request, g
##from flask_login import login_user, logout_user, current_user, login_required
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
import urllib

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
    user = "jcarter@abellavida.com"
    pw = "Punkllb14!"

    mongoUri = "mongodb+srv://%s:" + urllib.parse.quote("%s", safe='') + "@cluster0.mongodb.net/test" %(user, pw)
    print(mongoUri)
##    client = MongoClient()
##    client = MongoClient("192.168.1.194", 27107)
    client = MongoClient(mongoUri)
    dbtemp = client.temp
##    timestmp = datetime.datetime.now().strftime("%Y-%d-%d %H:%M:%S")
    timestmp = datetime.datetime.utcnow()
    
    xmlread = content.decode('ascii')
    xmlread = fromstring(xmlread)

    newfile = dumps(parker.data(xmlread))
    data = loads(newfile)
    result = dbtemp.new_Ireq_data.insert_one(data)

    db=client.Ireqdata

    copycursor = db.req_data.find()

##    db.req_archive.drop_indexes()
##    db.req_archive.reindex()
    db.req_data.drop_indexes()
    db.req_data.reindex()
    
    for document in copycursor:
        db.req_archive.insert(document)
        print (document)
    
    cursor = dbtemp.new_Ireq_data.distinct("Unit.Packet.Payload.ResultSet.Jobs.Job")
    for document in cursor:
        newreq = { "dateAdded": timestmp,
                   "req" : document}
        db.req_data.insert_one(newreq)
    dbtemp.new_Ireq_data.drop()

    

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
    if xfile != None:
        page = 1
        while (page < 101):
            tree = ET.parse(xfile)
            xroot = tree.getroot()
            for fpage in xroot.iter('PageNumber'):
                fpage.text = str(page)
            xmlfile = ET.tostring(xroot)
            xmlfile = xmlfile.decode('ascii', 'ignore')
##            print (xmlfile)

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

