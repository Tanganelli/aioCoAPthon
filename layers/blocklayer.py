import cachetools
import logging

from utilities import errors, defines, utils
from utilities.transaction import Transaction
from messages.request import Request
from messages.response import Response

logger = logging.getLogger(__name__)

__author__ = 'Giacomo Tanganelli'


class BlockItem(object):
    def __init__(self, byte: int, num: int, m: int, size: int, payload: utils.CoAPPayload = None,
                 content_type: defines.ContentType = None):
        """
        Data structure to store Block parameters

        :param byte: the last byte exchanged
        :param num: the num field of the block option
        :param m: the M bit of the block option
        :param size: the size field of the block option
        :param payload: the overall payload received in all blocks
        :param content_type: the content-type of the payload
        """
        self.byte = byte
        self.num = num
        self.m = m
        self.size = size
        self.payload = payload
        self.content_type = content_type


class BlockLayer(object):
    """
    Handle the Blockwise options. Hides all the exchange to both servers and clients.
    """

    def __init__(self):
        self._block1_sent = cachetools.LFUCache(maxsize=defines.TRANSACTION_LIST_MAX_SIZE)
        self._block2_sent = cachetools.LFUCache(maxsize=defines.TRANSACTION_LIST_MAX_SIZE)
        self._block1_receive = cachetools.LFUCache(maxsize=defines.TRANSACTION_LIST_MAX_SIZE)
        self._block2_receive = cachetools.LFUCache(maxsize=defines.TRANSACTION_LIST_MAX_SIZE)

    async def receive_request(self, transaction: Transaction) -> Transaction:
        """
        Handles the Blocks option in a incoming request.

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the edited transaction
        """
        try:
            host, port = transaction.request.source
        except AttributeError:
            raise errors.CoAPException("Request Source cannot be computed")

        key_token = utils.str_append_hash(host, port, transaction.request.token)

        if transaction.request.block2 is not None:

            num, m, size = transaction.request.block2
            if key_token in self._block2_receive:
                self._block2_receive[key_token].num = num
                self._block2_receive[key_token].size = size
                self._block2_receive[key_token].m = m
            else:
                # early negotiation
                byte = size * num
                self._block2_receive[key_token] = BlockItem(byte, num, m, size)

        elif transaction.request.block1 is not None or len(transaction.request.payload) > defines.MAX_PAYLOAD:
            # POST or PUT
            if len(transaction.request.payload) > defines.MAX_PAYLOAD:
                num, m, size = 0, 1, defines.MAX_PAYLOAD
                transaction.request.payload = transaction.request.payload[0:size]
            else:
                num, m, size = transaction.request.block1
            if key_token in self._block1_receive:
                content_type = transaction.request.content_type
                if num != self._block1_receive[key_token].num \
                        or content_type != self._block1_receive[key_token].content_type \
                        or transaction.request.payload is None:
                    # Error Incomplete
                    raise errors.InternalError(msg="Entity incomplete",
                                               response_code=defines.Code.REQUEST_ENTITY_INCOMPLETE,
                                               transaction=transaction, related=defines.MessageRelated.REQUEST)
                self._block1_receive[key_token].payload += transaction.request.payload
            else:
                # first block
                if num != 0:
                    # Error Incomplete
                    raise errors.InternalError(msg="Entity incomplete",
                                               response_code=defines.Code.REQUEST_ENTITY_INCOMPLETE,
                                               transaction=transaction, related=defines.MessageRelated.REQUEST)
                content_type = transaction.request.content_type
                self._block1_receive[key_token] = BlockItem(size, num, m, size, transaction.request.payload,
                                                            content_type)
            num += 1
            byte = size
            self._block1_receive[key_token].byte = byte
            self._block1_receive[key_token].num = num
            self._block1_receive[key_token].size = size
            self._block1_receive[key_token].m = m

            if m == 0:
                transaction.request.payload = self._block1_receive[key_token].payload
                # end of blockwise
                transaction.block_transfer = False
                #
                return transaction
            else:
                # Continue
                transaction.block_transfer = True
                transaction.response = Response()
                transaction.response.destination = transaction.request.source
                transaction.response.token = transaction.request.token

        return transaction

    async def send_response(self, transaction: Transaction) -> Transaction:
        """
        Handles the Blocks option in a outgoing response.

        :type transaction: Transaction
        :param transaction: the transaction that owns the response
        :rtype : Transaction
        :return: the edited transaction
        """
        try:
            host, port = transaction.request.source
        except AttributeError:
            raise errors.CoAPException("Request Source cannot be computed")

        key_token = utils.str_append_hash(host, port, transaction.request.token)

        if (key_token in self._block2_receive and transaction.response.payload is not None) or \
                (transaction.response.payload is not None and len(transaction.response.payload) > defines.MAX_PAYLOAD):
            if key_token in self._block2_receive:

                byte = self._block2_receive[key_token].byte
                size = self._block2_receive[key_token].size
                num = self._block2_receive[key_token].num

            else:
                byte = 0
                num = 0
                size = defines.MAX_PAYLOAD
                m = 1

                self._block2_receive[key_token] = BlockItem(byte, num, m, size)

            if num != 0:
                del transaction.response.observe
            m = 0
            if len(transaction.response.payload) > (byte + size):
                m = 1

            transaction.response.payload = transaction.response.payload[byte:byte + size]
            transaction.response.block2 = (num, m, size)

            self._block2_receive[key_token].byte += size
            self._block2_receive[key_token].num += 1
            if m == 0:
                del self._block2_receive[key_token]
        elif key_token in self._block1_receive:
            num = self._block1_receive[key_token].num
            size = self._block1_receive[key_token].size
            m = self._block1_receive[key_token].m
            transaction.response.block1 = (num - 1, m, size)
            if m == 1:
                transaction.response.code = defines.Code.CONTINUE
            else:
                del self._block1_receive[key_token]

        return transaction

    async def send_request(self, request: Request):
        """
        Handles the Blocks option in a outgoing request.

        :type request: Request
        :param request: the outgoing request
        :return: the edited request
        """
        if request.block1 or (request.payload is not None and len(request.payload) > defines.MAX_PAYLOAD):
            try:
                host, port = request.destination
            except AttributeError:
                raise errors.CoAPException("Request destination cannot be computed")
            key_token = utils.str_append_hash(host, port, request.token)
            if request.block1:
                num, m, size = request.block1
            else:
                num = 0
                m = 1
                size = defines.MAX_PAYLOAD
                request.block1 = num, m, size
            self._block1_sent[key_token] = BlockItem(size, num, m, size, request.payload, request.content_type)
            request.payload = request.payload[0:size]

        elif request.block2:
            try:
                host, port = request.destination
            except AttributeError:
                raise errors.CoAPException("Request destination cannot be computed")
            key_token = utils.str_append_hash(host, port, request.token)
            num, m, size = request.block2
            item = BlockItem(size, num, m, size)
            self._block2_sent[key_token] = item
            return request
        return request

    async def receive_response(self, transaction: Transaction):
        """
        Handles the Blocks option in a incoming response.

        :type transaction: Transaction
        :param transaction: the transaction that owns the response
        :rtype : Transaction
        :return: the edited transaction
        """
        try:
            host, port = transaction.response.source
        except AttributeError:
            raise errors.CoAPException("Response source cannot be computed")
        key_token = utils.str_append_hash(host, port, transaction.response.token)

        if key_token in self._block1_sent and transaction.response.block1 is not None:
            item = self._block1_sent[key_token]
            n_num, n_m, n_size = transaction.response.block1
            if n_num != item.num:
                raise errors.InternalError(msg=f"Block num acknowledged error, expected {item.num} received {n_num}",
                                           response_code=defines.Code.REQUEST_ENTITY_INCOMPLETE,
                                           transaction=transaction, related=defines.MessageRelated.RESPONSE)
            if n_size < item.size:
                logger.debug("Scale down size, was " + str(item.size) + " become " + str(n_size))
                item.size = n_size

        elif transaction.response.block2 is not None:
            num, m, size = transaction.response.block2
            if m == 1:
                if key_token in self._block2_sent:
                    item = self._block2_sent[key_token]
                    if num != item.num:
                        raise errors.InternalError(msg="Receive unwanted block",
                                                   response_code=defines.Code.REQUEST_ENTITY_INCOMPLETE,
                                                   transaction=transaction, related=defines.MessageRelated.RESPONSE)

                    if item.content_type is None:
                        item.content_type = transaction.response.content_type
                    if item.content_type != transaction.response.content_type:
                        raise errors.InternalError(msg="Content-type Error",
                                                   response_code=defines.Code.UNSUPPORTED_CONTENT_FORMAT,
                                                   transaction=transaction, related=defines.MessageRelated.RESPONSE)
                    item.byte += size
                    item.num = num + 1
                    item.size = size
                    item.m = m
                    item.payload += transaction.response.payload
                else:
                    item = BlockItem(size, num + 1, m, size, transaction.response.payload,
                                     transaction.response.content_type)
                    self._block2_sent[key_token] = item

            else:
                if key_token in self._block2_sent:
                    if self._block2_sent[key_token].content_type is None:
                        self._block2_sent[key_token].content_type = transaction.response.content_type
                    if self._block2_sent[key_token].content_type != transaction.response.content_type:
                        raise errors.InternalError(msg="Content-type Error",
                                                   response_code=defines.Code.UNSUPPORTED_CONTENT_FORMAT,
                                                   transaction=transaction, related=defines.MessageRelated.RESPONSE)
                    del self._block2_sent[key_token]

        return transaction
