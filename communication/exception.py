class SkError(Exception):
    msg: str = ''
    errno: int = 0

    def __init__(self, errno=0, msg=''):
        super(SkError, self).__init__(msg)
        self.errno = errno
        self.msg = msg


class VarNotFound(SkError):
    errno = 404

    def __init__(self, name):
        SkError.__init__(self, msg=name)


class UnsupportedType(SkError):
    errno = 415
    msg = ''


VAR_CFG_ERROR = 1
UNSUPPORTED_TYPE = 2
READ_ONLY = 3
NETWORK_ERROR = 4
PROTOCOL_ERROR = 5
VAR_NOT_FOUND = 6
