from utilities import defines
from messages.message import Message
from messages.options import Option

__author__ = 'Giacomo Tanganelli'


class Response(Message):
    """
    Class to handle the Responses.
    """

    def __init__(self):
        super().__init__()

    @property
    def location_path(self) -> str:
        """
        Return the Location-Path of the response.

        :rtype : String
        :return: the Location-Path option
        """
        value = []
        for option in self.options:
            if option.number == defines.OptionRegistry.LOCATION_PATH.number:
                value.append(str(option.value))
        return "/".join(value)

    @location_path.setter
    def location_path(self, path: str):
        """
        Set the Location-Path of the response.

        :type path: String
        :param path: the Location-Path as a string
        """
        del self.location_path
        path = path.strip("/")
        tmp = path.split("?")
        path = tmp[0]
        paths = path.split("/")
        for p in paths:
            option = Option(defines.OptionRegistry.LOCATION_PATH)
            option.value = p
            self.add_option(option)

    @location_path.deleter
    def location_path(self):
        """
        Delete the Location-Path of the response.
        """
        self.del_option_by_number(defines.OptionRegistry.LOCATION_PATH.number)

    @property
    def location_query(self) -> str:
        """
        Return the Location-Query of the response.

        :rtype : String
        :return: the Location-Query option
        """
        value = []
        for option in self.options:
            if option.number == defines.OptionRegistry.LOCATION_QUERY.number:
                value.append(option.value)
        return "&".join(value)

    @location_query.setter
    def location_query(self, value: str):
        """
        Set the Location-Query of the response.

        :type value: String
        :param value: the Location-Query as a string
        """
        del self.location_query
        queries = value.split("&")
        for q in queries:
            option = Option(defines.OptionRegistry.LOCATION_QUERY)
            option.value = str(q)
            self.add_option(option)

    @location_query.deleter
    def location_query(self):
        """
        Delete the Location-Query of the response.
        """
        self.del_option_by_number(defines.OptionRegistry.LOCATION_QUERY.number)

    @property
    def max_age(self) -> int:
        """
        Return the MaxAge of the response.

        :rtype : int
        :return: the MaxAge option
        """
        value = defines.OptionRegistry.MAX_AGE.default
        for option in self.options:
            if option.number == defines.OptionRegistry.MAX_AGE.number:
                value = option.value
        return value

    @max_age.setter
    def max_age(self, value: int):
        """
        Set the MaxAge of the response.

        :type value: int
        :param value: the MaxAge option
        """
        del self.max_age
        option = Option(defines.OptionRegistry.MAX_AGE)
        option.value = value
        self.add_option(option)

    @max_age.deleter
    def max_age(self):
        """
        Delete the MaxAge of the response.
        """
        self.del_option_by_number(defines.OptionRegistry.MAX_AGE.number)
