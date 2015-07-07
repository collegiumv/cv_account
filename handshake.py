import logging, hmac

class Handshake:
    def __init__(self, loungeACL, pretzel):
        self.loungeACL = loungeACL
        self.pretzel = pretzel

    def send(self, netID, user):
        secretKey = hmac.new(self.pretzel, netID+user).hexdigest()
        logging.debug("Composed secretKey %s for %s", secretKey, netID)
        
