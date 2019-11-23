import time
from typing import Optional, Tuple

import cachetools as cachetools
import logging
import random

from utilities import errors, defines, utils
from utilities.transaction import Transaction
from messages.message import Message
from messages.response import Response
from messages.request import Request

logger = logging.getLogger(__name__)

__author__ = 'Giacomo Tanganelli'


class MessageLayer(object):
    """
    Handles matching between messages (Message ID) and request/response (Token)
    """

    def __init__(self, starting_mid: int = None):
        """
        Set the layer internal structure.

        :param starting_mid: the first mid used to send messages.
        """
        self._transactions = cachetools.TTLCache(maxsize=defines.TRANSACTION_LIST_MAX_SIZE,
                                                 ttl=defines.EXCHANGE_LIFETIME)
        self._transactions_token = cachetools.TTLCache(maxsize=defines.TRANSACTION_LIST_MAX_SIZE,
                                                       ttl=defines.EXCHANGE_LIFETIME)
        if starting_mid is not None:
            self._current_mid = starting_mid
        else:
            self._current_mid = random.randint(1, 65534)

    def fetch_mid(self) -> int:
        """
        Gets the next valid MID.

        :return: the mid to use
        """
        current_mid = self._current_mid
        self._current_mid += 1
        self._current_mid %= 65535
        return current_mid

    async def receive_request(self, request: Request) -> Transaction:
        """
        Handle duplicates and store received messages.

        :type request: Request
        :param request: the incoming request
        :rtype : Transaction
        :return: the edited transaction
        """
        logger.debug("receive_request - {0}".format(request))
        try:
            host, port = request.source
        except TypeError or AttributeError:  # pragma: no cover
            raise errors.CoAPException("Request Source cannot be computed")
        key_mid = utils.str_append_hash(host, port, request.mid)
        key_token = utils.str_append_hash(host, port, request.token)

        transaction = self._transactions.get(key_mid, None)
        if transaction is not None:
            from_token = self._transactions_token.get(key_token, None)
            if from_token is None:
                logger.warning("Duplicated message with different Token")
                raise errors.ProtocolError(msg="Tokens does not match",
                                           mid=transaction.request.mid)
            transaction.request.duplicated = True
        else:
            request.timestamp = time.time()
            transaction = Transaction(request=request, timestamp=request.timestamp)
            self._transactions[key_mid] = transaction
            self._transactions_token[key_token] = transaction
        return transaction

    async def receive_response(self, response: Response):
        """
        Pair responses with requests.

        :type response: Response
        :param response: the received response
        :rtype : Transaction
        :return: the transaction to which the response belongs to
        """
        logger.debug("receive_response - {0}".format(response))
        try:
            host, port = response.source
        except TypeError or AttributeError:  # pragma: no cover
            raise errors.CoAPException("Response Source cannot be computed")

        key_mid = utils.str_append_hash(host, port, response.mid)
        key_mid_multicast = utils.str_append_hash(defines.ALL_COAP_NODES, port, response.mid)
        key_token = utils.str_append_hash(host, port, response.token)
        key_token_multicast = utils.str_append_hash(defines.ALL_COAP_NODES, port, response.token)
        if key_mid in list(self._transactions.keys()):
            transaction = self._transactions[key_mid]
            if response.token != transaction.request.token:
                logger.warning(f"Tokens does not match -  response message {host}:{port}")
                raise errors.CoAPException(msg=f"Tokens does not match -  response message {host}:{port}")
        elif key_token in self._transactions_token:
            transaction = self._transactions_token[key_token]
        elif key_mid_multicast in list(self._transactions.keys()):
            transaction = self._transactions[key_mid_multicast]
        elif key_token_multicast in self._transactions_token:
            transaction = self._transactions_token[key_token_multicast]
            if response.token != transaction.request.token:
                logger.warning(f"Tokens does not match -  response message {host}:{port}")
                raise errors.CoAPException(msg=f"Tokens does not match -  response message {host}:{port}")
        else:
            raise errors.CoAPException("Un-Matched incoming response message " + str(host) + ":" + str(port))

        transaction.request.acknowledged = True
        transaction.response = response
        if response.type != defines.Type.CON:
            transaction.response.acknowledged = True
        transaction.retransmit_stop = True
        if transaction.retransmit_task is not None:
            transaction.retransmit_task.cancel()
        return transaction

    async def receive_empty(self, message: Message) -> Transaction:
        """
        Pair ACKs with requests.

        :type message: Message
        :param message: the received message
        :rtype : Transaction
        :return: the transaction to which the message belongs to
        """
        logger.debug("receive_empty - {0}".format(message))
        try:
            host, port = message.source
        except TypeError or AttributeError:  # pragma: no cover
            raise errors.CoAPException("Request Source cannot be computed")

        key_mid = utils.str_append_hash(host, port, message.mid)
        key_mid_multicast = utils.str_append_hash(defines.ALL_COAP_NODES, port, message.mid)
        key_token = utils.str_append_hash(host, port, message.token)
        key_token_multicast = utils.str_append_hash(defines.ALL_COAP_NODES, port, message.token)
        transaction = self._transactions.get(key_mid, None)
        in_memory = [(transaction, key_mid)]
        transaction = self._transactions_token.get(key_token, None)
        in_memory.append((transaction, key_token))
        transaction = self._transactions.get(key_mid_multicast, None)
        in_memory.append((transaction, key_mid_multicast))
        transaction = self._transactions_token.get(key_token_multicast, None)
        in_memory.append((transaction, key_token_multicast))
        valid = list(filter(lambda x: x[0] is not None, in_memory))
        if len(valid) == 0:  # pragma: no cover
            logger.warning("Un-Matched incoming empty message fom {0}:{1} with MID {2}".format(host, port,
                                                                                               message.mid))
            raise errors.PongException("Un-Matched incoming empty message fom {0}:{1} with MID {2}"
                                       .format(host, port, message.mid), message=message)
        else:
            transaction, key = valid[0]

        if message.type == defines.Type.ACK:
            if not transaction.request.acknowledged:
                transaction.request.acknowledged = True
            elif (transaction.response is not None) and (not transaction.response.acknowledged):
                transaction.response.acknowledged = True
        elif message.type == defines.Type.RST:
            if not transaction.request.acknowledged:
                transaction.request.rejected = True
            elif not transaction.response.acknowledged:
                transaction.response.rejected = True
        elif message.type == defines.Type.CON:  # pragma: no cover
            # implicit ACK (might have been lost)
            logger.debug("Implicit ACK on received CON for waiting transaction")
            transaction.request.acknowledged = True
        else:  # pragma: no cover
            logger.warning("Unhandled message type...")
            raise errors.CoAPException("Unhandled message type...")

        transaction.retransmit_stop = True
        if transaction.retransmit_task is not None:
            transaction.retransmit_task.cancel()

        for t, k in valid:

            if k == key_mid:
                self._transactions[key_mid] = transaction
            elif k == key_token:
                self._transactions_token[key_token] = transaction
            elif k == key_mid_multicast:
                self._transactions[key_mid_multicast] = transaction
            elif k == key_token_multicast:
                self._transactions_token[key_token_multicast] = transaction

        return transaction

    async def send_request(self, request: Request):
        """
        Create the transaction and fill it with the outgoing request.

        :type request: Request
        :param request: the request to send
        :rtype : Transaction
        :return: the created transaction
        """

        try:
            host, port = request.destination
        except TypeError or AttributeError:  # pragma: no cover
            raise errors.CoAPException("Request destination cannot be computed")

        request.timestamp = time.time()
        transaction = Transaction(request=request, timestamp=request.timestamp)
        if transaction.request.type is None:  # pragma: no cover
            raise errors.CoAPException("Request type is not set")

        if transaction.request.mid is None:
            transaction.request.mid = self.fetch_mid()

        key_mid = utils.str_append_hash(host, port, request.mid)
        self._transactions[key_mid] = transaction

        key_token = utils.str_append_hash(host, port, request.token)
        self._transactions_token[key_token] = transaction
        logger.debug("send_request - {0}".format(request))
        return transaction

    async def send_response(self, transaction: Transaction) -> Transaction:
        """
        Set the type, the token and eventually the MID for the outgoing response

        :type transaction: Transaction
        :param transaction: the transaction that owns the response
        :rtype : Transaction
        :return: the edited transaction
        """
        if transaction.response.type is None:
            if transaction.request.type == defines.Type.CON and not transaction.request.acknowledged:
                transaction.response.type = defines.Type.ACK
                transaction.response.mid = transaction.request.mid
                transaction.response.acknowledged = True
                # transaction.completed = True
            elif transaction.request.type == defines.Type.NON:
                transaction.response.type = defines.Type.NON
                transaction.response.acknowledged = True
            else:
                transaction.response.type = defines.Type.CON

        transaction.response.token = transaction.request.token
        transaction.response.timestamp = time.time()

        if transaction.response.mid is None:
            transaction.response.mid = self.fetch_mid()
        try:
            host, port = transaction.response.destination
        except TypeError or AttributeError:  # pragma: no cover
            raise errors.CoAPException("Response destination cannot be computed")

        logger.debug("send_response - {0}".format(transaction.response))

        key_mid = utils.str_append_hash(host, port, transaction.response.mid)
        key_token = utils.str_append_hash(host, port, transaction.response.token)
        self._transactions[key_mid] = transaction
        self._transactions_token[key_token] = transaction
        request_host, request_port = transaction.request.source
        if request_host.is_multicast:
            key_mid_multicast = utils.str_append_hash(request_host, request_port, transaction.response.mid)
            key_token_multicast = utils.str_append_hash(request_host, request_port, transaction.response.token)
            self._transactions[key_mid_multicast] = transaction
            self._transactions_token[key_token_multicast] = transaction

        transaction.request.acknowledged = True
        return transaction

    async def send_empty(self, transaction: Optional[Transaction] = None,
                         related: Optional[defines.MessageRelated] = None,
                         message: Message = None) -> Tuple[Transaction, Message]:
        """
        Manage ACK or RST related to a transaction. Sets if the transaction has been acknowledged or rejected.

        :param message: 
        :param msg_type:
        :param transaction: the transaction
        :param related: if the ACK/RST message is related to the request or the response. Must be equal to
        transaction.request or to transaction.response or None
        """
        if message is None:
            message = Message()
        if related == defines.MessageRelated.REQUEST:
            if transaction.request.type == defines.Type.CON:
                transaction.request.acknowledged = True
                # transaction.completed = True
                message.type = defines.Type.ACK
                message.mid = transaction.request.mid
                message.code = defines.Code.EMPTY
                message.destination = transaction.request.source
            else:  # pragma: no cover
                raise errors.CoAPException("NON messages cannot be replied with ACKs")

            try:
                host, port = transaction.request.source
            except TypeError or AttributeError:  # pragma: no cover
                raise errors.CoAPException("Response destination cannot be computed")
            key_mid = utils.str_append_hash(host, port, transaction.request.mid)
            key_token = utils.str_append_hash(host, port, transaction.request.token)
            self._transactions[key_mid] = transaction
            self._transactions_token[key_token] = transaction

        elif related == defines.MessageRelated.RESPONSE:
            if transaction.response.type == defines.Type.CON:
                transaction.response.acknowledged = True
                # transaction.completed = True
                message.type = defines.Type.ACK
                message.mid = transaction.response.mid
                message.code = defines.Code.EMPTY
                message.destination = transaction.response.source
            else:  # pragma: no cover
                raise errors.CoAPException("NON messages cannot be replied with ACKs")

            try:
                host, port = transaction.response.source
            except TypeError or AttributeError:  # pragma: no cover
                raise errors.CoAPException("Response destination cannot be computed")
            key_mid = utils.str_append_hash(host, port, transaction.response.mid)
            key_token = utils.str_append_hash(host, port, transaction.response.token)
            self._transactions[key_mid] = transaction
            self._transactions_token[key_token] = transaction
            request_host, request_port = transaction.request.destination
            if request_host.is_multicast:
                key_mid_multicast = utils.str_append_hash(request_host, request_port, transaction.response.mid)
                key_token_multicast = utils.str_append_hash(request_host, request_port, transaction.response.token)
                self._transactions[key_mid_multicast] = transaction
                self._transactions_token[key_token_multicast] = transaction
        else:
            # for clients
            try:
                host, port = message.destination
            except TypeError or AttributeError:  # pragma: no cover
                raise errors.CoAPException("Message destination cannot be computed")

            key_mid = utils.str_append_hash(host, port, message.mid)
            key_token = utils.str_append_hash(host, port, message.token)

            message.timestamp = time.time()
            transaction = Transaction(request=message, timestamp=message.timestamp)
            self._transactions[key_mid] = transaction
            self._transactions_token[key_token] = transaction
        logger.debug("send_empty -  {0}".format(message))
        return transaction, message
