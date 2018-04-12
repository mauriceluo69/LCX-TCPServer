import hashlib
import string


chapSalt = 1
chapHash = 2
chapResult = 3
bindRequest = 4
bindResponse = 5
connectRequest = 6
connectResponse = 7
dta = 8
discon = 9

gap = '$$$$$'
BUF_SIZE = 1024
noSuchUserErrorMsg = '# Error: No such user!\n# Connection refuse!\n'
hashFailedErrorMsg = '# Error: Hash Configuration failed!\n# Connection refuse!\n'
hashSuccessMsg = '# IMPORTANT # Hash Configuration passed!\n# Connection established!\n'
TIMES = 5


def resolve(msg):
    return msg.split(gap)


def genearteMD5(str):
    hl = hashlib.md5()
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()


class message:
    def __init__(self, length, cmd):
        self.messageLen = length
        self.command = cmd


class chap_salt(message):
    def __init__(self, saltlen, _salt):
        self.command = chapSalt
        self.saltLength = saltlen
        self.salt = _salt

    def tostring(self):
        return str(self.command) + gap + str(self.salt)


class chap_hash(message):
    def __init__(self, usrlen, usr, hashlen, _hash):
        self.command = chapHash
        self.usernameLength = usrlen
        self.userName = usr
        self.hashLength = hashlen
        self.hash = _hash

    def tostring(self):
        return str(self.command) + gap + str(self.userName) + gap + str(self.hash)


class chap_result(message):
    def __init__(self, _result):
        self.command = chapResult
        self.result = _result

    def tostring(self):
        return str(self.command) + gap + str(self.result)


class bind_request(message):
    def __init__(self, rID, lisPort):
        self.command = bindRequest
        self.requestID = rID
        self.listenPort = lisPort

    def tostring(self):
        return str(self.command) + gap + str(self.requestID) + gap + str(self.listenPort)


class bind_response(message):
    def __init__(self, rID, res, lisPort):
        self.command = bindResponse
        self.requestID = rID
        self.result = res
        self.listenPort = lisPort
    
    def tostring(self):
        return str(self.command) + gap + str(self.requestID) + gap + str(self.result) + gap + str(self.listenPort)


class connect_request(message):
    def __init__(self, rID, lisPort):
        self.command = connectRequest
        self.requestID = rID
        self.listenPort = lisPort

    def tostring(self):
        return str(self.command) + gap + str(self.requestID) + gap + str(self.listenPort)


class connect_response(message):
    def __init__(self, rID, res, conID):
        self.command = connect_response
        self.requestID = rID
        self.result = res
        self.connectionID = conID

    def tostring(self):
        return str(self.command) + gap + str(self.requestID) + gap + str(self.result) + gap + str(self.connectionID)


class data(message):
    def __init__(self, conID, dLen, dCon):
        self.command = dta
        self.connectionID = conID
        self.dataLength = dLen
        self.dataContent = dCon
    
    def tostring(self):
        return str(self.command) + gap + str(self.connectionID) + gap + str(self.dataContent)


class disconnect(message):
    def __init__(self, conID):
        self.command = discon
        self.connectionID = conID

    def tostring(self):
        return str(self.command) + gap + str(self.connectionID)
