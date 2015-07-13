#!/usr/bin/env python

from flask import Flask, render_template
import logging
import csv
import json
import validate
import accountServices
import handshake

app = Flask(__name__)
app.debug = True

weblog = logging.getLogger('werkzeug')
weblog.setLevel(logging.ERROR)


def init():
    configLog = logging.getLogger("config")

    config = dict()
    config["ACL"] = dict()
    with open('account_access.list', 'r') as f:
        accounts = csv.reader(f)
        for account in accounts:
            if len(account) == 0:
                configLog.debug("Skipping blank line in file")
                continue
            if any("#" in s for s in account[0]):
                configLog.debug("Drop comment %s", account)
                continue
            configLog.debug("Loaded account record %s", account)
            config["ACL"][account[2]] = [account[1], account[0]]

    with open('words.txt', 'r') as f:
        config["WORDS"] = f.read().split("\n")
        configLog.info("Loaded %s words", len(config["WORDS"]))

    with open('settings.json', 'r') as f:
        config.update(json.load(f))
        configLog.info("Loaded config file")

    return config


@app.route("/")
def index():
    return render_template('index.html')

def version():
    return "CV Account System - Version 0.0.1"


@app.route("/ums/validate/netID/<netID>")
def realtimeNetID(netID):
    return json.dumps(validate.netID(netID))


@app.route("/ums/validate/uname/<user>")
def realtimeUsername(user):
    return json.dumps(validate.user(user))


@app.route("/ums/validate/exists/byNetID/<netID>")
def accountByNetID(netID):
    return json.dumps(acctMgr.netIDExists(netID))


@app.route("/ums/validate/exists/byUID/<uid>")
def accountByUID(uid):
    return json.dumps(acctMgr.uidExists(uid))


@app.route("/ums/provision/<netID>/<user>/")
def IDConfirm(netID, user):
    if validate.netID(netID) and validate.user(user):
        handshake.send(netID, user)
    return json.dumps(True)


@app.route("/ums/provision/<netID>/<user>/<hmac>/<time>/")
def provisionAcct(netID, user, hmac, time):
    if handshake.verify(netID, user, hmac, time):
        password = acctMgr.mkPassword()
        if acctMgr.provision(netID, user, password):
            handshake.sendPassword(netID, password)
            return "Account provisioned"
        else:
            return "Your account could not be provisioned at this time."


@app.route("/exists/<username>")
def exists(username):
    return json.dumps(acctMgr.checkAccount(username))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    config = init()
    validate = validate.Validate(config)
    handshake = handshake.Handshake(config)
    acctMgr = accountServices.Manager(config)

    host = config["SETTINGS"]["serverAddr"].split(":")[0]
    port = int(config["SETTINGS"]["serverAddr"].split(":")[1]) or 5000
    app.run(host, port)
