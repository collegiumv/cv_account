import logging, hmac, time, smtplib
from email.mime.text import MIMEText

class Handshake:
    def __init__(self, config):
        self.loungeACL = config["ACL"]
        self.pretzel = config["SETTINGS"]["pretzel"]
        self.serverAddr = config["SETTINGS"]["serverLink"]
        self.replyTo = config["SETTINGS"]["replyTo"]
        self.subject = config["SETTINGS"]["subject"]
        self.smtpServer = config["SETTINGS"]["smptServer"]
        self.mailDomain = config["SETTINGS"]["mailDomain"]
        self.window = config["SETTINGS"]["HMACWindow"]
        self.logger = logging.getLogger("Handshake")

    def send(self, netID, user, create=True):
        link=self.createLink(netID, user, create)
        address = netID + "@" + self.mailDomain
        if create:
            message = "Please use the link below to create your account:\n"+ link
        else:
            message = "Please use the link below to reset your password:\n" + link

        self.sendMail(address, message)

    def createLink(self, netID, user, create):
        validFrom = time.time()
        message = netID+user+str(validFrom)
        userHMAC = hmac.new(str(self.pretzel), message).hexdigest()
        if create:
            url = "http://{0}/ums/provision/{1}/{2}/{3}/{4}/".format(self.serverAddr, netID, user, userHMAC, validFrom)
        else:
            url = "http://{0}/ums/changePassword/{1}/{2}/{3}/{4}/".format(self.serverAddr, netID, user, userHMAC, validFrom)
        self.logger.debug("Composed %s's URL: %s", netID, url)
        return url

    def verify(self, netID, user, userHMAC, linkTime):
        if time.time()-float(linkTime) < self.window:

            validFrom = linkTime
            message = netID+user+str(validFrom)
            validHMAC = unicode(hmac.new(str(self.pretzel), message).hexdigest())
            self.logger.debug("valid: %s", validHMAC)
            self.logger.debug("user: %s", userHMAC)
            # This is a hack until ubuntu updates thier python
            if self.compDigest(userHMAC, validHMAC):
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
        self.logger.debug("message: %s", content)
        s.sendmail(self.replyTo, address, msg.as_string())
        s.quit()

    def sendPassword(self, netID, user, password):
        message = "Your login credentials are below:\n" + "Username: " + user + "\nPassword: " + password + "\n\nNote: Usernames AND passwords are case-sensitive!"
        self.sendMail(netID+"@"+self.mailDomain, message)

    def compDigest(self, a, b):
        same=False
        for i in range(len(b)):
            same |= (a[i] != b[i])
        return not same
