from utilities import defines


class CoAPException(Exception):
    def __init__(self, msg: str = ""):
        super().__init__(msg)
        self.msg = msg


class SerializerException(CoAPException):
    def __init__(self, msg: str = "", response_code: defines.Code = None):
        super().__init__(msg)
        self.response_code = response_code
        self.msg = msg


class MessageValueError(SerializerException):
    def __init__(self, msg: str = "", response_code: defines.Code = None):
        super().__init__(msg, response_code)


class MessageFormatError(SerializerException):
    def __init__(self, msg: str = "", response_code: defines.Code = None, mid: int = None):
        super().__init__(msg, response_code)
        self.mid = mid


class InternalError(CoAPException):
    def __init__(self, msg: str = "", response_code: defines.Code = None, exc: Exception = None,
                 transaction: "Transaction" = None, related: defines.MessageRelated.REQUEST = None):
        super().__init__(msg)
        self.response_code = response_code
        self.msg = msg
        self.exception = exc
        self.transaction = transaction
        self.related = related


class OptionFormatError(InternalError):
    def __init__(self, msg: str = "", response_code: defines.Code = None, exc: Exception = None):
        super().__init__(msg, response_code, exc)


class SilentIgnore(InternalError):
    def __init__(self, msg: str = "", exc: Exception = None, message: "Message" = None):
        super().__init__(msg, exc=exc)
        self.message = message


class ObserveError(CoAPException):
    def __init__(self, msg: str = "", response_code: defines.Code = None,
                 transaction: "Transaction" = None):
        super().__init__(msg)
        self.response_code = response_code
        self.msg = msg
        self.transaction = transaction
