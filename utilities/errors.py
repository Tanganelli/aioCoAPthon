from utilities import defines


class CoAPException(Exception):
    def __init__(self, msg: str = ""):
        super().__init__(msg)
        self.msg = msg


class MessageFormatError(CoAPException):
    def __init__(self, msg: str, response_code: defines.Code, mid: int):
        super().__init__(msg)
        self.response_code = response_code
        self.mid = mid


class InternalError(CoAPException):
    def __init__(self, msg: str, response_code: defines.Code,
                 transaction: "Transaction", related: defines.MessageRelated, exc: Exception = None):
        super().__init__(msg)
        self.response_code = response_code
        self.msg = msg
        self.exception = exc
        self.transaction = transaction
        self.related = related


class PongException(CoAPException):
    def __init__(self, msg: str = "", message: "Message" = None):
        super().__init__(msg)
        self.message = message


class ObserveError(CoAPException):
    def __init__(self, msg: str = "", response_code: defines.Code = None,
                 transaction: "Transaction" = None):
        super().__init__(msg)
        self.response_code = response_code
        self.msg = msg
        self.transaction = transaction
