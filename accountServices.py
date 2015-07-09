import logging, random, ldap

class Manager:
    def __init__(self, config):
        self.loungeACL = config["ACL"]
        self.config = config
        self.words = config["WORDS"]
        self.logger = logging.getLogger("AcctServices")
        self.mailDomain = config["SETTINGS"]["mailDomain"]
        self.gidNumber = config["SETTINGS"]["userGID"]

    def provision(self, netID, username, password):
        fname = self.loungeACL[netID][0]
        lname = self.loungeACL[netID][1]
        ObjectClass = ["inetOrgPerson", "posixAccount", "cvPerson"]
        userDN = "uid="+username+",ou=people,dc=collegiumv,dc=org"

        #create the ldap values
        ldapAttrs = list()
        ldapAttrs.append(("objectClass",ObjectClass))
        ldapAttrs.append(("cn",[fname + ' ' + lname]))
        ldapAttrs.append(("sn",[lname]))
        ldapAttrs.append(("ou",["cv"]))
        ldapAttrs.append(("displayName",[fname + ' ' + lname]))
        ldapAttrs.append(("givenName",[fname]))
        ldapAttrs.append(("netID",[str(netID)]))
        ldapAttrs.append(("mail",[str(netID+'@'+self.mailDomain)]))
        ldapAttrs.append(('o',["collegiumv"]))
        ldapAttrs.append(("uid", [str(username)]))
        ldapAttrs.append(("uidNumber", [str(self.nextUID())]))
        ldapAttrs.append(("gidNumber", [str(self.gidNumber)]))
        ldapAttrs.append(("homeDirectory",[str("/home/" + username)]))
        ldapAttrs.append(("loginShell",["/bin/bash"]))

        conn = self.connectLDAP()
        try:
            conn.add_s(userDN, ldapAttrs)
        except ldap.LDAPError as e:
            self.logger.error("An ldap error has occured, %s", e)
        finally:    
            conn.unbind()
            self.logger.info("Sucessfully provisioned account %s for %s", username, netID)

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

    def mkPassword(self):
        password=""
        for i in range(0,4):
            password += random.choice(self.words).capitalize()
        return password

    def nextUID(self):
        return 50000
