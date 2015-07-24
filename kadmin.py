import logging
import subprocess
import os


class KAdmin:
    def __init__(self, kprinc, kpass):
        self.kprinc = kprinc
        self.kpass = kpass
        self.logger = logging.getLogger("pyKAdmin")

    def createPrinc(self, uid, password):
        FNULL = open(os.devnull, 'w')

        cmd = ['kadmin','-p'+self.kprinc, '-q', 'addprinc -pw '+password+' '+uid, '-w'+self.kpass]
        return not bool(subprocess.call(cmd, shell=False, stdout=FNULL, stderr=FNULL))


    def chPassword(self, uid, password):
        FNULL = open(os.devnull, 'w')

        cmd = ['kadmin','-p'+self.kprinc, '-q', 'cpw -pw '+password+' '+uid, '-w'+self.kpass]
        return not bool(subprocess.call(cmd, shell=False, stdout=FNULL, stderr=FNULL))

if __name__ == "__main__":
    o = KAdmin("cv/admin", "a")
    o.createPrinc("test2", "b")
    o.changePW("test2", "c")
