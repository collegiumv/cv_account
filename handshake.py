import logging, hmac, time, smtplib
from email.mime.text import MIMEText

class Handshake:
    def __init__(self, config):
        self.loungeACL = config["ACL"]
        self.pretzel = config["SETTINGS"]["pretzel"]
        self.serverAddr = config["SETTINGS"]["serverAddr"]
        self.replyTo = config["SETTINGS"]["replyTo"]
        self.subject = config["SETTINGS"]["subject"]
        self.smtpServer = config["SETTINGS"]["smptServer"]
        self.mailDomain = config["SETTINGS"]["mailDomain"]
        self.window = config["SETTINGS"]["HMACWindow"]
        self.logger = logging.getLogger("Handshake")

    def send(self, netID, user, create=True):
        link=self.createLink(netID, user)
        address = netID + "@" + self.mailDomain
        if create:
            message = "Please use the link below to create your account:\n"+ link
        else:
            message = "Please use the link below to reset your password:\n" + link

        self.sendMail(address, message)

    def createLink(self, netID, user):
        validFrom = time.time()
        message = netID+user+str(validFrom)
        userHMAC = hmac.new(str(self.pretzel), message).hexdigest()
        url = "http://{0}/ums/provision/{1}/{2}/{3}/{4}/".format(self.serverAddr, netID, user, userHMAC, validFrom)
        self.logger.debug("Composed %s's URL: %s", netID, url)
        return url

    def verify(self, netID, user, userHMAC, linkTime):
        if time.time()-float(linkTime) < self.window:

            validFrom = linkTime
            message = netID+user+str(validFrom)
            validHMAC = unicode(hmac.new(str(self.pretzel), message).hexdigest())
            self.logger.debug("valid: %s", validHMAC)
            self.logger.debug("user: %s", userHMAC)
            if hmac.compare_digest(userHMAC, validHMAC):
                self.logger.debug("HMAC from %s valid", netID)
                return True
            else:
                self.logger.warning("HMAC from %s INVALID", netID)
                return False
        else:
            self.logger.warning("%s used an outdated link", netID)
            return False

    def sendMail(self, address, content):
        msg=MIMEText(content)
        msg['Subject']=self.subject
        msg['From']=self.replyTo
        msg['To']=address

        s = smtplib.SMTP(self.smtpServer)
        s.sendmail(self.replyTo, address, msg.as_string())
        s.quit()

    def sendPassword(self, netID, password):
        message = "Your password has been set to: " + password + "."
        self.sendMail(netID+"@"+self.mailDomain, message)
