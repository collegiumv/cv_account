import logging, random

class Manager:
    def __init__(self, config):
        self.loungeACL = config["ACL"]
        self.words = config["WORDS"]
        self.logger = logging.getLogger("AcctServices")

    def provision(self, netID, username, password):
        self.logger.debug("valid provision call for %s, requesting %s", netID, username)
        return True

    def mkPassword(self):
        password=""
        for i in range(0,4):
            password += random.choice(self.words).capitalize()
        return password
