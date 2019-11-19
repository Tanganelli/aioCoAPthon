import asyncio
from typing import Callable

from messages.request import Request
from messages.response import Response
from utilities import defines

__author__ = 'Giacomo Tanganelli'


class Helper(object):
    def __init__(self, sender_function: Callable, receive_function: Callable):
        self.send_request = sender_function
        self.receive_response = receive_function

    def mk_request(self, address, method: defines.Code, path: str, msgtype: defines.Type = defines.Type.CON):
        """
        Create a request.

        :param msgtype:
        :param method: the CoAP method
        :param path: the path of the request
        :return:  the request
        """
        request = Request()
        request.type = msgtype
        request.destination = address
        request.code = method
        request.uri_path = path
        return request

    async def _finalize_block2(self, response, request, timeout):
        payload = response.payload
        while isinstance(response, Response) and response.block2 is not None:
            num, m, size = response.block2
            if m == 1:
                del request.mid
                del request.block2
                request.block2 = (num + 1, 0, size)
                transaction = await self.send_request(request)
                response = await self.receive_response(transaction, timeout)
                if response is None:
                    return response
                payload += response.payload
            else:
                break
        response.payload = payload
        return response

    async def _finalize_block1(self, response, request, payload, timeout):
        start = 0
        while isinstance(response, Response) and response.block1 is not None:
            num, m, size = response.block1
            start += size
            remaining_payload = payload[start:]
            if len(remaining_payload) > size:
                m = 1
            else:
                m = 0
            num += 1
            del request.mid
            del request.block1
            request.block1 = (num, m, size)
            request.payload = remaining_payload[:size]
            transaction = await self.send_request(request)
            response = await self.receive_response(transaction, timeout)

            if m == 0:
                break
        return response

    async def get(self, request, callback, timeout):
        transaction = await self.send_request(request)
        response = await self.receive_response(transaction, timeout)
        if response is not None:
            if response.code == defines.Code.EMPTY and response.type == defines.Type.ACK:
                transaction.response = None
                response = await self.receive_response(transaction, timeout)
            response = await self._finalize_block2(response, request, timeout)
        if callback is None:
            return response
        else:
            callback(response)
        return response

    async def put(self, request, callback, timeout):
        payload = request.payload.raw
        transaction = await self.send_request(request)
        response = await self.receive_response(transaction, timeout)
        if response is not None:
            if response.code == defines.Code.EMPTY and response.type == defines.Type.ACK:
                transaction.response = None
                response = await self.receive_response(transaction, timeout)
            response = await self._finalize_block2(response, request, timeout)
            response = await self._finalize_block1(response, request, payload, timeout)
        if callback is None:
            return response
        else:
            callback(response)
        return response

    async def post(self, request, callback, timeout):
        return await self.put(request, callback, timeout)

    async def delete(self, request, callback, timeout):
        return await self.get(request, callback, timeout)

    async def observe(self, request, callback=None, queue=None, stop=None, timeout=None, **kwargs):  # pragma: no cover
        transaction = await self.send_request(request)
        response = await self.receive_response(transaction, timeout)

        if response is not None:
            if response.code == defines.Code.EMPTY and response.type == defines.Type.ACK:
                transaction.response = None
                response = await self.receive_response(transaction, timeout)
            response = await self._finalize_block2(response, request, timeout)

        if callback is not None:
            register = False
            while callback(response):
                try:
                    if register:
                        transaction = await self.send_request(request)
                        response = await self.receive_response(transaction, timeout)
                        if response is not None:
                            if response.code == defines.Code.EMPTY and response.type == defines.Type.ACK:
                                transaction.response = None
                                response = await self.receive_response(transaction, timeout)
                            response = await self._finalize_block2(response, request, timeout)
                            continue
                    if response.max_age is not None:
                        max_delay = response.max_age
                    else:
                        max_delay = timeout
                    transaction.response = None
                    response = await self.receive_response(transaction, timeout)
                    if response is not None:
                        if response.code == defines.Code.EMPTY and response.type == defines.Type.ACK:
                            transaction.response = None
                            response = await self.receive_response(transaction, timeout)
                        response = await self._finalize_block2(response, request, max_delay)
                        register = False
                except asyncio.TimeoutError:
                    if not register:
                        register = True
                        pass
                    else:
                        break
        elif queue is not None and stop is not None:
            assert isinstance(queue, asyncio.Queue)
            assert isinstance(stop, asyncio.Event)
            await queue.put(response)
            register = False
            while not stop.is_set():
                try:
                    if register:
                        transaction = await self.send_request(request)
                        response = await self.receive_response(transaction, timeout)
                        if response is not None:
                            if response.code == defines.Code.EMPTY and response.type == defines.Type.ACK:
                                transaction.response = None
                                response = await self.receive_response(transaction, timeout)
                            response = await self._finalize_block2(response, request, timeout)
                            register = False
                            continue
                    if response.max_age is not None:
                        max_delay = response.max_age + defines.MAX_LATENCY
                    else:
                        max_delay = timeout
                    transaction.response = None
                    response = await self.receive_response(transaction, max_delay)
                    if response is not None:
                        if response.code == defines.Code.EMPTY and response.type == defines.Type.ACK:
                            transaction.response = None
                            response = await self.receive_response(transaction, timeout)
                        response = await self._finalize_block2(response, request, max_delay)
                        await queue.put(response)
                    register = False
                except asyncio.TimeoutError:
                    if not register:
                        register = True
                        pass
                    else:
                        break
                except RuntimeError:
                    break

        return response
