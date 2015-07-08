#!/usr/bin/env python

from flask import Flask, request
import logging, csv, json, validate, accountServices, handshake

app = Flask(__name__)
app.debug = True

def init():
    config = dict()
    config["ACL"]=dict()
    with open('account_access.list','r') as f:
        accounts=csv.reader(f)
        for account in accounts:
            if len(account)==0:
                logging.debug("Skipping blank line in file")
                continue
            if any("#" in s for s in account[0]):
                logging.debug("Drop comment %s", account)
                continue
            logging.debug("Loaded account record %s", account)
            config["ACL"][account[2]] = [account[1], account[0]]

    with open('settings.json', 'r') as f:
        config.update(json.load(f))
        logging.info("Loaded config file")

    return config

@app.route("/")
def version():
    return "CV Account System - Version 0.0.1"

@app.route("/ums/validate/netID/<netID>")
def realtimeNetID(netID):
    return json.dumps(validate.netID(netID))

@app.route("/ums/validate/uname/<user>")
def realtimeUsername(user):
    return json.dumps(validate.user(user))

@app.route("/ums/provision/<netID>/<user>/")
def IDConfirm(netID, user):
    if validate.netID(netID) and validate.user(user):
        handshake.send(netID, user)
    return json.dumps(True)

@app.route("/ums/provision/<netID>/<user>/<hmac>/<time>/")
def provisionAcct(netID, user, hmac, time):
    if json.dumps(handshake.verify(netID, user, hmac, time)):
        return "Account provisioned"

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    config = init()
    validate = validate.Validate(config)
    handshake = handshake.Handshake(config)
    acctMgr = accountServices.Manager(config)
    app.run(host='0.0.0.0')
