#!/usr/bin/env python

from flask import Flask, render_template
import logging
import csv
import json
import validate
import accountServices
import handshake
import os

app = Flask(__name__)
app.debug = False

# Quiet down the web requests router
weblog = logging.getLogger('werkzeug')
weblog.setLevel(logging.ERROR)

# Perform Log setup
if not os.path.isdir("log"):
    os.mkdir("log")
logfile = os.path.join(os.path.abspath("log"), "accountService.log")
logging.basicConfig(level=logging.INFO, filename=logfile)
logging.info("Starting CV Account System")

def init():
    configLog = logging.getLogger("config")

    config = dict()
    config["ACL"] = dict()
    configDir = os.path.abspath("config")
    with open(os.path.join(configDir, "access.list"), 'r') as f:
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
        configLog.info("Loaded %s account records", len(config["ACL"]))

    with open(os.path.join(configDir, "words.txt"), 'r') as f:
        config["WORDS"] = [ s.strip() for s in f.read().split("\n") ]
        configLog.info("Loaded %s words", len(config["WORDS"]))

    with open(os.path.join(configDir, "blacklist.txt"), 'r') as f:
        config["BLACKLIST"] = [ s.strip() for s in f.read().split("\n") ]
        configLog.info("Loaded %s blacklisted phrases", len(config["BLACKLIST"]))

    with open(os.path.join(configDir, "settings.json"), 'r') as f:
        config.update(json.load(f))
        configLog.info("Loaded config file")

    return config


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/version")
def version():
    return "CV Account System - Version 0.0.2"


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
            handshake.sendPassword(netID, user, password)
            return json.dumps("Your password has been emailed to you")
        else:
            return json.dumps("An error occured, please contact an admin")


@app.route("/ums/changePassword/<netID>")
def passwordHandshake(netID):
    if validate.netID(netID):
        handshake.send(netID, acctMgr.uidFromNetID(netID), False)
        return json.dumps(True)
    else:
        return json.dumps(False)

@app.route("/ums/changePassword/<netID>/<user>/<hmac>/<time>/")
def chPassword(netID, user, hmac, time):
    if handshake.verify(netID, user, hmac, time):
        password = acctMgr.mkPassword()
        if acctMgr.chPassword(user, password):
            handshake.sendPassword(netID, user, password)
            return "Your password has been emailed to you"
        else:
            return "Your password could not be reset, please try again later"
    else:
        return "An error occured, perhaps you have an old link?"

# ------------- Begin Program Setup --------------
# Perform global config loading
config = init()

# Create core objects
validate = validate.Validate(config)
handshake = handshake.Handshake(config)
acctMgr = accountServices.Manager(config)


# If we're being loaded without uwsgi, configure the internal server
if __name__ == "__main__":
    host = config["SETTINGS"]["serverAddr"].split(":")[0]
    port = int(config["SETTINGS"]["serverAddr"].split(":")[1]) or 5000
    app.run(host, port)
