import asyncio
import logging
import random
from typing import Union

from messages.message import Message
from messages.request import Request
from protocol.coap_protocol import CoAPProtocol
from utilities import defines, utils
from utilities.helper import Helper

__author__ = 'Giacomo Tanganelli'

logger = logging.getLogger(__name__)


class CoAPClient(CoAPProtocol):
    def __init__(self, host, port, starting_mid=1, loop=None):
        super().__init__(remote_address=(host, port), starting_mid=starting_mid, loop=loop)
        self._address = (host, port)
        self.queue = asyncio.Queue()
        self.helper = Helper(self.send_request, self.receive_response)

    async def send_request(self, request: Union[Request, Message]):
        if isinstance(request, Request):
            request = await self._observeLayer.send_request(request)
            request = await self._blockLayer.send_request(request)
            transaction = await self._messageLayer.send_request(request)
            if transaction.request.type == defines.Type.CON:
                future_time = random.uniform(defines.ACK_TIMEOUT,
                                             (defines.ACK_TIMEOUT * defines.ACK_RANDOM_FACTOR))
                transaction.retransmit_task = self._loop.create_task(
                    self._retransmit(transaction, transaction.request, future_time, 0))

            await self._send_datagram(transaction.request)
            return transaction
        elif isinstance(request, Message):
            message = await self._observeLayer.send_empty(request)
            message.destination = self._address
            transaction, message = await self._messageLayer.send_empty(message=message)
            await self._send_datagram(message)
            return transaction
        return None

    async def receive_response(self, transaction, timeout: int = 0):
        self._loop.create_task(self.receive_message())
        while transaction.response is None:
            try:
                async with transaction.response_wait:
                    await asyncio.wait_for(transaction.response_wait.wait(), timeout)
            except asyncio.TimeoutError:
                return None

        return transaction.response

    async def get(self, path, callback=None, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a GET on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.GET, path)
        request.token = utils.generate_random_hex(2)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.get(request, callback, timeout)

    async def get_non(self, path, callback=None, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a GET on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.GET, path, defines.Type.NON)
        request.token = utils.generate_random_hex(2)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.get(request, callback, timeout)

    async def discover(self, callback=None, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a GET on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.GET, "/.well-known/core")
        request.token = utils.generate_random_hex(2)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.get(request, callback, timeout)

    async def put(self, path, payload, callback=None, timeout=None, no_response=False, **kwargs):  # pragma: no cover
        """
        Perform a PUT on a certain path.

        :param no_response:
        :param path: the path
        :param payload: the request payload
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.PUT, path)
        request.token = utils.generate_random_hex(2)
        request.payload = payload
        if no_response:
            request.no_response = True

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.put(request, callback, timeout)

    async def put_non(self, path, payload, callback=None, timeout=None, no_response=False, **kwargs):  # pragma: no cover
        """
        Perform a PUT on a certain path.

        :param no_response:
        :param path: the path
        :param payload: the request payload
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.PUT, path, defines.Type.NON)
        request.token = utils.generate_random_hex(2)
        request.payload = payload

        if no_response:
            request.no_response = True

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.put(request, callback, timeout)

    async def post(self, path, payload, callback=None, timeout=None, no_response=False, **kwargs):  # pragma: no cover
        """
        Perform a PUT on a certain path.

        :param no_response:
        :param path: the path
        :param payload: the request payload
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.POST, path)
        request.token = utils.generate_random_hex(2)
        request.payload = payload

        if no_response:
            request.no_response = True

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.post(request, callback, timeout)

    async def post_non(self, path, payload, callback=None, timeout=None, no_response=False, **kwargs):  # pragma: no cover
        """
        Perform a PUT on a certain path.

        :param no_response:
        :param path: the path
        :param payload: the request payload
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.POST, path, defines.Type.NON)
        request.token = utils.generate_random_hex(2)
        request.payload = payload

        if no_response:
            request.no_response = True

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.post(request, callback, timeout)

    async def delete(self, path, callback=None, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a DELETE on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.DELETE, path)
        request.token = utils.generate_random_hex(2)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.delete(request, callback, timeout)

    async def delete_non(self, path, callback=None, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a DELETE on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.DELETE, path, defines.Type.NON)
        request.token = utils.generate_random_hex(2)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.delete(request, callback, timeout)

    async def observe(self, path, callback=None, queue=None, stop=None, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a GET on a certain path.

        :param stop:
        :param queue:
        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.GET, path)
        request.token = utils.generate_random_hex(2)
        request.observe = 0

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.observe(request, callback, queue, stop, timeout)

    async def observe_non(self, path, callback=None, queue=None, stop=None, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a GET on a certain path.

        :param stop:
        :param queue:
        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.helper.mk_request(self._address, defines.Code.GET, path, defines.Type.NON)
        request.token = utils.generate_random_hex(2)
        request.observe = 0

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return await self.helper.observe(request, callback, queue, stop, timeout)
