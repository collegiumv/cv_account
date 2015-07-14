import logging, re

class Validate:
    def __init__(self, config):
        self.loungeACL = config["ACL"]
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
            return True
        else:
            self.logger.debug("User %s failed regex check", user)
            return False


