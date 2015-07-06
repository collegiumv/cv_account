#!/usr/bin/env python

from flask import Flask, request
import logging, csv, json

app = Flask(__name__)
app.debug = True

@app.route("/")
def version():
    return "CV Account System - Version 0.0.1"

@app.route("/ums/validate/netID/<netID>")
def validateNetID(netID):
    if any(netID in acct for acct in users):
        return "valid NETID"
    else:
        return "bad NETID"

@app.route("/ums/validate/uname/<user>")
def validateUser(user):
# return true for now, eventually ldap to make sure there is no collision
    return true

def init():
    users=list()
    with open('account_access.list','r') as f:
        accounts=csv.reader(f)
        for account in accounts:
            users.append(account)
        return users

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    users = init()
    app.run(host='0.0.0.0')
