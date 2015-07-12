import logging, subprocess

class KAdmin:
    def __init__(self, kprinc, kpass):
        self.kprinc = kprinc
        self.kpass = kpass
        self.logger = logging.getLogger("pyKAdmin")

    def createPrinc(self, uid, password):
        cmd = ['kadmin','-p'+self.kprinc, '-q', 'addprinc -pw '+password+' '+uid, '-w'+self.kpass]
        if subprocess.call(cmd, shell=False):
            return False
        else:
            return True

    def changePW(self, uid, password):
        cmd = ['kadmin','-p'+self.kprinc, '-q', 'cpw -pw '+password+' '+uid, '-w'+self.kpass]
        if subprocess.call(cmd, shell=False):
            return False
        else:
            return True

if __name__=="__main__":
    o = KAdmin("cv/admin","a")
    o.createPrinc("test2","b")
    o.changePW("test2","c")
