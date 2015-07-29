import logging
import random
import ldap
import kadmin
import socket


class Manager:
    def __init__(self, config):
        self.loungeACL = config["ACL"]
        self.config = config
        self.words = config["WORDS"]
        self.logger = logging.getLogger("AcctServices")
        self.kadmin = kadmin.KAdmin(config["krb5"]["aprinc"], config["krb5"]["apass"])
        self.mailDomain = config["SETTINGS"]["mailDomain"]
        self.gidNumber = config["SETTINGS"]["userGID"]
        self.fileServerAddress = config["SETTINGS"]["fileServerAddress"]
        self.fileServerPort = config["SETTINGS"]["fileServerPort"]

    def uidExists(self, username):
        conn = self.connectLDAP()
        result = conn.search_s("ou=people,dc=collegiumv,dc=org", ldap.SCOPE_SUBTREE, "(uid={0})".format(username), attrlist=["uid"])
        conn.unbind()
        self.logger.debug("Account %s exists? %s", username, bool(len(result)))
        return bool(len(result))

    def netIDExists(self, netID):
        conn = self.connectLDAP()
        result = conn.search_s("ou=people,dc=collegiumv,dc=org", ldap.SCOPE_SUBTREE, "(netID={0})".format(netID), attrlist=["netID"])
        conn.unbind()
        self.logger.debug("Account %s exists? %s", netID, bool(len(result)))
        return bool(len(result))

    def uidFromNetID(self, netID):
        conn = self.connectLDAP()
        result = conn.search_s("ou=people,dc=collegiumv,dc=org", ldap.SCOPE_SUBTREE, "(netID={0})".format(netID), attrlist=["uid"])
        conn.unbind()
        return result[0][1]['uid'][0]
        
    def provision(self, netID, username, password):
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
        ldapAttrs.append(('o', ["Collegium V"]))
        ldapAttrs.append(("uid", [str(username)]))
        ldapAttrs.append(("uidNumber", [str(self.nextUID())]))
        ldapAttrs.append(("gidNumber", [str(self.gidNumber)]))
        ldapAttrs.append(("homeDirectory", [str("/home/" + username)]))
        ldapAttrs.append(("loginShell", ["/bin/bash"]))

        conn = self.connectLDAP()
        try:
            conn.add_s(userDN, ldapAttrs)
            if self.kadmin.createPrinc(username, password):
                self.logger.info("Sucessfully provisioned account %s for %s", username, netID)
            else:
                self.logger.error("Kerberos Error on account %s", username)
                return False
        except ldap.LDAPError as e:
            self.logger.error("An ldap error has occured, %s", e)
            return False
        finally:
            conn.unbind()
            fileSock = socket.socket()
            try:
                fileSock.connect((self.fileServerAddress, self.fileServerPort))
            except socket.error, e:
                self.logger.error("FileServer socket error. WARNING")
            finally:
                fileSock.close()
            return True

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
        return self.kadmin.chPassword(username, password)

    def mkPassword(self):
        self.logger.debug("Made a password")
        password=""
        for i in range(0,4):
            password += random.choice(self.words).capitalize()
        return password

    def nextUID(self):
        conn = self.connectLDAP()
        num = self.getLastuidNumber(sock=conn)
        conn.unbind()
        return num+1

    def getLastuidNumber(self, baseNum=0, sock=None):
        result = list()
        searchID = sock.search("ou=people,dc=collegiumv,dc=org", ldap.SCOPE_SUBTREE, "(uidNumber>={0})".format(baseNum), attrlist=["uidNumber"])
        while True:
            try:
                result.append(sock.result(searchID, all=0, timeout=2))
            except (ldap.TIMEOUT, ldap.SIZELIMIT_EXCEEDED):
                break
                
        # Get the last result, assuming the list is ordered
        if result[-1][1]==list():
            # this handles the timeout condition
            lastResult = result[-2]
        else:
            lastResult = result[-1]
    
        # I sincerely appologize for this index maze, it was necessary
        # to avoid using a large number of temp variables to store
        # data I had no intent of using.  The end output is the last
        # uidNumber to be returned, we assume the result set to be
        # both well defined, and ordered, otherwise this doesn't work
        lastUID = int(lastResult[1][0][1][lastResult[1][0][1].keys()[-1]][0])
            
        if lastUID > baseNum:
            return self.getLastuidNumber(lastUID, sock)
        else:
            return lastUID
