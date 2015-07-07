#!/usr/bin/env python

from flask import Flask, request
import logging, csv, json, validate

app = Flask(__name__)
app.debug = True

@app.route("/")
def version():
    return "CV Account System - Version 0.0.1"

@app.route("/ums/validate/netID/<netID>")
def realtimeNetID(netID):
    return json.dumps(validate.netID(users, netID))

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
        validate = validate.Validation(users)
        return validate

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    validate = init()
    app.run(host='0.0.0.0')
