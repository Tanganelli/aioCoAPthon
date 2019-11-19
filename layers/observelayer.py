import time

import cachetools
import logging
from typing import Optional, List, Union

from resources.resource import Resource
from utilities import errors, defines, utils
from utilities.transaction import Transaction

__author__ = 'Giacomo Tanganelli'

logger = logging.getLogger(__name__)


class ObserveItem(object):
    def __init__(self, timestamp: time.time, non_counter: int, allowed: bool,
                 transaction: Optional[Transaction], content_type: Optional[Union[defines.ContentType, int]]):
        """
        Data structure for the Observe option

        :param timestamp: the timestamop of last message sent
        :param non_counter: the number of NON notification sent
        :param allowed: if the client is allowed as observer
        :param transaction: the transaction
        """
        self.timestamp = timestamp
        self.non_counter = non_counter
        self.allowed = allowed
        self.transaction = transaction
        self.content_type = content_type
        self.pmin = None
        self.pmax = None


class ObserveLayer(object):
    """
    Manage the observing feature. It store observing relationships.
    """
    def __init__(self):
        self._relations = cachetools.LFUCache(maxsize=defines.TRANSACTION_LIST_MAX_SIZE)

    async def send_request(self, request):
        """
        Add itself to the observing list

        :param request: the request
        :return: the request unmodified
        """
        if request.observe == 0:
            # Observe request
            try:
                host, port = request.destination
            except AttributeError as e:  # pragma: no cover
                raise errors.InternalError("Request destination cannot be computed",
                                           defines.Code.INTERNAL_SERVER_ERROR, e)

            key_token = utils.str_append_hash(host, port, request.token)

            self._relations[key_token] = ObserveItem(time.time(), 0, True, None, None)

        return request

    async def receive_response(self, transaction):
        """
        Sets notification's parameters.

        :type transaction: Transaction
        :param transaction: the transaction
        :rtype : Transaction
        :return: the modified transaction
        """
        try:
            host, port = transaction.response.source
        except AttributeError as e:  # pragma: no cover
            raise errors.InternalError("Message source cannot be computed",
                                       defines.Code.INTERNAL_SERVER_ERROR, e, transaction=transaction)
        key_token = utils.str_append_hash(host, port, transaction.response.token)

        if key_token in self._relations and transaction.response.type == defines.Type.CON:
            transaction.notification = True
        return transaction

    async def send_empty(self, message):
        """
        Eventually remove from the observer list in case of a RST message.

        :type message: Message
        :param message: the message
        :return: the message unmodified
        """

        try:
            host, port = message.destination
        except AttributeError as e:  # pragma: no cover
            raise errors.InternalError("Message destination cannot be computed",
                                       defines.Code.INTERNAL_SERVER_ERROR, e)
        key_token = utils.str_append_hash(host, port, message.token)
        if key_token in self._relations and message.type == defines.Type.RST:
            del self._relations[key_token]
        return message

    async def receive_request(self, transaction):
        """
        Manage the observe option in the request end eventually initialize the client for adding to
        the list of observers or remove from the list.

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the modified transaction
        """

        if transaction.request.observe == 0 or transaction.request.observe == 1:
            # Observe request
            try:
                host, port = transaction.request.source
            except AttributeError as e:  # pragma: no cover
                raise errors.InternalError("Request Source cannot be computed",
                                           defines.Code.INTERNAL_SERVER_ERROR, e, transaction=transaction)

            key_token = utils.str_append_hash(host, port, transaction.request.token)

            if transaction.request.observe == 0:
                non_counter = 0
                if key_token in self._relations:
                    # Renew registration
                    allowed = True
                else:
                    allowed = False
                self._relations[key_token] = ObserveItem(time.time(), non_counter, allowed, transaction, -1)
            elif transaction.request.observe == 1:
                logger.info("Remove Subscriber")
                try:
                    del self._relations[key_token]
                except KeyError:  # pragma: no cover
                    logger.exception("Subscriber was not registered")

        return transaction

    async def receive_empty(self, empty, transaction):
        """
        Manage the observe feature to remove a client in case of a RST message received in reply to a notification.

        :type empty: Message
        :param empty: the received message
        :type transaction: Transaction
        :param transaction: the transaction that owns the notification message
        :rtype : Transaction
        :return: the modified transaction
        """
        if empty.type == defines.Type.RST:
            try:
                host, port = transaction.request.source
            except AttributeError as e:  # pragma: no cover
                raise errors.InternalError("Request Source cannot be computed",
                                           defines.Code.INTERNAL_SERVER_ERROR, e, transaction=transaction)

            key_token = utils.str_append_hash(host, port, transaction.request.token)
            logger.info("Remove Subscriber")
            try:
                del self._relations[key_token]
            except KeyError:  # pragma: no cover
                logger.exception("Subscriber was not registered")
            transaction.completed = True
        return transaction

    async def send_response(self, transaction):
        """
        Finalize to add the client to the list of observer.

        :type transaction: Transaction
        :param transaction: the transaction that owns the response
        :return: the transaction unmodified
        """
        try:
            host, port = transaction.request.source
        except AttributeError as e:  # pragma: no cover
            raise errors.InternalError("Request source cannot be computed",
                                       defines.Code.INTERNAL_SERVER_ERROR, e, transaction=transaction)

        key_token = utils.str_append_hash(host, port, transaction.request.token)
        if key_token in self._relations:
            if transaction.response.code == defines.Code.CONTENT:
                if transaction.resource is not None and transaction.resource.observable:
                    if transaction.resource.content_type == self._relations[key_token].content_type or \
                                    self._relations[key_token].content_type == -1:
                        transaction.response.observe = transaction.resource.observe_count
                        self._relations[key_token].allowed = True
                        self._relations[key_token].transaction = transaction
                        self._relations[key_token].timestamp = time.time()
                        self._relations[key_token].content_type = transaction.resource.content_type
                        del transaction.request.observe
                        if transaction.response.max_age is not None:
                            self._relations[key_token].pmin = transaction.response.max_age
                    else:
                        del self._relations[key_token]
                        raise errors.ObserveError("Content-Type changed",
                                                  defines.Code.NOT_ACCEPTABLE, transaction=transaction)
                else:
                    del self._relations[key_token]
            elif transaction.response.code.is_error():
                del self._relations[key_token]
        return transaction

    async def notify(self, resource: Resource) -> List[Transaction]:
        """
        Prepare notification for the resource to all interested observers.

        :rtype: list
        :param resource: the resource for which send a new notification
        :return: the list of transactions to be notified
        """
        ret = []
        resource_list = [resource]
        for key in list(self._relations.keys()):
            if self._relations[key].transaction.resource in resource_list:
                if self._relations[key].non_counter > defines.MAX_NON_NOTIFICATIONS \
                        or self._relations[key].transaction.request.type == defines.Type.CON:
                    self._relations[key].transaction.response.type = defines.Type.CON
                    self._relations[key].non_counter = 0
                elif self._relations[key].transaction.request.type == defines.Type.NON:
                    self._relations[key].non_counter += 1
                    self._relations[key].transaction.response.type = defines.Type.NON
                self._relations[key].transaction.resource = resource
                del self._relations[key].transaction.response.mid
                # del self._relations[key].transaction.response.token
                ret.append(self._relations[key].transaction)
        return ret

    async def notify_all(self) -> List[Transaction]:
        """
        Prepare notification for the resource to all interested observers.

        :rtype: list
        :return: the list of transactions to be notified
        """
        ret = []
        for key in list(self._relations.keys()):
            if self._relations[key].non_counter > defines.MAX_NON_NOTIFICATIONS \
                    or self._relations[key].transaction.request.type == defines.Type.CON:
                self._relations[key].transaction.response.type = defines.Type.CON
                self._relations[key].non_counter = 0
            elif self._relations[key].transaction.request.type == defines.Type.NON:
                self._relations[key].non_counter += 1
                self._relations[key].transaction.response.type = defines.Type.NON
            del self._relations[key].transaction.response.mid
            # del self._relations[key].transaction.response.token
            ret.append(self._relations[key].transaction)
        return ret

    async def remove_subscriber(self, message):
        """
        Remove a subscriber based on token.

        :param message: the message
        """
        logger.debug("Remove Subcriber")
        try:
            host, port = message.destination
        except AttributeError as e:  # pragma: no cover
            raise errors.InternalError("Message destination cannot be computed",
                                       defines.Code.INTERNAL_SERVER_ERROR, e)
        key_token = utils.str_append_hash(host, port, message.token)
        try:
            self._relations[key_token].transaction.completed = True
            del self._relations[key_token]
        except KeyError:  # pragma: no cover
            logger.exception("Subscriber was not registered")
