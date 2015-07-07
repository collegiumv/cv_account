import logging

class Manager:
    def __init__(self, loungeACL):
        self.loungeACL = loungeACL

    def provision(self, netID, username):
        logging.debug("valid provision call for %s, requesting %s", netID, username)
