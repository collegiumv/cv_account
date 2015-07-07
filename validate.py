import logging, re

class Validate:
    def __init__(self, loungeACL):
        self.loungeACL = loungeACL
    
    def netID(self, netID):
        if netID in self.loungeACL:
            logging.debug("Valid netID %s", netID)
            return True
        else:
            logging.warning("Invalid netID %s", netID)
            return False

    def user(self, user):
        uValid = re.compile(ur'^[A-Za-z0-9.-_]{1,30}$')
        if re.search(uValid, user):
            logging.debug("User %s passed regex check", user)
            # Do the ldap search to make sure they didn't pick a username
            return True
        else:
            logging.debug("User %s failed regex check", user)
            return False


