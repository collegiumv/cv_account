import logging
import random
import ldap
import kadmin
import socket
from papercut import PaperCut

class Manager:
    def __init__(self, config):
        self.loungeACL = config["ACL"]
        self.config = config
        self.words = config["WORDS"]
        self.logger = logging.getLogger("AcctServices")
        self.kadm = kadmin.init_with_keytab(config["krb5"]["aprinc"],
                                            config["krb5"]["atab"])
        self.mailDomain = config["SETTINGS"]["mailDomain"]
        self.gidNumber = config["SETTINGS"]["userGID"]
        self.fileServerAddress = config["SETTINGS"]["fileServerAddress"]
        self.fileServerPort = config["SETTINGS"]["fileServerPort"]
        self.pc = PaperCut(config["papercut"]["url"], config["papercut"]["secret"])

    def uidExists(self, username):
        conn = self.connectLDAP()
        result = conn.search_s("ou=people,dc=collegiumv,dc=org",
                               ldap.SCOPE_SUBTREE,
                               "(uid={0})".format(username), attrlist=["uid"])
        conn.unbind()
        self.logger.debug("Account %s exists? %s", username, bool(len(result)))
        return bool(len(result))

    def netIDExists(self, netID):
        conn = self.connectLDAP()
        result = conn.search_s("ou=people,dc=collegiumv,dc=org",
                               ldap.SCOPE_SUBTREE,
                               "(netID={0})".format(netID),
                               attrlist=["netID"])
        conn.unbind()
        self.logger.debug("Account %s exists? %s", netID, bool(len(result)))
        return bool(len(result))

    def uidFromNetID(self, netID):
        conn = self.connectLDAP()
        result = conn.search_s("ou=people,dc=collegiumv,dc=org",
                               ldap.SCOPE_SUBTREE,
                               "(netID={0})".format(netID), attrlist=["uid"])
        conn.unbind()
        return result[0][1]['uid'][0]

    def provision(self, netID, username, password):
        success = False

        fname = self.loungeACL[netID][0]
        lname = self.loungeACL[netID][1]
        ObjectClass = ["inetOrgPerson", "posixAccount", "cvPerson"]
        userDN = "uid="+username+",ou=people,dc=collegiumv,dc=org"

        # create the ldap values
        ldapAttrs = list()
        ldapAttrs.append(("objectClass", ObjectClass))
        ldapAttrs.append(("cn", [fname + ' ' + lname]))
        ldapAttrs.append(("sn", [lname]))
        ldapAttrs.append(("ou", ["cv"]))
        ldapAttrs.append(("displayName", [fname + ' ' + lname]))
        ldapAttrs.append(("givenName", [fname]))
        ldapAttrs.append(("netID", [str(netID)]))
        ldapAttrs.append(("mail", [str(netID+'@' + self.mailDomain)]))
        ldapAttrs.append(("o", ["Collegium V"]))
        ldapAttrs.append(("uid", [str(username)]))
        ldapAttrs.append(("uidNumber", [str(self.nextUID())]))
        ldapAttrs.append(("userPassword", ["{{SASL}}{0}@COLLEGIUMV.ORG"
                                           .format(username)]))
        ldapAttrs.append(("gidNumber", [str(self.gidNumber)]))
        ldapAttrs.append(("homeDirectory", [str("/home/" + username)]))
        ldapAttrs.append(("loginShell", ["/bin/bash"]))
        ldapAttrs.append(("desktopEnvironment", ["cinnamon"]))

        conn = self.connectLDAP()
        try:
            conn.add_s(userDN, ldapAttrs)
            if self.kadm.addprinc(username, password):
                self.logger.info("Successfully provisioned account %s for %s",
                                 username, netID)
            else:
                self.logger.error("Kerberos Error on account %s", username)

            fileSock = socket.socket()
            try:
                fileSock.connect((self.fileServerAddress, self.fileServerPort))
            except socket.error, e:
                self.logger.error("FileServer socket error: %s", e[1])
            finally:
                fileSock.close()
            success = True
        except ldap.LDAPError as e:
            self.logger.error("An ldap error has occured, %s", e)
        finally:
            conn.unbind()
            self.pc.performUserAndGroupSync()
            return success

    def connectLDAP(self):
        try:
            conn = ldap.initialize(self.config["LDAP"]["ldapAddr"])
            bindDN = self.config["LDAP"]["bindDN"]
            bindPW = self.config["LDAP"]["bindPW"]

            try:
                conn.bind_s(bindDN, bindPW)
            except ldap.INVALID_CREDENTIALS:
                self.logger.severe("Invalid LDAP credentials")
            except ldap.LDAPError as e:
                self.logger.error("LDAP Error: %s", e)
        except:
            self.logger.error("An unidentified error occured in LDAP")
        return conn

    def chPassword(self, username, password):
        return self.kadm.get_princ(username).change_password(password)

    def mkPassword(self):
        self.logger.debug("Made a password")
        password = ""
        for i in range(0, 4):
            password += random.choice(self.words).capitalize()
        return password

    def nextUID(self):
        conn = self.connectLDAP()
        num = self.getLastuidNumber(sock=conn)
        conn.unbind()
        return num+1

    def getLastuidNumber(self, sock=None):
        # this function courtesy of justanull
        lastIndex = 0
        highestUid = 0
        while True:
            searchID = sock.search("ou=people,dc=collegiumv,dc=org",
                                   ldap.SCOPE_SUBTREE,
                                   "(uidNumber>={0})".format(lastIndex),
                                   attrlist=["uidNumber"])
            while True:
                try:
                    tempResults = list()
                    tempResults.append(sock.result(searchID, all=0, timeout=2))

                    if len(tempResults[0][1]) == 0:
                        # oh god why
                        return highestUid

                    if tempResults[-1][1] == list():
                        tempResults = tempResults[:-1]

                    for entry in tempResults:
                        for uidEntry in entry[1][0][1].values():
                            uid = int(uidEntry[0])
                            lastIndex = uid
                            if uid > highestUid:
                                highestUid = uid

                except (ldap.TIMEOUT, ldap.SIZELIMIT_EXCEEDED):
                    break
