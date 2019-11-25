import ctypes
import enum
import struct

from typing import Tuple, List, Union, Optional

from messages.message import Message
from messages.response import Response
from messages.request import Request
from utilities import errors, defines
from messages.options import Option
from utilities.defines import OptionRegistry

__author__ = 'Giacomo Tanganelli'


class MessageCodeClass(enum.Enum):
    REQUEST = 0
    RESPONSE = 2
    CLIENT_ERROR = 4
    SERVER_ERROR = 5


class Serializer(object):
    """
    Serializer class to serialize and deserialize CoAP message to/from udp streams.
    """

    @classmethod
    def _read_extended_value(cls, value: int, data: bytes) -> Tuple[bytes, int]:
        if 0 <= value < 13:
            return data, value
        elif value == 13:
            if len(data) < 1:  # pragma: no cover
                raise errors.CoAPException("Option ended prematurely")
            return data[1:], data[0] + 13
        elif value == 14:
            if len(data) < 2:  # pragma: no cover
                raise errors.CoAPException("Malformed option")
            return data[2:], int.from_bytes(data[:2], 'big') + 269
        else:  # pragma: no cover
            raise errors.CoAPException("Malformed option")

    @classmethod
    def _deserialize_options(cls, data: bytes) -> Tuple[bytes, List[Option]]:
        ret = []
        option_number = 0
        while data:
            if data[0] == defines.PAYLOAD_MARKER:
                return data, ret
            field = data[0]
            delta = (field & 0xF0) >> 4
            length = (field & 0x0F)
            data = data[1:]
            data, delta = Serializer._read_extended_value(delta, data)
            data, length = Serializer._read_extended_value(length, data)
            option_number += delta
            if len(data) < length:  # pragma: no cover
                raise errors.CoAPException("Option value is not present")
            try:
                option_item = OptionRegistry(option_number)
            except KeyError or ValueError:
                (opt_critical, _, _) = OptionRegistry.get_option_flags(option_number)
                if opt_critical:  # pragma: no cover
                    raise errors.CoAPException("Critical option {0} unknown".format(option_number))
                else:
                    # If the non-critical option is unknown
                    # (vendor-specific, proprietary) - just skip it
                    pass
            else:
                if length == 0:
                    value = bytes()
                else:
                    value = data[:length]

                option = Option(option_item)
                option.raw_value = value

                ret.append(option)
            finally:
                data = data[length:]
        return data, ret

    @classmethod
    async def deserialize(cls, datagram: bytes,
                          source: Optional[Tuple[str, int]]=None,
                          destination: Optional[Tuple[str, int]] = None) -> Union[Message, Request, Response]:
        """
        De-serialize a stream of byte to a message.

        :param destination:
        :param datagram: the incoming udp message
        :param source: the source address and port (ip, port)
        :return: the message
        :rtype: Message
        """

        try:
            (vttkl, code, mid) = struct.unpack('!BBH', datagram[:4])
        except struct.error:  # pragma: no cover
            raise errors.CoAPException("Message too short for CoAP")

        datagram = datagram[4:]
        version = int((vttkl & 0xC0) >> 6)
        message_type = (vttkl & 0x30) >> 4
        tkl = int(vttkl & 0x0F)

        if version != defines.VERSION:  # pragma: no cover
            raise errors.ProtocolError("Unsupported protocol version", mid)

        if 9 <= tkl <= 15:  # pragma: no cover
            raise errors.ProtocolError("Token Length 9-15 are reserved", mid)

        code_class = (code & 0b11100000) >> 5
        code_details = (code & 0b00011111)
        try:
            cl = MessageCodeClass(code_class)
        except ValueError:  # pragma: no cover
            raise errors.ProtocolError("Unknown code class {0}".format(code_class), mid)
        try:
            if cl == MessageCodeClass.RESPONSE or cl == MessageCodeClass.CLIENT_ERROR or \
                    cl == MessageCodeClass.SERVER_ERROR:
                message = Response()
                message.code = code
            elif cl == MessageCodeClass.REQUEST and code_details != 0:
                message = Request()
                message.code = code
            else:  # Empty message
                message = Message()
                message.code = defines.Code.EMPTY
        except ValueError:  # pragma: no cover
            raise errors.ProtocolError("Unknown code {0}".format(code), mid)

        if source is not None:
            message.source = source
        if destination is not None:
            message.destination = destination
        message.version = version
        message.type = message_type
        message.mid = mid

        if tkl > 0:
            message.token = datagram[:tkl]
        else:
            message.token = None
        try:
            datagram, options = cls._deserialize_options(datagram[tkl:])
        except errors.CoAPException as e:
            raise errors.ProtocolError(e.msg, mid)
        message.add_options(options)
        if len(datagram) == 1:  # pragma: no cover
            raise errors.ProtocolError("Payload Marker with no payload", mid)
        elif len(datagram) == 0:
            message.payload = None
        else:
            message.payload = datagram[1:]
        return message

    @classmethod
    def _write_extended_value(cls, value: int) -> Tuple[int, bytes, str]:
        """Used to encode large values of option delta and option length
           into raw binary form.
           In CoAP option delta and length can be represented by a variable
           number of bytes depending on the value."""
        if 0 <= value < 13:
            return value, bytes(), ""
        elif 13 <= value < 269:
            return 13, (value - 13).to_bytes(1, 'big'), "c"
        elif 269 <= value < 65804:
            return 14, (value - 269).to_bytes(2, 'big'), "cc"
        else:  # pragma: no cover
            raise errors.CoAPException("Delta or Length value out of range.")

    @classmethod
    def _serialize_options(cls, options: List[Option]) -> Tuple[List[bytes], str]:
        options = sorted(options, key=lambda o: o.number)
        lastoptionnumber = 0
        fmt = ""
        data = []
        for option in options:

            delta, extended_delta, delta_fmt = cls._write_extended_value(option.number - lastoptionnumber)
            length, extended_length, length_fmt = cls._write_extended_value(option.length)
            fmt += "c"
            data.append(bytes([((delta & 0x0F) << 4) + (length & 0x0F)]))
            if delta_fmt != "":
                fmt += delta_fmt
                data.append(extended_delta)
            if length_fmt != "":
                fmt += length_fmt
                data.append(extended_length)

            if option.length != 0:
                fmt += "{0}s".format(option.length)
                data.append(option.raw_value)

            # update last option number
            lastoptionnumber = option.number
        return data, fmt

    @classmethod
    async def serialize(cls, message: Union[Request, Response, Message], source: Optional[Tuple[str, int]] = None,
                        destination: Optional[Tuple[str, int]] = None) -> ctypes.Array:
        """
        Serialize a message to a udp packet

        :param destination:
        :param source:
        :type message: Message
        :param message: the message to be serialized
        :rtype: stream of byte
        :return: the message serialized
        """
        if message.source is None:
            message.source = source
        if message.destination is None:
            message.destination = destination
        if message.code is None or message.type is None or message.mid is None:  # pragma: no cover
            raise errors.CoAPException("Code, Message Type and Message ID must not be None.")
        fmt = "!BBH"

        if message.token is None:
            tkl = 0
        else:
            tkl = len(message.token)
        tmp = (defines.VERSION << 2)
        tmp |= message.type
        tmp <<= 4
        tmp |= tkl

        data = [tmp, message.code.value, message.mid]

        if tkl > 0:
            fmt += "{0}s".format(tkl)
            data.append(message.token)

        optiondata, option_fmt = cls._serialize_options(message.options)
        data.extend(optiondata)
        fmt += option_fmt
        payload = message.payload.raw

        if payload is not None and len(payload) > 0:
            # if payload is present and of non-zero length, it is prefixed by
            # an one-byte Payload Marker (0xFF) which indicates the end of
            # options and the start of the payload

            fmt += "B"
            data.append(defines.PAYLOAD_MARKER)

            fmt += "{0}s".format(len(payload))
            data.append(payload)

        try:
            s = struct.Struct(fmt)
            datagram = ctypes.create_string_buffer(s.size)
            s.pack_into(datagram, 0, *data)
        except struct.error:  # pragma: no cover
            print("fmt: {0}, {1}".format(fmt, data))
            raise errors.CoAPException("Message cannot be serialized.")
        return datagram
