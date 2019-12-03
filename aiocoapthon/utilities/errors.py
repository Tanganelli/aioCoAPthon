from aiocoapthon.utilities import defines


class CoAPException(Exception):
    def __init__(self, msg: str = ""):
        super().__init__(msg)
        self.msg = msg


class ProtocolError(CoAPException):
    def __init__(self, msg: str, mid: int):
        super().__init__(msg)
        self.mid = mid


class InternalError(CoAPException):  # pragma: no cover
    def __init__(self, msg: str, response_code: defines.Code,
                 transaction: "Transaction", exc: Exception = None):
        super().__init__(msg)
        self.response_code = response_code
        self.msg = msg
        self.exception = exc
        self.transaction = transaction


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
