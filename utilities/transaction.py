import time

import asyncio
from typing import Union

from ..messages.message import Message
from ..messages.request import Request
from ..messages.response import Response
from ..resources.resource import Resource

__author__ = 'Giacomo Tanganelli'


class Transaction(object):
    """
    Transaction object to bind together a request, a response and a resource.
    """

    def __init__(self, request: Union[Request, Message] = None, response: Response = None,
                 resource: Resource = None, timestamp: time.time = None):
        """
        Initialize a Transaction object.

        :param request: the request
        :param response: the response
        :param resource: the resource interested by the transaction
        :param timestamp: the timestamp of the transaction
        """
        self._response = response
        self._request = request
        self._resource = resource
        self._timestamp = timestamp
        self._completed = False
        self._block_transfer = False
        self.notification = False
        self.notification_not_acknowledged = 0

        self._separate_task = None
        self._retransmit_task = None
        self.send_separate = asyncio.Event()
        self._retransmit_stop = False

        self.lock = asyncio.Lock()
        self.response_wait = asyncio.Condition()

        self.cacheHit = False
        self.cached_element = None

    @property
    def retransmit_stop(self) -> bool:
        return self._retransmit_stop

    @retransmit_stop.setter
    def retransmit_stop(self, b: bool):
        self._retransmit_stop = b

    @property
    def retransmit_task(self) -> asyncio.Task:
        return self._retransmit_task

    @retransmit_task.setter
    def retransmit_task(self, coro: asyncio.Task):
        self._retransmit_task = coro

    @retransmit_task.deleter
    def retransmit_task(self):
        self._retransmit_task.cancel()

    @property
    def separate_task(self) -> asyncio.Task:
        return self._separate_task

    @separate_task.setter
    def separate_task(self, coro: asyncio.Task):
        self._separate_task = coro

    @separate_task.deleter
    def separate_task(self):
        self._separate_task.cancel()

    @property
    def response(self) -> Response:
        """
        Return the response.

        :return: the response
        :rtype: Response
        """
        return self._response

    @response.setter
    def response(self, value: Response):
        """
        Set the response.

        :type value: Response
        :param value: the response to be set in the transaction
        """
        self._response = value

    @property
    def request(self) -> Request:
        """
        Return the request.

        :return: the request
        :rtype: Request
        """
        return self._request

    @request.setter
    def request(self, value: Request):
        """
        Set the request.

        :type value: Request
        :param value: the request to be set in the transaction
        """
        self._request = value

    @property
    def resource(self) -> Resource:
        """
        Return the resource.

        :return: the resource
        :rtype: Resource
        """
        return self._resource

    @resource.setter
    def resource(self, value: Resource):
        """
        Set the resource.

        :type value: Resource
        :param value: the resource to be set in the transaction
        """
        self._resource = value

    @property
    def completed(self) -> bool:
        """
        Return the completed attribute.

        :return: True, if transaction is completed
        """
        return self._completed

    @completed.setter
    def completed(self, b: bool):
        """
        Set the completed attribute.

        :param b: the completed value
        :type b: bool
        """
        assert isinstance(b, bool)
        self._completed = b

    @property
    def block_transfer(self) -> bool:
        """
        Return the block_transfer attribute.

        :return: True, if transaction is blockwise
        """
        return self._block_transfer

    @block_transfer.setter
    def block_transfer(self, b: bool):
        """
        Set the block_transfer attribute.

        :param b: the block_transfer value
        :type b: bool
        """
        assert isinstance(b, bool)
        self._block_transfer = b
