import random
import asyncio
import logging
import unittest

from aiounittest import async_test

from aiocoapthon.client.coap_client import CoAPClient
from aiocoapthon.messages.message import Message
from aiocoapthon.messages.request import Request
from aiocoapthon.messages.response import Response
from aiocoapthon.server.coap_server import CoAPServer
from aiocoapthon.tests.plugtest_core_resources import *

logger = logging.getLogger(__name__)
# create logger
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class PlugtestCoreClass(unittest.TestCase):  # pragma: no cover
    def setUp(self):
        self.server_address = ("127.0.0.1", 5683)
        self.server_mid = random.randint(1000, 2000)

    async def start_client_server(self):
        server = CoAPServer(self.server_address[0], self.server_address[1], starting_mid=self.server_mid)
        server.add_resource('test/', TestResource())
        server.add_resource('separate/', SeparateResource())
        server.add_resource('seg1/seg2/seg3/', ComposedResource())
        server.add_resource('query/', QueryResource())
        server.add_resource('location-query/', LocationQueryResource())
        server.add_resource('multi-format/', MultiFormatResource())
        server.add_resource('validate/', ValidateResource())
        server.add_resource('storage/', StorageResource())
        server.add_resource('slow/', SlowResource())
        print(server.get_resources())

        loop = asyncio.get_event_loop()
        loop.create_task(server.create_server())
        client = CoAPClient("127.0.0.1", 5683)
        return client, server

    @staticmethod
    def stop_client_server(client, server):
        server.stop()
        client.stop()
        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]

        [task.cancel() for task in tasks]

    def main(self):
        unittest.main()

    @async_test
    async def test_td_coap_core_01(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_01")
        path = "/test"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Test"
        expected.token = req.token
        expected.content_type = defines.ContentType.TEXT_PLAIN

        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_02(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_02")
        path = "/test"
        req = Request()
        req.code = defines.Code.DELETE
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.DELETED
        expected.source = "127.0.0.1", 5683
        expected.token = req.token

        transaction =  await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_03(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_03")
        path = "/test"
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)
        req.payload = "Uploaded"
        req.content_type = defines.ContentType.TEXT_PLAIN

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CHANGED
        expected.token = req.token

        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_04(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_04")
        path = "/test"
        req = Request()
        req.code = defines.Code.POST
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)
        req.payload = "Uploaded"
        req.content_type = defines.ContentType.TEXT_PLAIN

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CHANGED
        expected.token = req.token

        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_05(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_05")
        path = "/test"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.NON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Test"
        expected.token = req.token
        expected.content_type = defines.ContentType.TEXT_PLAIN

        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_06(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_06")
        path = "/test"
        req = Request()
        req.code = defines.Code.DELETE
        req.uri_path = path
        req.type = defines.Type.NON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.DELETED
        expected.token = req.token
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_07(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_07")
        path = "/test"
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.NON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)
        req.payload = "Updated"

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.CHANGED
        expected.token = req.token
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_08(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_08")
        path = "/test"
        req = Request()
        req.code = defines.Code.POST
        req.uri_path = path
        req.type = defines.Type.NON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)
        req.payload = "Updated"

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.CHANGED
        expected.token = req.token
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_09(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_09")
        path = "/separate"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.EMPTY
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        transaction.response = None

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid+1
        expected.code = defines.Code.CONTENT
        expected.token = req.token
        expected.source = "127.0.0.1", 5683
        expected.payload = "Separate"
        expected.content_type = defines.ContentType.TEXT_PLAIN

        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        req = Request()
        req.code = defines.Code.POST
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)
        req.payload = "POST"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.EMPTY
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        transaction.response = None

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 4
        expected.code = defines.Code.CHANGED
        expected.token = req.token
        expected.source = "127.0.0.1", 5683
        expected.payload = "Resource changed through POST"

        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)
        req.payload = "PUT"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.EMPTY
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        transaction.response = None

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 7
        expected.code = defines.Code.CHANGED
        expected.token = req.token
        expected.source = "127.0.0.1", 5683
        expected.payload = "Resource changed through PUT"

        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        req = Request()
        req.code = defines.Code.DELETE
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)
        req.payload = "DELETE"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.EMPTY
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        transaction.response = None

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 10
        expected.code = defines.Code.DELETED
        expected.token = req.token
        expected.source = "127.0.0.1", 5683
        expected.payload = "Resource deleted"

        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_12(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_12")
        path = "/test"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Test"
        expected.content_type = defines.ContentType.TEXT_PLAIN
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_13(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_13")
        path = "/seg1/seg2/seg3/"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Composed"
        expected.content_type = defines.ContentType.TEXT_PLAIN
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_14(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_14")
        path = "/query"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.uri_query = "first=1&second=2"
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Query12"
        expected.content_type = defines.ContentType.TEXT_PLAIN
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_18(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_18")
        path = "/test"
        req = Request()
        req.code = defines.Code.POST
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.uri_query = "test"
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CREATED
        expected.location_path = "/location1/location2/location3"
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_19(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_19")
        path = "/location-query"
        req = Request()
        req.code = defines.Code.POST
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CREATED
        expected.location_path = "/location-query/location-query1"
        expected.location_query = "?first=1&second=2"
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_20(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_20")
        path = "/multi-format"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.accept = defines.ContentType.TEXT_PLAIN
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "1"
        expected.content_type = defines.ContentType.TEXT_PLAIN
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.accept = defines.ContentType.application_xml
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "<value>1</value>"
        expected.content_type = defines.ContentType.application_xml
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.accept = defines.ContentType.application_exi
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.NOT_ACCEPTABLE
        expected.payload = "Request representation is not acceptable."
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_21(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_21")
        path = "/validate"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Validate"
        expected.etag = b'\x01'
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.etag = b'\x01'
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.VALID
        expected.etag = b'\x01'
        expected.source = self.server_address
        expected.payload = None

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.payload = "Validate changed"

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.etag = b'\x01'
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.etag = b'\x02'
        expected.source = self.server_address
        expected.payload = "Validate changed"

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_22(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_22")
        path = "/validate"

        # STEP 2
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Validate"
        expected.etag = b'\x01'
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 5
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.if_match = b'\x01'
        req.type = defines.Type.CON
        req.payload = "Validate changed"
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        # STEP 6
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CHANGED
        expected.source = self.server_address
        expected.payload = None

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 9
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        # STEP 10
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Validate changed"
        expected.etag = b'\x02'
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 13
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.payload = "Step 13"

        # STEP 14
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CHANGED
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 17
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.if_match = b'\x02'
        req.destination = self.server_address
        req.payload = "Step 13"

        # STEP 14
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.PRECONDITION_FAILED
        expected.source = self.server_address
        expected.payload = None

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 17
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.if_match = b'\x02'
        req.destination = self.server_address

        # STEP 14
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.PRECONDITION_FAILED
        expected.source = self.server_address
        expected.payload = None

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 17
        req = Request()
        req.code = defines.Code.POST
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.if_match = b'\x02'
        req.destination = self.server_address
        req.payload = "Step 13"

        # STEP 14
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.PRECONDITION_FAILED
        expected.source = self.server_address
        expected.payload = None

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 17
        req = Request()
        req.code = defines.Code.DELETE
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.if_match = b'\x02'
        req.destination = self.server_address

        # STEP 14
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.PRECONDITION_FAILED
        expected.source = self.server_address
        expected.payload = None

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_23(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_23")
        path = "/storage/create1"

        # STEP 2
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.payload = "New Resource"
        req.if_none_match = True

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CREATED
        expected.payload = None
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 6
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.if_none_match = True
        req.type = defines.Type.CON
        req.payload = "Validate changed"
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address

        # STEP 6
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.PRECONDITION_FAILED
        expected.source = self.server_address
        expected.payload = None

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_31(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_31")
        path = "/storage/create1"

        # STEP 2
        msg = Message()
        msg.code = defines.Code.EMPTY
        msg.type = defines.Type.CON
        msg.mid = random.randint(1, 1000)
        msg.destination = self.server_address

        # STEP 3
        expected = Message()
        expected.type = defines.Type.RST
        expected.mid = msg.mid
        expected.code = defines.Code.EMPTY
        expected.payload = None
        expected.source = self.server_address

        transaction = await client.send_request(msg)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_32(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_32")
        path = "/storage/create1"

        # STEP 2
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.payload = "New Resource"
        req.if_match = "".encode("utf-8")

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.PRECONDITION_FAILED
        expected.source = self.server_address
        expected.payload = None

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 2
        req = Request()
        req.code = defines.Code.POST
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.payload = "New Resource"
        req.if_none_match = True

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.NOT_FOUND
        expected.payload = None
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 2
        req = Request()
        req.code = defines.Code.DELETE
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.payload = "New Resource"
        req.if_none_match = True

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.NOT_FOUND
        expected.payload = None
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        # STEP 2
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.payload = "New Resource"
        req.if_none_match = True

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CREATED
        expected.payload = None
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 2
        req = Request()
        req.code = defines.Code.POST
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.payload = "New Resource"
        req.if_none_match = True

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.PRECONDITION_FAILED
        expected.payload = None
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_33(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_33")
        path = "/validate/create1"

        # STEP 2
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.payload = "New Resource"

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.NOT_FOUND
        expected.payload = None
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 2
        req = Request()
        req.code = defines.Code.POST
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.payload = "New Resource"

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.NOT_FOUND
        expected.payload = None
        expected.source = self.server_address

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_34(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_34")
        path = "/test"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Test"
        expected.token = req.token
        expected.content_type = defines.ContentType.TEXT_PLAIN
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        old_mid = req.mid
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = old_mid
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.RST
        expected.mid = req.mid
        expected.payload = "Tokens does not match"
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_35(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_35")
        path = "/test"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Test"
        expected.token = req.token
        expected.content_type = defines.ContentType.TEXT_PLAIN

        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        transaction = await client.send_request(req)
        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_36(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_36")
        path = "/slow"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.EMPTY
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)


        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 1
        expected.code = defines.Code.CONTENT
        expected.payload = "Long Time"
        expected.token = req.token
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_37(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_37")
        path = "/slow"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        token = req.token
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.EMPTY
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)

        req = Request()
        req.code = defines.Code.GET
        req.uri_path = "/test"
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)
        transaction2 = await client.send_request(req)

        expected2 = Response()
        expected2.type = defines.Type.ACK
        expected2.mid = req.mid
        expected2.code = defines.Code.CONTENT
        expected2.source = "127.0.0.1", 5683
        expected2.payload = "Test"
        expected2.token = req.token
        expected2.content_type = 0

        ret = await client.receive_response(transaction2, 60)
        if ret != expected2:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected2))
            self.assertEqual(ret, expected2)
        else:
            print("Received Test")

        ret = await client.receive_response(transaction, 60)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 2
        expected.code = defines.Code.CONTENT
        expected.payload = "Long Time"
        expected.token = token
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_38(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_38")
        path = "/slow"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        token = req.token
        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.EMPTY
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 60)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 1
        expected.code = defines.Code.CONTENT
        expected.payload = "Long Time"
        expected.token = token
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 60)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)
