import base64
import ipaddress
from typing import Optional, Union, List, Tuple

from .options import Option
from utilities import errors, defines, utils

__author__ = 'Giacomo Tanganelli'


class Message(object):
    """
    Class to handle the Messages.
    """

    def __init__(self):
        """
        Data structure that represent a CoAP message
        """
        self._type = None
        self._mid = None
        self._token = None
        self._options = []
        self._payload = utils.CoAPPayload()
        self._destination = None
        self._source = None
        self._code = defines.Code.EMPTY
        self._acknowledged = None
        self._rejected = None
        self._timeouts = None
        self._cancelled = None
        self._duplicated = None
        self._timestamp = None
        self._version = 1

    @property
    def version(self) -> int:
        """
        Return the CoAP version

        :return: the version
        """
        return self._version

    @version.setter
    def version(self, v: int):
        """
        Sets the CoAP version

        :param v: the version
        :raise AttributeError: if value is not 1
        """
        if not isinstance(v, int) or v != 1:  # pragma: no cover
            raise errors.CoAPException("Only CoAP version 1 is supported")
        self._version = v

    @property
    def type(self) -> defines.Type:
        """
        Return the type of the message.

        :return: the type
        """
        return self._type

    @type.setter
    def type(self, value: Union[defines.Type, int]):
        """
        Sets the type of the message.

        :type value: Types
        :param value: the type
        :raise AttributeError: if value is not a valid type
        """
        if isinstance(value, defines.Type):
            self._type = value
        else:
            try:
                self._type = defines.Type(value)
            except ValueError:  # pragma: no cover
                raise errors.CoAPException("Unsupported message type")

    @property
    def mid(self) -> int:
        """
        Return the mid of the message.

        :return: the MID
        """
        return self._mid

    @mid.setter
    def mid(self, value: int):
        """
        Sets the MID of the message.

        :type value: Integer
        :param value: the MID
        :raise AttributeError: if value is not int or cannot be represented on 16 bits.
        """
        if not isinstance(value, int) or value > 65536:  # pragma: no cover
            raise errors.CoAPException("MID must be between 0 and 65536")
        self._mid = value

    @mid.deleter
    def mid(self):
        """
        Unset the MID of the message.
        """
        self._mid = None

    @property
    def token(self) -> bytes:
        """
        Get the Token of the message.

        :return: the Token
        """
        return self._token

    @token.setter
    def token(self, value: Union[bytes, str, None]):
        """
        Set the Token of the message.

        :type value: String
        :param value: the Token
        :raise AttributeError: if value is longer than 256
        """
        if value is None:
            self._token = value
        elif isinstance(value, str) and len(value) < 256:
            self._token = value.encode("utf-8")
        elif isinstance(value, bytes) and len(value) < 256:
            self._token = value
        else:  # pragma: no cover
            raise errors.CoAPException("Invalid token")

    @property
    def options(self) -> List[Option]:
        """
        Return the options of the CoAP message.

        :rtype: list
        :return: the options
        """
        return sorted(self._options, key=lambda o: o.number)

    @options.setter
    def options(self, value: Optional[List[Option]]):
        """
        Set the options of the CoAP message.

        :type value: list
        :param value: list of options
        """
        if value is None:
            value = []
        if isinstance(value, list):
            self._options = value
        else:  # pragma: no cover
            raise errors.CoAPException("Invalid option list")

    @property
    def payload(self) -> utils.CoAPPayload:
        """
        Return the payload.

        :return: the payload
        """
        return self._payload

    @payload.setter
    def payload(self, value: Union[bytes, str, utils.CoAPPayload, None]):
        """
        Sets the payload of the message and eventually the Content-Type

        :param value: the payload
        """
        if value is None:
            self._payload.payload = None
        elif isinstance(value, bytes):
            self._payload.payload = value
        elif isinstance(value, str):
            self._payload.payload = value.encode("utf-8")
        elif isinstance(value, utils.CoAPPayload):
            self._payload.payload = value.payload
        else:  # pragma: no cover
            raise errors.CoAPException("Payload must be bytes, str or None")

    @property
    def destination(self) -> Optional[Tuple[Union[ipaddress.IPv4Address, ipaddress.IPv6Address], int]]:
        """
        Return the destination of the message.

        :rtype: tuple
        :return: (ip, port)
        """
        return self._destination

    @destination.setter
    def destination(self, value: Optional[Tuple[Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address], int]]):
        """
        Set the destination of the message.

        :type value: tuple
        :param value: (ip, port)
        :raise AttributeError: if value is not a ip and a port.
        """
        if not isinstance(value, tuple) or len(value) != 2:  # pragma: no cover
            raise errors.CoAPException("Invalid destination")

        host, port = value
        try:
            host = ipaddress.ip_address(host)
        except ipaddress.AddressValueError:  # pragma: no cover
            raise errors.CoAPException("Invalid destination")
        self._destination = host, port

    @property
    def source(self) -> Optional[Tuple[Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address], int]]:
        """
        Return the source of the message.

        :rtype: tuple
        :return: (ip, port)
        """
        return self._source

    @source.setter
    def source(self, value: Optional[Tuple[Union[str, ipaddress.IPv4Address, ipaddress.IPv6Address], int]]):
        """
        Set the source of the message.

        :type value: tuple
        :param value: (ip, port)
        :raise AttributeError: if value is not a ip and a port.
        """
        if value is None:
            self._source = None
            return
        elif not isinstance(value, tuple) or len(value) != 2:  # pragma: no cover
            raise errors.CoAPException("Invalid source")

        host, port = value
        try:
            host = ipaddress.ip_address(host)
        except ipaddress.AddressValueError:  # pragma: no cover
            raise errors.CoAPException("Invalid source")

        self._source = host, port

    @property
    def code(self) -> defines.Code:
        """
        Return the code of the message.

        :rtype: Codes
        :return: the code
        """
        return self._code

    @code.setter
    def code(self, value: Union[defines.Code, int]):
        """
        Set the code of the message.

        :type value: Codes
        :param value: the code
        :raise AttributeError: if value is not a valid code
        """
        if isinstance(value, defines.Code):
            self._code = value
        elif isinstance(value, int):
            self._code = defines.Code(value)
        else:  # pragma: no cover
            raise ValueError("Invalid code, allowed types are: Code and int")

    @property
    def acknowledged(self) -> bool:
        """
        Checks if is this message has been acknowledged.

        :return: True, if is acknowledged
        """
        return self._acknowledged

    @acknowledged.setter
    def acknowledged(self, value: bool):
        """
        Marks this message as acknowledged.

        :type value: Boolean
        :param value: if acknowledged
        """
        assert (isinstance(value, bool))
        self._acknowledged = value
        if value:
            self._timeouts = False
            self._rejected = False
            self._cancelled = False

    @property
    def rejected(self) -> bool:
        """
        Checks if this message has been rejected.

        :return: True, if is rejected
        """
        return self._rejected

    @rejected.setter
    def rejected(self, value: bool):
        """
        Marks this message as rejected.

        :type value: Boolean
        :param value: if rejected
        """
        assert (isinstance(value, bool))
        self._rejected = value
        if value:
            self._timeouts = False
            self._acknowledged = False
            self._cancelled = True

    @property
    def timeouts(self) -> bool:
        """
        Checks if this message has timeouted. Confirmable messages in particular
        might timeout.

        :return: True, if has timeouted
        """
        return self._timeouts

    @timeouts.setter
    def timeouts(self, value: bool):
        """
        Marks this message as timeouted. Confirmable messages in particular might
        timeout.

        :type value: Boolean
        :param value:
        """
        assert (isinstance(value, bool))
        self._timeouts = value
        if value:
            self._acknowledged = False
            self._rejected = False
            self._cancelled = True

    @property
    def duplicated(self) -> bool:
        """
        Checks if this message is a duplicate.

        :return: True, if is a duplicate
        """
        return self._duplicated

    @duplicated.setter
    def duplicated(self, value: bool):
        """
        Marks this message as a duplicate.

        :type value: Boolean
        :param value: if a duplicate
        """
        assert (isinstance(value, bool))
        self._duplicated = value

    @property
    def timestamp(self) -> float:
        """
        Return the timestamp of the message.
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: float):
        """
        Set the timestamp of the message.

        :type value: timestamp
        :param value: the timestamp
        """
        self._timestamp = value

    def _already_in(self, option: Option) -> bool:
        """
        Check if an option is already in the message.

        :type option: Option
        :param option: the option to be checked
        :return: True if already present, False otherwise
        """
        for opt in self._options:
            if option.number == opt.number:
                return True
        return False

    def add_option(self, option: Option):
        """
        Add an option to the message.

        :type option: Option
        :param option: the option
        :raise TypeError: if the option is not repeatable and such option is already present in the message
        """
        assert isinstance(option, Option)
        if not option.type.repeatable:
            ret = self._already_in(option)
            if ret:  # pragma: no cover
                raise errors.CoAPException("Option {0} is not repeatable".format(option.name))
            else:
                self._options.append(option)
        else:
            self._options.append(option)
        # self._options = sorted(self._options, key=lambda o: o.number)

    def add_options(self, options: List[Option]):
        for o in options:
            self.add_option(o)

    def del_option(self, option: Option):  # pragma: no cover
        """
        Delete an option from the message

        :type option: Option
        :param option: the option
        """
        assert isinstance(option, Option)
        while option in list(self._options):
            self._options.remove(option)

    def del_option_by_name(self, name: str):  # pragma: no cover
        """
        Delete an option from the message by name

        :type name: String
        :param name: option name
        """
        for o in list(self._options):
            assert isinstance(o, Option)
            if o.name == name:
                self._options.remove(o)

    def del_option_by_number(self, number: int):
        """
        Delete an option from the message by number

        :type number: Integer
        :param number: option naumber
        """
        for o in list(self._options):
            assert isinstance(o, Option)
            if o.number == number:
                self._options.remove(o)

    def clear_options(self):
        for o in list(self._options):
            self._options.remove(o)

    @property
    def etag(self) -> List[bytes]:
        """
        Get the ETag option of the message.

        :rtype: list
        :return: the ETag values or [] if not specified by the request
        """
        value = []
        for option in self.options:
            if option.number == defines.OptionRegistry.ETAG.value:
                value.append(option.value)
        return value

    @etag.setter
    def etag(self, etag: List[Union[str, bytes]]):
        """
        Add an ETag option to the message.

        :param etag: the etag
        """
        if not isinstance(etag, list):
            etag = [etag]
        for e in etag:
            option = Option(defines.OptionRegistry.ETAG)
            if isinstance(e, str):
                e = e.encode("utf-8")
            if isinstance(e, bytes):
                option.value = e
            else:  # pragma: no cover
                raise errors.CoAPException("ETAG must be Opaque")
            self.add_option(option)

    @etag.deleter
    def etag(self):
        """
        Delete an ETag from a message.

        """
        self.del_option_by_number(defines.OptionRegistry.ETAG.value)

    @property
    def content_type(self) -> defines.ContentType:
        """
        Get the Content-Type option of a response.

        :return: the Content-Type value or 0 if not specified by the response
        """
        value = defines.ContentType.TEXT_PLAIN
        for option in self.options:
            if option.number == defines.OptionRegistry.CONTENT_TYPE.value:
                try:
                    value = defines.ContentType(option.value)
                except ValueError:  # pragma: no cover
                    raise errors.CoAPException("Unknown Content Type")
        return value

    @content_type.setter
    def content_type(self, content_type: Union[defines.ContentType, int]):
        """
        Set the Content-Type option of a response.

        :type content_type: int
        :param content_type: the Content-Type
        """
        option = Option(defines.OptionRegistry.CONTENT_TYPE)
        if isinstance(content_type, defines.ContentType):
            option.value = content_type.value
        elif isinstance(content_type, int):
            option.value = content_type
        self.add_option(option)

    @content_type.deleter
    def content_type(self):
        """
        Delete the Content-Type option of a response.
        """

        self.del_option_by_number(defines.OptionRegistry.CONTENT_TYPE.value)

    @property
    def observe(self) -> Optional[int]:
        """
        Check if the request is an observing request.

        :return: 0, if the request is an observing request
        """
        for option in self.options:
            if option.number == defines.OptionRegistry.OBSERVE.value:
                if option.value is None:
                    return 0
                return option.value
        return None

    @observe.setter
    def observe(self, ob: int):
        """
        Add the Observe option.

        :param ob: observe count
        """
        option = Option(defines.OptionRegistry.OBSERVE)
        option.value = ob
        self.del_option_by_number(defines.OptionRegistry.OBSERVE.value)
        self.add_option(option)

    @observe.deleter
    def observe(self):
        """
        Delete the Observe option.
        """
        self.del_option_by_number(defines.OptionRegistry.OBSERVE.value)

    @property
    def block1(self) -> Optional[Tuple[int, int, int]]:
        """
        Get the Block1 option.

        :return: the Block1 value
        """
        value = None
        for option in self.options:
            if option.number == defines.OptionRegistry.BLOCK1.value:
                value = utils.parse_blockwise(option.value)
        return value

    @block1.setter
    def block1(self, value: Tuple[int, int, int]):
        """
        Set the Block1 option.

        :param value: the Block1 value
        """
        option = Option(defines.OptionRegistry.BLOCK1)
        num, m, size = value
        if size > 512:
            szx = 6
        elif 256 < size <= 512:
            szx = 5
        elif 128 < size <= 256:
            szx = 4
        elif 64 < size <= 128:
            szx = 3
        elif 32 < size <= 64:
            szx = 2
        elif 16 < size <= 32:
            szx = 1
        else:
            szx = 0

        value = (num << 4)
        value |= (m << 3)
        value |= szx

        option.value = value
        self.add_option(option)

    @block1.deleter
    def block1(self):
        """
        Delete the Block1 option.
        """
        self.del_option_by_number(defines.OptionRegistry.BLOCK1.value)

    @property
    def block2(self) -> Optional[Tuple[int, int, int]]:
        """
        Get the Block2 option.

        :return: the Block2 value
        """
        value = None
        for option in self.options:
            if option.number == defines.OptionRegistry.BLOCK2.value:
                value = utils.parse_blockwise(option.value)
        return value

    @block2.setter
    def block2(self, value: Tuple[int, int, int]):
        """
        Set the Block2 option.

        :param value: the Block2 value
        """
        option = Option(defines.OptionRegistry.BLOCK2)
        num, m, size = value
        if size > 512:
            szx = 6
        elif 256 < size <= 512:
            szx = 5
        elif 128 < size <= 256:
            szx = 4
        elif 64 < size <= 128:
            szx = 3
        elif 32 < size <= 64:
            szx = 2
        elif 16 < size <= 32:
            szx = 1
        else:
            szx = 0

        value = (num << 4)
        value |= (m << 3)
        value |= szx

        option.value = value
        self.add_option(option)

    @block2.deleter
    def block2(self):
        """
        Delete the Block2 option.
        """
        self.del_option_by_number(defines.OptionRegistry.BLOCK2.value)

    @property
    def cache_key(self) -> str:  # pragma: no cover
        value = [self.code.value.to_bytes(1, 'big').decode("utf-8")]
        for option in self.options:
            if option.is_cacheables():
                value.append(option.raw_value.decode("utf-8"))
        return "".join(value)

    @property
    def line_print(self):
        """
        Return the message as a one-line string.

        :return: the string representing the message
        """

        if self._code is None:
            code = defines.Code.EMPTY
        else:
            code = self._code
        if self.token is None:
            token = ""
        else:
            token = base64.b64encode(self._token)
        msg = "From {source}, To {destination}, {type}-{mid}, {code}-{token}, [" \
            .format(source=self._source, destination=self._destination, type=self._type.name, mid=self._mid,
                    code=code.name, token=token)
        for opt in self._options:
            msg += "{0}, ".format(opt)
        msg += "]"
        if self.payload is not None:
            tmp = self.payload[0:20]
            msg += " {payload}...{length} bytes".format(payload=tmp, length=len(self.payload))
        else:
            msg += " No payload"
        return msg

    def __str__(self):
        return self.line_print

    def pretty_print(self):  # pragma: no cover
        """
        Return the message as a formatted string.

        :return: the string representing the message
        """
        msg = "Source: {0}\n".format(self._source)
        msg += "Destination: {0}\n".format(self._destination)
        msg += "Type: {0}\n".format(self._type.name)
        msg += "MID: {0}\n".format(self._mid)
        if self._code is None:
            msg += "Code: {0}\n".format(defines.Code.EMPTY.name)
        else:
            msg += "Code: {0}\n".format(self.code.name)
        if self.token is None:
            msg += "Token: None\n"
        else:
            msg += "Token: {0}\n".format(base64.b64encode(self._token))
        for opt in self._options:
            msg += "{0}\n".format(opt)
        msg += "Payload: " + "\n"
        msg += "{0}\n".format(self.payload)
        return msg

    def __eq__(self, other):
        assert isinstance(other, Message)
        return self.type == other.type and self.mid == other.mid and self.token == other.token \
               and self.payload == other.payload and self.destination == other.destination \
               and self.source == other.source and self.code == other.code and self.version == other.version \
               and self.options == other.options
