import asyncio
import logging
import random
import time
from typing import List

from protocol.coap_protocol import CoAPProtocol
from resources.resource import Resource
from utilities import defines, errors

logger = logging.getLogger(__name__)

__author__ = 'Giacomo Tanganelli'


class CoAPServer(CoAPProtocol):
    def __init__(self, host, port, starting_mid=1, loop=None):
        super().__init__(local_address=(host, port), starting_mid=starting_mid, loop=loop)
        self._address = (host, port)
        self.queue = asyncio.Queue()

        self._notifier = self._loop.create_task(self._notify_all())
        self._notifier_resource = self._loop.create_task(self._notify())
        self.notify_queue = asyncio.Queue()

    async def create_server(self):
        while not self._stop.is_set():
            try:
                await self.receive_message()
            except asyncio.CancelledError:
                return
            except Exception:  # pragma: no cover
                return

    def add_resource(self, path: str, resource: Resource) -> bool:
        """
        Helper function to add resources to the resource directory during server initialization.

        :param path: the path for the new created resource
        :type resource: Resource
        :param resource: the resource to be added
        """
        resource.notify_queue = self.notify_queue
        return self._requestLayer.add_resource(path, resource)

    def remove_resource(self, path: str) -> bool:  # pragma: no cover
        """
        Helper function to remove resources.

        :param path: the path for the unwanted resource
        :rtype : the removed object
        """

        return self._requestLayer.remove_resource(path)

    def get_resources(self, prefix: str = None) -> List[str]:
        return self._requestLayer.get_resources_path(prefix)

    async def _notify(self):
        while not self._stop.is_set():
            try:
                resource = await self.notify_queue.get()
                self.notify_queue.task_done()
                observers = await self._observeLayer.notify(resource)
                for transaction in observers:
                    try:
                        logger.debug("Notify resource {0} to {1}".format(resource, transaction.response.destination))
                        transaction.response = None
                        del transaction.request.block2
                        transaction = await self._blockLayer.receive_request(transaction)
                        transaction = await self._observeLayer.receive_request(transaction)
                        transaction = await self._requestLayer.receive_request(transaction)
                        transaction = await self._observeLayer.send_response(transaction)
                        transaction = await self._blockLayer.send_response(transaction)
                        transaction = await self._messageLayer.send_response(transaction)
                        if transaction.response is not None:
                            if transaction.response.type == defines.Type.CON:
                                future_time = random.uniform(defines.ACK_TIMEOUT,
                                                             (defines.ACK_TIMEOUT * defines.ACK_RANDOM_FACTOR))
                                transaction.retransmit_task = self._loop.create_task(
                                    self._retransmit(transaction, transaction.response, future_time, 0))

                            self._loop.create_task(self._send_datagram(transaction.response))
                    except errors.ObserveError as e:  # pragma: no cover
                        if e.transaction is not None:
                            if e.transaction.separate_task is not None:
                                 e.transaction.separate_task.cancel()
                            e.transaction.response.payload = e.msg
                            e.transaction.response.clear_options()
                            e.transaction.response.type = defines.Type.CON
                            e.transaction.response.code = e.response_code
                            e.transaction = await self._messageLayer.send_response(e.transaction)
                            self._loop.create_task(self._send_datagram(e.transaction.response))
            except asyncio.CancelledError or RuntimeError:
                break
            except Exception as e:  # pragma: no cover
                logger.exception(e)
                break

    async def _notify_all(self):

        while not self._stop.is_set():
            try:
                observers = await self._observeLayer.notify_all()
                min_pmin = defines.MINIMUM_OBSERVE_INTERVAL
                for transaction in observers:
                    try:
                        logger.debug("Notify All")
                        if transaction.response.max_age is not None:
                            max_age = transaction.response.max_age
                        else:
                            max_age = 60
                        notify_in = transaction.response.timestamp + max_age - time.time() - defines.OBSERVING_JITTER
                        if notify_in <= 0:
                            if transaction.response.type == defines.Type.NON or transaction.response.acknowledged:
                                transaction.response = None
                                transaction = await self._blockLayer.receive_request(transaction)
                                transaction = await self._observeLayer.receive_request(transaction)
                                transaction = await self._requestLayer.receive_request(transaction)
                                transaction = await self._observeLayer.send_response(transaction)
                                transaction = await self._blockLayer.send_response(transaction)
                                transaction = await self._messageLayer.send_response(transaction)
                                if transaction.response is not None:
                                    if transaction.response.max_age is not None:
                                        notify_in = transaction.response.max_age
                                    else:
                                        notify_in = 60
                                    transaction.response.acknowledged = False
                                    if transaction.response.type == defines.Type.CON:
                                        future_time = random.uniform(defines.ACK_TIMEOUT,
                                                                     (defines.ACK_TIMEOUT * defines.ACK_RANDOM_FACTOR))
                                        transaction.retransmit_task = self._loop.create_task(
                                            self._retransmit(transaction, transaction.response, future_time, 0))

                                    self._loop.create_task(self._send_datagram(transaction.response))
                            elif not transaction.response.acknowledged:
                                transaction.notification_not_acknowledged += 1
                                logger.debug("Notification for {0} on resource {1} has not been acknowledged".format(
                                    transaction.response.destination, transaction.resource.path))
                                notify_in = max_age
                                if transaction.notification_not_acknowledged > defines.MAX_LOST_NOTIFICATION:
                                    await self._observeLayer.remove_subscriber(transaction.response)

                        if notify_in < min_pmin:
                            min_pmin = notify_in
                    except errors.ObserveError as e:  # pragma: no cover
                        if e.transaction is not None:
                            e.transaction.separate_task.cancel()
                            e.transaction.response.payload = e.msg
                            e.transaction.response.clear_options()
                            e.transaction.response.type = defines.Type.CON
                            e.transaction.response.code = e.response_code
                            e.transaction = await self._messageLayer.send_response(e.transaction)
                            self._loop.create_task(self._send_datagram(e.transaction.response))

                await asyncio.sleep(min_pmin)
            except asyncio.CancelledError or RuntimeError:
                break
            except Exception as e:  # pragma: no cover
                logger.exception(e)
                break
