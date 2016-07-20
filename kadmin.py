import logging
import subprocess
import os


class KAdmin:
    def __init__(self, kprinc, ktab):
        self.kprinc = kprinc
        self.ktab = ktab
        self.logger = logging.getLogger("pyKAdmin")

    def createPrinc(self, uid, password):
        FNULL = open(os.devnull, 'w')

        cmd = ['kadmin','-p'+self.kprinc, '-q', 'addprinc -pw '+password+' '+uid, '-k', '-t'+self.ktab]
        if not bool(subprocess.call(cmd, shell=False, stdout=FNULL, stderr=FNULL)):
            self.logger.debug("Kerberos Create Success!")
            return True
        else:
            self.logger.error("Kerberos Create Error")
            return False

    def chPassword(self, uid, password):
        FNULL = open(os.devnull, 'w')

        cmd = ['kadmin','-p'+self.kprinc, '-q', 'cpw -pw '+password+' '+uid, '-k', '-t'+self.ktab]
        if not bool(subprocess.call(cmd, shell=False, stdout=FNULL, stderr=FNULL)):
            self.logger.debug("Kerberos Change Success!")
            return True
        else:
            self.logger.error("Kerberos Change Error")
            return False
