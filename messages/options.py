import struct
from typing import Union

from utilities import utils, errors
from utilities.defines import OptionType, OptionRegistry

__author__ = 'Giacomo Tanganelli'


class Option(object):
    """
    Class to handle the CoAP Options.
    """
    def __init__(self, opt_type: OptionRegistry):
        """
        Data structure to store options.
        """
        self._type = opt_type
        self._raw_value = bytes()

    @property
    def type(self) -> OptionRegistry:
        """
        Return the number of the option.

        :return: the option number
        """
        return self._type

    @type.setter
    def type(self, value: OptionRegistry):
        """
        Set the option number.

        :param value: the option number
        """
        self._type = value

    @property
    def raw_value(self) -> bytes:
        return self._raw_value

    @raw_value.setter
    def raw_value(self, value: bytes):
        self._raw_value = value

    @property
    def value(self) -> Union[int, str, bytes]:
        """
        Return the option value.

        :return: the option value in the correct format depending on the option
        """

        if self._type.format == OptionType.INTEGER:
            if len(self._raw_value) == 0:
                return self._type.default
            else:
                value = 0
                for b in self._raw_value:
                    value = (value << 8) | struct.unpack("B", b.to_bytes(1, "big"))[0]
                return value
        elif self._type.format == OptionType.STRING:
            if len(self._raw_value) == 0:
                return self._type.default
            else:
                return self._raw_value.decode("utf-8")
        else:
            if len(self._raw_value) == 0:
                return self._type.default
            else:
                return self._raw_value

    @value.setter
    def value(self, value: Union[int, str, bytes, None]):
        """
        Set the value of the option.

        :param value: the option value
        """
        if self._type.format == OptionType.INTEGER:
            if isinstance(value, int):
                self._raw_value = value.to_bytes(length=utils.byte_len(value), byteorder="big", signed=False)
            elif isinstance(value, bytes):
                self._raw_value = value
            else:  # pragma: no cover
                raise errors.CoAPException("Invalid value for option. UINT options only accept int and bytes")
        elif self._type.format == OptionType.STRING:
            if isinstance(value, str):
                try:
                    self._raw_value = value.encode("utf-8")
                except UnicodeEncodeError:  # pragma: no cover
                    raise errors.CoAPException("Invalid value for option. Value is not UTF-8")
            elif isinstance(value, bytes):
                self._raw_value = value
            else:  # pragma: no cover
                raise errors.CoAPException("Invalid value for option. STRING options only accept strings and bytes")
        elif self._type.format == OptionType.OPAQUE:
            if value is None:
                value = bytes()
            if isinstance(value, bytes):
                self._raw_value = value
            elif isinstance(value, str):
                try:
                    self._raw_value = value.encode("utf-8")
                except UnicodeEncodeError:  # pragma: no cover
                    raise errors.CoAPException("Invalid value for option. Value is not UTF-8")
            elif isinstance(value, int):
                self._raw_value = value.to_bytes(length=utils.byte_len(value), byteorder="big", signed=False)
        else:  # pragma: no cover
            raise errors.CoAPException("Unknown option format")

    @property
    def length(self) -> int:
        """
        Return the value length

        :rtype : int
        """
        if self._type.format == OptionType.INTEGER:
            return utils.byte_len(self.value)
        elif self._type.format == OptionType.STRING:
            return len(self._raw_value.decode("utf-8"))
        else:
            return len(self._raw_value)

    def is_safe(self) -> bool:  # pragma: no cover
        """
        Check if the option is safe.

        :rtype : bool
        :return: True, if option is safe
        """
        return not self._type.unsafe

    def is_critical(self) -> bool:  # pragma: no cover
        """
        Check if the option is critical.

        :rtype : bool
        :return: True, if option is critical
        """
        return not self._type.critical

    def is_cacheables(self) -> bool:  # pragma: no cover
        """
        Check if the option is cacheables.

        :rtype : bool
        :return: True, if option is cacheables
        """
        return not self._type.nocachekey

    @property
    def name(self) -> str:
        """
        Return option name.

        :rtype : String
        :return: the option name
        """
        return self._type.name

    @property
    def number(self) -> int:
        return self.type.value

    def __str__(self) -> str:
        """
        Return a string representing the option

        :rtype : String
        :return: a message with the option name and the value
        """

        if self._type.format == OptionType.OPAQUE:
            import base64
            value = base64.b64encode(self.value)
        elif self._type == OptionRegistry.BLOCK1 or self._type == OptionRegistry.BLOCK2:
            value = utils.parse_blockwise(self.value)
        else:
            value = self.value
        return "{0}: {1}".format(self.name, value)

    def __eq__(self, other: "Option") -> bool:
        """
        Return True if two option are equal

        :type other: Option
        :param other: the option to be compared against
        :rtype : Boolean
        :return: True, if option are equal
        """
        return self.__dict__ == other.__dict__
