import asyncio
import functools
import logging
import random
import socket
import struct
from ipaddress import IPv4Address, IPv6Address
from typing import Union

from layers.blocklayer import BlockLayer
from layers.messagelayer import MessageLayer
from layers.observelayer import ObserveLayer
from layers.requestlayer import RequestLayer
from messages.message import Message
from messages.request import Request
from messages.response import Response
from utilities import defines, errors
from utilities.serializer import Serializer
from utilities.transaction import Transaction

logger = logging.getLogger(__name__)


class CoAPProtocol(object):
    def __init__(self, local_address=None, remote_address=None, loop=None, starting_mid=1, enable_multicast=False):
        if isinstance(local_address, tuple) and (isinstance(local_address[0], IPv4Address) or isinstance(local_address[0], IPv6Address)):
            ip, port = local_address
            local_address = (ip.compressed, port)
        if isinstance(remote_address, tuple) and (isinstance(remote_address[0], IPv4Address) or isinstance(remote_address[0], IPv6Address)):
            ip, port = remote_address
            remote_address = (ip.compressed, port)
        self._address = local_address
        self._remote_address = remote_address
        self._loop = loop or asyncio.get_event_loop()
        self._currentMID = starting_mid
        self._multicast = enable_multicast

        self._serializer = Serializer()
        self._messageLayer = MessageLayer(starting_mid)
        self._blockLayer = BlockLayer()
        self._observeLayer = ObserveLayer()
        self._requestLayer = RequestLayer()

        self._socket = None
        self._multicast_socket = None
        self._stop = asyncio.Event()

        if self._address is not None:
            addrinfo = socket.getaddrinfo(self._address[0], None)[0]
            if self._multicast:
                self._create_multicast_socket(addrinfo)
            else:
                self._create_unicast_socket(addrinfo)
        else:
            addrinfo = socket.getaddrinfo(self._remote_address[0], None)[0]
            if addrinfo[0] == socket.AF_INET:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            else:
                self._socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self._socket.setblocking(False)

    def _create_multicast_socket(self, addrinfo):

        if addrinfo[0] == socket.AF_INET:  # IPv4
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.setblocking(False)
            self._socket.bind(('', self._address[1]))
            mreq = struct.pack("4sl", socket.inet_aton(defines.ALL_COAP_NODES), socket.INADDR_ANY)
            try:
                self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            except OSError:
                pass
        else:
            self._multicast_socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

            # Allow multiple copies of this program on one machine
            # (not strictly needed)
            self._multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._multicast_socket.bind((defines.ALL_COAP_NODES_IPV6, self._address[1]))

            addrinfo_multicast = socket.getaddrinfo(defines.ALL_COAP_NODES_IPV6, 5683)[0]
            group_bin = socket.inet_pton(socket.AF_INET6, addrinfo_multicast[4][0])
            mreq = group_bin + struct.pack('@I', 0)
            self._multicast_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
            self._multicast_socket.setblocking(False)

            self._socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.setblocking(False)
            self._socket.bind(self._address)

    def _create_unicast_socket(self, addrinfo):
        if addrinfo[0] == socket.AF_INET:  # IPv4
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.setblocking(False)
        else:
            self._socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.setblocking(False)

        self._socket.bind(self._address)

    def recvfrom(self, fut=None, registed=False):
        fd = self._socket.fileno()
        if fut is None:
            fut = self._loop.create_future()
        if registed:
            try:
                self._loop.remove_reader(fd)
            except ValueError:  # pragma: no cover
                return
        try:
            data, addr = self._socket.recvfrom(defines.RECEIVING_BUFFER)
        except (BlockingIOError, InterruptedError):
            self._loop.add_reader(fd, self.recvfrom, fut, True)
        else:
            fut.set_result((data, addr))
        return fut

    def sendto(self, data, addr, fut=None, registed=False):
        fd = self._socket.fileno()
        if fut is None:
            fut = self._loop.create_future()
        if registed:
            try:
                self._loop.remove_writer(fd)
            except ValueError:  # pragma: no cover
                return
        if not data:
            return
        try:
            n = self._socket.sendto(data, addr)
        except (BlockingIOError, InterruptedError):  # pragma: no cover
            self._loop.add_writer(fd, self.sendto, data, addr, fut, True)
        else:
            fut.set_result(n)
        return fut

    async def receive_message(self):
        data, addr = await self.recvfrom()
        self._loop.create_task(self._handler(data, addr))

    async def _handler(self, data, addr):
        try:
            transaction, msg_type = await self._handle_datagram(data, addr)
            await self.handle_message(transaction, msg_type)
        except errors.PongException as e:
            if e.message is not None:
                # check if it is ping
                if e.message.type == defines.Type.CON:
                    rst = Message()
                    rst.destination = addr
                    rst.type = defines.Type.RST
                    rst.mid = e.message.mid
                    await self._send_datagram(rst)
        except errors.ProtocolError as e:
            '''
               From RFC 7252, Section 4.2
               reject the message if the recipient
               lacks context to process the message properly, including situations
               where the message is Empty, uses a code with a reserved class (1, 6,
               or 7), or has a message format error.  Rejecting a Confirmable
               message is effected by sending a matching Reset message and otherwise
               ignoring it.

               From RFC 7252, Section 4.3
               A recipient MUST reject the message
               if it lacks context to process the message properly, including the
               case where the message is Empty, uses a code with a reserved class
               (1, 6, or 7), or has a message format error.  Rejecting a Non-
               confirmable message MAY involve sending a matching Reset message
            '''
            rst = Message()
            rst.destination = addr
            rst.type = defines.Type.RST
            rst.mid = e.mid
            rst.payload = e.msg
            await self._send_datagram(rst)
        except errors.InternalError as e:
            if e.transaction.separate_task is not None:
                e.transaction.separate_task.cancel()
                del e.transaction.separate_task

            e.transaction.response = Response()
            e.transaction.response.destination = addr
            e.transaction.response.code = e.response_code
            e.transaction.response.payload = e.msg
            transaction = await self._messageLayer.send_response(e.transaction)
            await self._send_datagram(transaction.response)
            logger.error(e.msg)
        except errors.ObserveError as e:
            if e.transaction is not None:
                if e.transaction.separate_task is not None:
                    e.transaction.separate_task.cancel()
                    del e.transaction.separate_task
                e.transaction.response.payload = e.msg
                e.transaction.response.clear_options()
                e.transaction.response.type = defines.Type.CON
                e.transaction.response.code = e.response_code
                e.transaction = await self._messageLayer.send_response(e.transaction)
                await self._send_datagram(e.transaction.response)
                logger.error("Observe Error")
        except errors.CoAPException as e:
            logger.error(e.msg)
        except Exception as e:
            logger.exception(e)

    async def _handle_datagram(self, data, addr):
        message = await self._serializer.deserialize(data, source=addr)
        logger.debug(f"handle_datagram: {message}")
        if isinstance(message, Request):
            if message.type == defines.Type.RST or message.type == defines.Type.ACK:  # pragma: no cover
                raise errors.ProtocolError("Request cannot be carried in RST or ACK messages",
                                           message.mid)
            transaction = await self._messageLayer.receive_request(message)
            return transaction, message
        elif isinstance(message, Response):
            if message.type == defines.Type.RST:  # pragma: no cover
                raise errors.ProtocolError("Responses cannot be carried in RST messages",
                                           message.mid)
            transaction = await self._messageLayer.receive_response(message)
            return transaction, message
        elif isinstance(message, Message):
            if message.type == defines.Type.NON:  # pragma: no cover
                '''
                   From RFC 7252, Section 4.3
                   A Non-confirmable message always carries either a request or response and
                   MUST NOT be Empty.
                '''
                raise errors.ProtocolError("NON messages cannot be EMPTY",
                                           message.mid)
            transaction = await self._messageLayer.receive_empty(message)
            return transaction, message
        else:
            return None

    async def handle_message(self, transaction, message):
        logger.debug(f"handle_message: {message}")
        if isinstance(message, Response):
            if transaction.retransmit_task is not None:
                transaction.retransmit_stop = True
                transaction.retransmit_task.cancel()
            if transaction.response.type == defines.Type.CON:
                transaction.response.acknowledged = True
                transaction, message = await self._messageLayer.send_empty(transaction, defines.MessageRelated.RESPONSE)
                await self._send_datagram(message)
            transaction = await self._blockLayer.receive_response(transaction)
            transaction = await self._observeLayer.receive_response(transaction)

            async with transaction.response_wait:
                transaction.response_wait.notify()

        elif isinstance(message, Request):
            if transaction.request.duplicated:
                logger.warning("Duplicate request")
                if transaction.response.completed is False:
                    transaction.send_separate.set()
                else:
                    if transaction.separate_task is not None:
                        transaction.separate_task.cancel()
                    transaction = await self._messageLayer.send_response(transaction)
                    await self._send_datagram(transaction.response)
                return

            transaction.separate_task = self._loop.create_task(self._send_ack(transaction))
            transaction.automatic_separate_task = self._loop.call_later(defines.SEPARATE_TIMEOUT,
                                                                        functools.partial(self._send_automatic_ack,
                                                                                          transaction))

            transaction = await self._blockLayer.receive_request(transaction)
            if transaction.block_transfer:
                transaction.separate_task.cancel()
                transaction = await self._blockLayer.send_response(transaction)
                transaction = await self._messageLayer.send_response(transaction)
                await self._send_datagram(transaction.response)
                return
            transaction = await self._observeLayer.receive_request(transaction)

            transaction = await self._requestLayer.receive_request(transaction)
            transaction.response.source = self._address

            transaction = await self._observeLayer.send_response(transaction)
            transaction = await self._blockLayer.send_response(transaction)

            transaction.separate_task.cancel()

            transaction = await self._messageLayer.send_response(transaction)

            if transaction.response is not None:
                if transaction.response.type == defines.Type.CON:
                    future_time = random.uniform(defines.ACK_TIMEOUT,
                                                 (defines.ACK_TIMEOUT * defines.ACK_RANDOM_FACTOR))
                    transaction.retransmit_task = self._loop.create_task(
                        self._retransmit(transaction, transaction.response, future_time, 0))

                await self._send_datagram(transaction.response)
            if transaction.resource is not None and transaction.resource.notify_queue is not None \
                    and transaction.resource.changed:
                await transaction.resource.notify_queue.put(transaction.resource)

        elif isinstance(message, Message):
            if transaction is not None:
                if not transaction.request.rejected:
                    # async with transaction.lock:
                    transaction = await self._observeLayer.receive_empty(message, transaction)
                    if transaction.retransmit_task is not None:
                        transaction.retransmit_stop = True
                        transaction.retransmit_task.cancel()
                transaction.response = message
            async with transaction.response_wait:
                transaction.response_wait.notify()
        else:  # pragma: no cover
            raise errors.CoAPException("Unknown Message type")

    @property
    def current_mid(self):
        """
        Return the current MID.

        :return: the current mid
        """
        return self._currentMID

    @current_mid.setter
    def current_mid(self, c):
        """
        Set the current MID.

        :param c: the mid to set
        """
        assert isinstance(c, int)
        self._currentMID = c

    async def _retransmit(self, transaction: Transaction, message: Message,
                          future_time: float, retransmit_count: int):
        try:
            if message.type == defines.Type.CON:
                while retransmit_count < defines.MAX_RETRANSMIT and \
                        (not message.acknowledged and not message.rejected) \
                        and not transaction.retransmit_stop:
                    await asyncio.sleep(future_time)
                    if not message.acknowledged and not message.rejected:
                        retransmit_count += 1
                        future_time *= 2
                        logger.error(f"Retransmit message #{retransmit_count}, next attempt in {future_time}")
                        await self._send_datagram(message)

                if message.acknowledged or message.rejected:
                    message.timeouts = False
                else:
                    logger.error("Give up on message {message}".format(message=message.line_print))
                    message.timeouts = True
                    if message.observe is not None:
                        await self._observeLayer.remove_subscriber(message)
                transaction.retransmit_stop = False
        except asyncio.CancelledError:
            logger.debug("_retransmit cancelled")

    async def _send_datagram(self, message: Union[Request, Response, Message]):
        destination = message.destination
        if isinstance(destination, tuple) and (isinstance(destination[0], IPv4Address) or isinstance(destination[0], IPv6Address)):
            ip, port = destination
            destination = (ip.compressed, port)
        raw_message = await self._serializer.serialize(message, destination=destination)
        self._messageLayer.fetch_mid()
        await self.sendto(raw_message.raw, destination)

    async def _send_ack(self, transaction: Transaction):
        """
        Sends an ACK message for the request.

        :param transaction: the transaction that owns the request
        """
        try:
            await transaction.send_separate.wait()
            if not transaction.request.acknowledged and transaction.request.type == defines.Type.CON:
                logger.debug("send empty ack")
                transaction, ack = await self._messageLayer.send_empty(transaction, defines.MessageRelated.REQUEST)
                await self._send_datagram(ack)
        except asyncio.CancelledError:  # pragma: no cover
            logger.debug("_send_ack cancelled")

    @staticmethod
    def _send_automatic_ack(transaction: Transaction):
        if not transaction.request.acknowledged and transaction.request.type == defines.Type.CON:
            transaction.send_separate.set()

    def stop(self):
        self._stop.set()
        if self._socket is not None:
            self._socket.close()
        if self._multicast_socket is not None:
            self._multicast_socket.close()
