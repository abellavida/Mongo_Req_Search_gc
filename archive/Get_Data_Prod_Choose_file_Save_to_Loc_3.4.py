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
    response, content = http.request(uri=url, method='POST', headers=headers, body=input_xml)

    
    kxa_output = str(content)
##    print ("Content", content)
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()
##    print('root :', root)
    out_xml = root.text
    out_xml = out_xml.encode('ascii', 'ignore')
##    print (out_xml, '\n')
##    kxa_out.write(out_xml)
    res_tree = ET.ElementTree(ET.fromstring(out_xml))
    res_root = res_tree.getroot()
    for i in res_root.find('Unit'):
        y = i.get('Packet')
##        print ('y:', y)
        z = i.iter('Job')
##        print ('Z:', z)
        n = 0
        for q in z: 
            n = n + 1
##            print (n)
            for j in q.iterfind('Question'):
##                print (j.attrib)
                question = j.tag
                qidnum = []
##                for tag, value in j.attrib.values():
##                    print (value)
                qidnum = j.attrib.get('Id')
                qidnum = int(qidnum)
##                print (qidnum)

                fieldtext = j.text
##                print ('\n Question: ', question, '\n QID ', qidnum, '\n Text:', fieldtext)
##                save_to_db(qidnum, question, fieldtext)

##    xmlread = fromstring(content)
    save_to_mongo(out_xml)
    
####    self = filedialog.asksaveasfilename(title="Select a File")
####    with open(self, 'wb') as output:
####        output.write(out_xml)
####        output.close()
##    kxa_out.close()


def save_to_mongo(content):
    client = MongoClient()
    dbtemp = client.temp
    timestmp = datetime.datetime.now().strftime("%Y-%d-%d %H:%M:%S")

    xmlread = content.decode('ascii')
    xmlread = fromstring(xmlread)
##    bf = BadgerFish(dict_type=OrderedDict)

    newfile = dumps(parker.data(xmlread))
    data = loads(newfile)
##    print (data)
    result = dbtemp.new_req_data.insert_one(data)
##    print("Result: ", result)

    db=client.reqdata
    cursor = dbtemp.new_req_data.distinct("Unit.Packet.Payload.ResultSet.Jobs.Job")
    for document in cursor:
        newreq = { "timestamp": timestmp,
                   "req" : document}
        print (newreq)
        db.req_data.insert_one(newreq)
    
def save_to_db(q_id, q_tag, q_text):

    conn = sqlite3.connect("bcg.db")
    cur = conn.cursor()
    cur.execute("Select id, qid_number, br_field_name, vendor_field from QIDMap")
    data = cur.fetchall()
##    print (len(data))
##    for i in data:
##        print("\n",i)
    timestmp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for row in data:
##        print('row[1]: ',row[1], "q_id: ", q_id, '\n')
##        print (row[2], '\t', q_tag, '\n')
        if row[1] == q_id:
##            print ("Match \n")
            cur.execute("Insert into TGResults(qid, xml_tag, xml_text, timestamp, qid_pk) \
                              Values (?, ?, ?, ?, ?)", (q_id, q_tag, q_text, timestmp, row[0]))          
        elif row[2] == q_tag:
            cur.execute("Insert into TGResults(qid, xml_tag, xml_text, timestamp, qid_pk) \
                              Values (?, ?, ?, ?, ?)", (q_id, q_tag, q_text, timestmp, row[0]))
        else:
##            print("No Match \n")
            pass
    conn.commit()
    conn.close()



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
            root = tree.getroot()
            for fpage in root.iter('PageNumber'):
                fpage.text = str(page)
            xmlfile = ET.tostring(root)

##            input_xml = open(xmlfile)
##            r = input_xml.read()
            get_data(xmlfile)
        page +=1
    else:
        print ("had to pass")    

    

if __name__ == '__main__':
    main()

    
#body.close()
#kxa_out.close()

