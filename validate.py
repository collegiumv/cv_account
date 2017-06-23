import logging, re

class Validate:
    def __init__(self, config):
        self.loungeACL = config["ACL"]
        self.blacklist = config["BLACKLIST"]
        self.logger = logging.getLogger("validation")

    def netID(self, netID):
        if netID in self.loungeACL:
            self.logger.debug("Valid netID %s", netID)
            return True
        else:
            self.logger.debug("Invalid netID %s", netID)
            return False

    def user(self, user):
        uValid = re.compile(ur'^[A-Za-z0-9.-_]{1,30}$')
        if re.search(uValid, user):
            self.logger.debug("User %s passed regex check", user)
            if (user.lower() == "root" or user.lower() == "admin"):
                return False
            if (not (all(ord(c) < 128 for c in user))):
                return False
            for word in self.blacklist:
                if (word in user.lower()):
                    self.logger.debug("User %s failed blacklist check", user)
                    return False
            return True
        else:
            self.logger.debug("User %s failed regex check", user)
            return False


