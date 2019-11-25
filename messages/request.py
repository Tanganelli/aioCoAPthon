from typing import Optional, List, Union

from ..utilities import errors, defines
from ..messages.message import Message
from ..messages.options import Option

__author__ = 'Giacomo Tanganelli'


class Request(Message):
    """
    Class to handle the Requests.
    """
    def __init__(self):
        """
        Initialize a Request message.

        """
        super(Request, self).__init__()

    @property
    def uri_query(self) -> Optional[str]:
        """
        Get the Uri-Query of a request.

        :return: the Uri-Query
        :rtype : String
        :return: the Uri-Query string
        """
        value = []
        for option in self.options:
            if option.number == defines.OptionRegistry.URI_QUERY.number:
                value.append(option.value)
        if len(value) == 0:
            return None
        return "&".join(value)

    @uri_query.setter
    def uri_query(self, value: str):
        """
        Adds a query.

        :param value: the query
        """
        del self.uri_query
        queries = value.split("&")
        for q in queries:
            option = Option(defines.OptionRegistry.URI_QUERY)
            option.value = q
            self.add_option(option)

    @uri_query.deleter
    def uri_query(self):
        """
        Delete a query.
        """
        self.del_option_by_number(defines.OptionRegistry.URI_QUERY.number)

    @property
    def uri_query_list(self) -> List[str]:
        """
        Get the Uri-Query of a request.

        :return: the Uri-Query
        :rtype : String
        :return: the Uri-Query string
        """
        value = []
        for option in self.options:
            if option.number == defines.OptionRegistry.URI_QUERY.number:
                value.append(option.value)
        return value

    @property
    def uri_path(self) -> Optional[str]:
        """
        Return the Uri-Path of a request

        :rtype : String
        :return: the Uri-Path
        """
        value = []
        for option in self.options:
            if option.number == defines.OptionRegistry.URI_PATH.number:
                value.append(option.value)
        if len(value) == 0:
            return None
        return "/".join(value)

    @uri_path.setter
    def uri_path(self, path: str):
        """
        Set the Uri-Path of a request.

        :param path: the Uri-Path
        """
        del self.uri_path
        path = path.strip("/")
        tmp = path.split("?")
        path = tmp[0]
        paths = path.split("/")
        for p in paths:
            option = Option(defines.OptionRegistry.URI_PATH)
            option.value = p
            self.add_option(option)

    @uri_path.deleter
    def uri_path(self):
        """
        Delete the Uri-Path of a request.
        """
        self.del_option_by_number(defines.OptionRegistry.URI_PATH.number)

    @property
    def uri_path_list(self) -> List[str]:
        """
        Return the Uri-Path of a request

        :rtype : String
        :return: the Uri-Path
        """
        value = []
        for option in self.options:
            if option.number == defines.OptionRegistry.URI_PATH.number:
                value.append(option.value)
        return value

    @property
    def accept(self) -> Optional[int]:
        """
        Get the Accept option of a request.

        :return: the Accept value or None if not specified by the request
        :rtype : String
        """
        for option in self.options:
            if option.number == defines.OptionRegistry.ACCEPT.number:
                return option.value
        return None

    @accept.setter
    def accept(self, value: int):
        """
        Add an Accept option to a request.

        :param value: the Accept value
        """
        del self.accept
        try:
            value = defines.ContentType(value)
            option = Option(defines.OptionRegistry.ACCEPT)
            option.value = value
            self.add_option(option)
        except ValueError:  # pragma: no cover
            raise errors.CoAPException("Unknown Accept value")

    @accept.deleter
    def accept(self):
        """
        Delete the Accept options of a request.
        """
        self.del_option_by_number(defines.OptionRegistry.ACCEPT.number)

    @property
    def if_match(self) -> List[bytes]:
        """
        Get the If-Match option of a request.

        :return: the If-Match values or [] if not specified by the request
        :rtype : list
        """
        value = []
        for option in self.options:
            if option.number == defines.OptionRegistry.IF_MATCH.number:
                value.append(option.value)
        return value

    @if_match.setter
    def if_match(self, values: Union[List[bytes], bytes]):
        """
        Set the If-Match option of a request.

        :param values: the If-Match values
        :type values : list
        """
        del self.if_match
        if isinstance(values, bytes):
            values = [values]
        for v in values:
            option = Option(defines.OptionRegistry.IF_MATCH)
            option.value = v
            self.add_option(option)

    @if_match.deleter
    def if_match(self):
        """
        Delete the If-Match options of a request.
        """
        self.del_option_by_number(defines.OptionRegistry.IF_MATCH.number)

    @property
    def if_none_match(self) -> bool:
        """
        Get the if-none-match option of a request.

        :return: True, if if-none-match is present
        :rtype : bool
        """
        for option in self.options:
            if option.number == defines.OptionRegistry.IF_NONE_MATCH.number:
                return True
        return False

    @if_none_match.setter
    def if_none_match(self, v: bool=True):
        """
        Add the if-none-match option to the request.
        """
        del self.if_none_match
        if v:
            option = Option(defines.OptionRegistry.IF_NONE_MATCH)
            option.value = None
            self.add_option(option)

    @if_none_match.deleter
    def if_none_match(self):
        """
        Delete the if-none-match option in the request.
        """
        self.del_option_by_number(defines.OptionRegistry.IF_NONE_MATCH.number)

    @property
    def no_response(self) -> bool:
        for option in self.options:
            if option.number == defines.OptionRegistry.NO_RESPONSE.number:
                return True
        return False

    @no_response.setter
    def no_response(self, v: bool = True):
        """
        Add the no-response option to the request
        # https://tools.ietf.org/html/rfc7967#section-2.1
        """
        del self.no_response
        if v:
            option = Option(defines.OptionRegistry.NO_RESPONSE)
            option.value = 26
            self.add_option(option)

    @no_response.deleter
    def no_response(self):
        """
        Delete the no_response option in the request.
        """
        self.del_option_by_number(defines.OptionRegistry.NO_RESPONSE.number)

    @property
    def proxy_uri(self) -> Optional[str]:
        """
        Get the Proxy-Uri option of a request.

        :return: the Proxy-Uri values or None if not specified by the request
        :rtype : String
        """
        for option in self.options:
            if option.number == defines.OptionRegistry.PROXY_URI.number:
                return option.value
        return None

    @proxy_uri.setter
    def proxy_uri(self, value: str):
        """
        Set the Proxy-Uri option of a request.

        :param value: the Proxy-Uri value
        """
        del self.proxy_uri
        option = Option(defines.OptionRegistry.PROXY_URI)
        option.value = value
        self.add_option(option)

    @proxy_uri.deleter
    def proxy_uri(self):
        """
        Delete the Proxy-Uri option of a request.
        """
        self.del_option_by_number(defines.OptionRegistry.PROXY_URI.number)

    @property
    def proxy_schema(self) -> Optional[str]:
        """
        Get the Proxy-Schema option of a request.

        :return: the Proxy-Schema values or None if not specified by the request
        :rtype : String
        """
        for option in self.options:
            if option.number == defines.OptionRegistry.PROXY_SCHEME.number:
                return option.value
        return None

    @proxy_schema.setter
    def proxy_schema(self, value: str):
        """
        Set the Proxy-Schema option of a request.

        :param value: the Proxy-Schema value
        """
        del self.proxy_schema
        option = Option(defines.OptionRegistry.PROXY_SCHEME)
        option.value = value
        self.add_option(option)

    @proxy_schema.deleter
    def proxy_schema(self):
        """
        Delete the Proxy-Schema option of a request.
        """
        self.del_option_by_number(defines.OptionRegistry.PROXY_SCHEME.number)
