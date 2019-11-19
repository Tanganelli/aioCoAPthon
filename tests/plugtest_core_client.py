import random
import asyncio
import logging
import unittest

from aiounittest import async_test

from client.coap_client import CoAPClient
from server.coap_server import CoAPServer
from messages.response import Response
from tests.plugtest_core_resources import *

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


class PlugtestCoreClientClass(unittest.TestCase):
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

        loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.handle_exception)
        loop.create_task(server.create_server())

        client = CoAPClient("127.0.0.1", 5683)

        return client, server

    @staticmethod
    async def stop_client_server(client, server):
        server.stop()
        client.stop()
        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]

        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    def handle_exception(loop, context):
        # context["message"] will always be there; but context["exception"] may not
        msg = context.get("exception", context["message"])
        logging.error(f"Caught exception: {msg}")
        logging.error(repr(context))

    def main(self):
        unittest.main()

    @async_test
    async def test_td_coap_core_01(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_01")
        path = "/test"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CONTENT
        expected.payload = "Test"
        expected.content_type = defines.ContentType.TEXT_PLAIN

        expected.source = "127.0.0.1", 5683

        ret = await client.get(path, timeout=10)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid
        expected.token = ret.token
        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_02(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_02")
        path = "/test"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.DELETED
        expected.source = "127.0.0.1", 5683

        ret = await client.delete(path, timeout=10)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid
        expected.token = ret.token

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_03(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_03")
        path = "/test"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CHANGED

        expected.source = "127.0.0.1", 5683

        ret = await client.put(path, "Uploaded", timeout=10)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid
        expected.token = ret.token

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_04(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_04")
        path = "/test"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CHANGED

        expected.source = "127.0.0.1", 5683

        ret = await client.post(path, "Uploaded", timeout=10)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid
        expected.token = ret.token

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_05(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_05")
        path = "/test"

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Test"
        expected.content_type = defines.ContentType.TEXT_PLAIN

        expected.source = "127.0.0.1", 5683

        ret = await client.get_non(path, timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_06(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_06")
        path = "/test"

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.DELETED
        expected.source = "127.0.0.1", 5683

        ret = await client.delete_non(path, timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_07(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_07")
        path = "/test"

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.CHANGED
        expected.source = "127.0.0.1", 5683

        ret = await client.put_non(path, "Updated", timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_08(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_08")
        path = "/test"

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.CHANGED
        expected.source = "127.0.0.1", 5683

        ret = await client.post_non(path, "Updated", timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_09(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_09")
        path = "/separate"

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid+1
        expected.code = defines.Code.CONTENT
        expected.source = "127.0.0.1", 5683
        expected.payload = "Separate"
        expected.content_type = defines.ContentType.TEXT_PLAIN

        ret = await client.get(path, timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_13(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_13")
        path = "/seg1/seg2/seg3/"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CONTENT
        expected.payload = "Composed"
        expected.content_type = defines.ContentType.TEXT_PLAIN
        expected.source = self.server_address

        ret = await client.get(path, timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_14(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_14")
        path = "/query"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CONTENT
        expected.payload = "Query12"
        expected.content_type = defines.ContentType.TEXT_PLAIN
        expected.source = self.server_address

        ret = await client.get(path, timeout=10, uri_query="first=1&second=2")
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_18(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_18")
        path = "/test"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.location_path = "/location1/location2/location3"
        expected.source = self.server_address

        ret = await client.post(path, None, timeout=10, uri_query="test")
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_19(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_19")
        path = "/location-query"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.location_path = "/location-query/location-query1"
        expected.location_query = "?first=1&second=2"
        expected.source = self.server_address

        ret = await client.post(path, None, timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_20(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_20")
        path = "/multi-format"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CONTENT
        expected.payload = "1"
        expected.content_type = defines.ContentType.TEXT_PLAIN
        expected.source = self.server_address

        ret = await client.get(path, timeout=10, accept=defines.ContentType.TEXT_PLAIN)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CONTENT
        expected.payload = "<value>1</value>"
        expected.content_type = defines.ContentType.application_xml
        expected.source = self.server_address

        ret = await client.get(path, timeout=10, accept=defines.ContentType.application_xml)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_21(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_21")
        path = "/validate"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CONTENT
        expected.payload = "Validate"
        expected.etag = b'\x01'
        expected.source = self.server_address

        ret = await client.get(path, timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.VALID
        expected.etag = b'\x01'
        expected.source = self.server_address
        expected.payload = None

        ret = await client.get(path, timeout=10, etag=b'\x01')
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        ret = await client.put(path, "Validate changed", timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CONTENT
        expected.etag = b'\x02'
        expected.source = self.server_address
        expected.payload = "Validate changed"

        ret = await client.get(path, timeout=10, etag=b'\x01')
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_22(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_22")
        path = "/validate"

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CONTENT
        expected.payload = "Validate"
        expected.etag = b'\x01'
        expected.source = self.server_address

        ret = await client.get(path, timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 6
        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CHANGED
        expected.source = self.server_address
        expected.payload = None

        ret = await client.put(path, "Validate changed", timeout=10, if_match=b'\x01')
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 10
        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CONTENT
        expected.payload = "Validate changed"
        expected.etag = b'\x02'
        expected.source = self.server_address

        ret = await client.get(path, timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 14
        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CHANGED
        expected.source = self.server_address

        ret = await client.put(path, "Step 13", timeout=10)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 14
        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.PRECONDITION_FAILED
        expected.source = self.server_address
        expected.payload = None

        ret = await client.put(path, "Step 17", timeout=10, if_match=b'\x02')
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_core_23(self):
        client, server = await self.start_client_server()
        print("TD_COAP_CORE_CLIENT_23")
        path = "/storage/create1"

        # STEP 3
        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.payload = None
        expected.source = self.server_address

        ret = await client.put(path, "New Resource", timeout=10, if_none_match=True)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        # STEP 6
        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.PRECONDITION_FAILED
        expected.source = self.server_address
        expected.payload = None

        ret = await client.put(path, "Validate changed", timeout=10, if_none_match=True)
        self.assertIsInstance(ret, Response)
        expected.token = ret.token
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))

        self.assertEqual(ret, expected)
        await self.stop_client_server(client, server)

