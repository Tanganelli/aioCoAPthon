""" CoAP Parameters """
import array
import struct

import enum
from typing import Union

ACK_TIMEOUT = 2  # standard 2

SEPARATE_TIMEOUT = ACK_TIMEOUT / 2

ACK_RANDOM_FACTOR = 1.5

MAX_RETRANSMIT = 4

MAX_TRANSMIT_SPAN = ACK_TIMEOUT * (pow(2, (MAX_RETRANSMIT + 1)) - 1) * ACK_RANDOM_FACTOR

MAX_LATENCY = 120  # 2 minutes

PROCESSING_DELAY = ACK_TIMEOUT

MAX_RTT = (2 * MAX_LATENCY) + PROCESSING_DELAY

EXCHANGE_LIFETIME = MAX_TRANSMIT_SPAN + (2 * MAX_LATENCY) + PROCESSING_DELAY

DISCOVERY_URL = "/.well-known/core"

ALL_COAP_NODES = "224.0.1.187"

ALL_COAP_NODES_IPV6 = "FF00::FD"

MAX_PAYLOAD = 1024

MAX_NON_NOTIFICATIONS = 10

MAX_LOST_NOTIFICATION = 2

BLOCKWISE_SIZE = 1024

VERSION = 1
# One byte which indicates indicates the end of options and the start of the payload.
PAYLOAD_MARKER = 0xFF

TRANSACTION_LIST_MAX_SIZE = 1024

MAX_OBSERVE_COUNT = 200

MINIMUM_OBSERVE_INTERVAL = 30

OBSERVING_JITTER = 5

RECEIVING_BUFFER = 4096


class Origin(enum.IntEnum):
    LOCAL = 0
    REMOTE = 1


class OptionType(enum.IntEnum):
    # The integer.
    INTEGER = 0
    # The string.
    STRING = 1
    # The opaque.
    OPAQUE = 2
    # The unknown.
    UNKNOWN = 3


class OptionRegistry(enum.IntEnum):
    _repeatable: bool
    _default: Union[bytes, str, int]
    _format: OptionType

    RESERVED = 0
    IF_MATCH = 1
    URI_HOST = 3
    ETAG = 4
    IF_NONE_MATCH = 5
    OBSERVE = 6
    URI_PORT = 7
    LOCATION_PATH = 8
    URI_PATH = 11
    CONTENT_TYPE = 12
    MAX_AGE = 14
    URI_QUERY = 15
    ACCEPT = 17
    LOCATION_QUERY = 20
    BLOCK2 = 23
    BLOCK1 = 27
    PROXY_URI = 35
    PROXY_SCHEME = 39
    SIZE1 = 60
    NO_RESPONSE = 258

    @property
    def critical(self) -> bool:  # pragma: no cover
        return self & 0x01 == 0x01

    @property
    def unsafe(self) -> bool:  # pragma: no cover
        return self & 0x02 == 0x02

    @property
    def nocachekey(self) -> bool:  # pragma: no cover
        if self.unsafe:
            raise ValueError("NoCacheKey is only meaningful for safe options")
        return self & 0x1e == 0x1c

    @property
    def number(self) -> int:
        return self.value

    @property
    def format(self) -> OptionType:
        if hasattr(self, "_format"):
            return self._format
        return OptionType.UNKNOWN

    @format.setter
    def format(self, option_type: OptionType):
        self._format = option_type

    @property
    def default(self) -> Union[bytes, str, int]:
        if hasattr(self, "_default"):
            return self._default
        return bytes()

    @default.setter
    def default(self, default: Union[bytes, str, int]):
        if (isinstance(default, int) and self._format == OptionType.INTEGER) \
                or (isinstance(default, str) and self._format == OptionType.STRING) \
                or (isinstance(default, bytes) and self._format == OptionType.OPAQUE):
            self._default = default
        else:  # pragma: no cover
            raise ValueError("Default value not of option type")

    @property
    def repeatable(self) -> bool:
        if hasattr(self, "_repeatable"):
            return self._repeatable
        return False

    @repeatable.setter
    def repeatable(self, r: bool):
        self._repeatable = r

    def __str__(self):  # pragma: no cover
        return "Option {0}".format(self.name)

    def __repr__(self):  # pragma: no cover
        return "Num: {0}, Name: {1}".format(self.value, self.name)

    @staticmethod
    def get_option_flags(option_num):  # pragma: no cover
        """
        Get Critical, UnSafe, NoCacheKey flags from the option number
        as per RFC 7252, section 5.4.6

        :param option_num: option number
        :return: option flags
        :rtype: 3-tuple (critical, unsafe, no-cache)
        """
        opt_bytes = array.array('B', '\0\0')
        if option_num < 256:
            s = struct.Struct("!B")
            s.pack_into(opt_bytes, 0, option_num)
        else:
            s = struct.Struct("H")
            s.pack_into(opt_bytes, 0, option_num)
        critical = (opt_bytes[0] & 0x01) > 0
        unsafe = (opt_bytes[0] & 0x02) > 0
        nocache = ((opt_bytes[0] & 0x1e) == 0x1c)
        return critical, unsafe, nocache


OptionRegistry.RESERVED.format = OptionType.UNKNOWN
OptionRegistry.IF_MATCH.format = OptionType.OPAQUE
OptionRegistry.IF_MATCH.repeatable = True
OptionRegistry.URI_HOST.format = OptionType.STRING
OptionRegistry.URI_HOST.repeatable = True
OptionRegistry.ETAG.format = OptionType.OPAQUE
OptionRegistry.ETAG.repeatable = True
OptionRegistry.IF_NONE_MATCH.format = OptionType.OPAQUE
OptionRegistry.OBSERVE.format = OptionType.INTEGER
OptionRegistry.OBSERVE.default = 0
OptionRegistry.URI_PORT.format = OptionType.INTEGER
OptionRegistry.URI_PORT.default = 5683
OptionRegistry.LOCATION_PATH.format = OptionType.STRING
OptionRegistry.LOCATION_PATH.repeatable = True
OptionRegistry.URI_PATH.format = OptionType.STRING
OptionRegistry.URI_PATH.repeatable = True
OptionRegistry.CONTENT_TYPE.format = OptionType.INTEGER
OptionRegistry.CONTENT_TYPE.default = 0
OptionRegistry.MAX_AGE.format = OptionType.INTEGER
OptionRegistry.MAX_AGE.default = 60
OptionRegistry.URI_QUERY.format = OptionType.STRING
OptionRegistry.URI_QUERY.repeatable = True
OptionRegistry.ACCEPT.format = OptionType.INTEGER
OptionRegistry.ACCEPT.default = 0
OptionRegistry.LOCATION_QUERY.format = OptionType.STRING
OptionRegistry.LOCATION_QUERY.repeatable = True
OptionRegistry.BLOCK2.format = OptionType.INTEGER
OptionRegistry.BLOCK1.format = OptionType.INTEGER
OptionRegistry.PROXY_URI.format = OptionType.STRING
OptionRegistry.PROXY_SCHEME.format = OptionType.STRING
OptionRegistry.SIZE1.format = OptionType.INTEGER
OptionRegistry.NO_RESPONSE.format = OptionType.INTEGER


class Type(enum.IntEnum):
    CON = 0
    NON = 1
    ACK = 2
    RST = 3


class Code(enum.IntEnum):
    EMPTY = 0
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4

    CREATED = 65
    DELETED = 66
    VALID = 67
    CHANGED = 68
    CONTENT = 69
    CONTINUE = 95

    BAD_REQUEST = 128
    FORBIDDEN = 131
    NOT_FOUND = 132
    METHOD_NOT_ALLOWED = 133
    NOT_ACCEPTABLE = 134
    REQUEST_ENTITY_INCOMPLETE = 136
    PRECONDITION_FAILED = 140
    REQUEST_ENTITY_TOO_LARGE = 141
    UNSUPPORTED_CONTENT_FORMAT = 143

    INTERNAL_SERVER_ERROR = 160
    NOT_IMPLEMENTED = 161
    BAD_GATEWAY = 162
    SERVICE_UNAVAILABLE = 163
    GATEWAY_TIMEOUT = 164
    PROXY_NOT_SUPPORTED = 165

    def is_error(self) -> bool:
        return self.value >= 128


class ContentType(enum.IntEnum):
    TEXT_PLAIN = 0
    application_link_format = 40
    application_xml = 41
    application_octet_stream = 42
    application_exi = 47
    application_json = 50
    application_cbor = 60
    application_senml_json = 110
    application_senml_cbor = 112
    application_lwm2m_tlv = 11542
    application_lwm2m_json = 11543


class MessageRelated(enum.IntEnum):
    EMPTY = 0
    REQUEST = 1
    RESPONSE = 2
