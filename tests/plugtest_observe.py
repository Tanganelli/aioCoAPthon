import logging
import random
import unittest

from aiounittest import async_test

from client.coap_client import CoAPClient
from server.coap_server import CoAPServer
from utilities import utils
from messages.message import Message
from messages.request import Request
from messages.response import Response
from tests.plugtest_observe_resources import *

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


class PlugtestObserveClass(unittest.TestCase):
    def setUp(self):
        self.server_address = ("127.0.0.1", 5683)
        self.server_mid = random.randint(1000, 2000)

    async def start_client_server(self):
        server = CoAPServer(self.server_address[0], self.server_address[1], starting_mid=self.server_mid)
        server.add_resource('obs/', ObserveResource())
        server.add_resource('obs-large/', LargeObserveResource())
        server.add_resource('not-obs/', NotObservableResource())
        server.add_resource('stable/', StableResource())

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
    async def test_td_coap_obs_01(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_01")
        path = "/obs"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "5"
        expected.token = token
        expected.observe = 2
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid+1
        expected.code = defines.Code.CONTENT
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        req = Message()
        req.code = defines.Code.EMPTY
        req.type = defines.Type.ACK
        req.mid = self.server_mid
        req.destination = self.server_address
        req.token = token

        transaction = await client.send_request(req)

        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 4
        expected.code = defines.Code.CONTENT
        expected.payload = "7"
        expected.token = token
        expected.observe = 4
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        req = Message()
        req.code = defines.Code.EMPTY
        req.type = defines.Type.RST
        req.mid = self.server_mid + 4
        req.destination = self.server_address
        req.token = token

        transaction = await client.send_request(req)
        await asyncio.sleep(5)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_02(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_02")
        path = "/obs"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.NON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.CONTENT
        expected.payload = "5"
        expected.token = token
        expected.observe = 2
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid + 2
        expected.code = defines.Code.CONTENT
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_06(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_06")
        path = "/obs"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "5"
        expected.token = token
        expected.observe = 2
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
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        req = Message()
        req.code = defines.Code.EMPTY
        req.type = defines.Type.RST
        req.mid = self.server_mid + 1
        req.destination = self.server_address
        req.token = token

        transaction = await client.send_request(req)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_07(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_07")
        path = "/obs"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "5"
        expected.token = token
        expected.observe = 2
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
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        req = Message()
        req.code = defines.Code.EMPTY
        req.type = defines.Type.ACK
        req.mid = self.server_mid + 1
        req.destination = self.server_address
        req.token = token

        transaction = await client.send_request(req)

        token2 = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.DELETE
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token2

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.DELETED
        expected.token = token2
        expected.source = self.server_address

        transaction2 = await client.send_request(req)
        ret = await client.receive_response(transaction2, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 4
        expected.code = defines.Code.NOT_FOUND
        expected.token = token
        expected.source = self.server_address

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        req = Message()
        req.code = defines.Code.EMPTY
        req.type = defines.Type.ACK
        req.mid = self.server_mid + 4
        req.destination = self.server_address
        req.token = token

        transaction = await client.send_request(req)
        await asyncio.sleep(5)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_08(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_08")
        path = "/obs"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "5"
        expected.token = token
        expected.observe = 2
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)
        else:
            print("PASS-EXCHANGE-01")

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 1
        expected.code = defines.Code.CONTENT
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)
        else:
            print("PASS-EXCHANGE-02")

        req = Message()
        req.code = defines.Code.EMPTY
        req.type = defines.Type.ACK
        req.mid = self.server_mid + 1
        req.destination = self.server_address
        req.token = token

        transaction = await client.send_request(req)

        token2 = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token2
        req.payload = "{ \"value\": 100}"
        req.content_type = defines.ContentType.application_json

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CHANGED
        expected.token = token2
        expected.source = self.server_address

        transaction2 = await client.send_request(req)
        ret = await client.receive_response(transaction2, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)
        else:
            print("PASS-EXCHANGE-03")

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 4
        expected.code = defines.Code.NOT_ACCEPTABLE
        expected.token = token
        expected.source = self.server_address
        expected.payload = "Content-Type changed"

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_09(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_09")
        path = "/obs"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "5"
        expected.token = token
        expected.observe = 2
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
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        req = Message()
        req.code = defines.Code.EMPTY
        req.type = defines.Type.ACK
        req.mid = self.server_mid + 1
        req.destination = self.server_address
        req.token = token

        transaction = await client.send_request(req)

        token2 = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token2
        req.payload = "100"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CHANGED
        expected.token = token2
        expected.source = self.server_address

        transaction2 = await client.send_request(req)
        ret = await client.receive_response(transaction2, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 4
        expected.code = defines.Code.CONTENT
        expected.token = token
        expected.source = self.server_address
        expected.observe = 4
        expected.payload = "100"

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_10(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_10")
        path = "/obs"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "5"
        expected.token = token
        expected.observe = 2
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
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        req = Message()
        req.code = defines.Code.EMPTY
        req.type = defines.Type.ACK
        req.mid = self.server_mid + 1
        req.destination = self.server_address
        req.token = token

        transaction = await client.send_request(req)

        token2 = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token2

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.token = token2
        expected.source = self.server_address
        expected.payload = "6"

        transaction2 = await client.send_request(req)
        ret = await client.receive_response(transaction2, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 4
        expected.code = defines.Code.CONTENT
        expected.payload = "7"
        expected.token = token
        expected.observe = 4
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_12(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_12")
        path = "/obs"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "5"
        expected.token = token
        expected.observe = 2
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
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        req = Message()
        req.code = defines.Code.EMPTY
        req.type = defines.Type.ACK
        req.mid = self.server_mid
        req.destination = self.server_address
        req.token = token

        transaction = await client.send_request(req)

        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.observe = 1
        req.token = token

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.token = token
        expected.source = self.server_address
        expected.payload = "6"

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_13(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_13")
        path = "/obs-large"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.token = token
        expected.observe = 2
        expected.source = "127.0.0.1", 5683
        expected.payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
                           "Cras accumsan tellus quis dui lacinia eleifend. Proin ultrices rutrum orci vitae luctus. " \
                           "Nullam malesuada pretium elit, at aliquam odio vehicula in. Etiam nec maximus elit. " \
                           "Etiam at erat ac ex ornare feugiat. Curabitur sed malesuada orci, id aliquet nunc. Phasellus " \
                           "nec leo luctus, blandit lorem sit amet, interdum metus. Duis efficitur volutpat magna, ac " \
                           "ultricies nibh aliquet sit amet. Etiam tempor egestas augue in hendrerit. Nunc eget augue " \
                           "ultricies, dignissim lacus et, vulputate dolor. Nulla eros odio, fringilla vel massa ut, " \
                           "facilisis cursus quam. Fusce faucibus lobortis congue. Fusce consectetur porta neque, id " \
                           "sollicitudin velit maximus eu. Sed pharetra leo quam, vel finibus turpis cursus ac. " \
                           "Aenean ac nisi massa. Cras commodo arcu nec ante tristique ullamcorper. Quisque eu hendrerit" \
                           " urna. Cras fringilla eros ut nunc maximus, non porta nisl mollis. Aliquam in rutrum massa." \
                           " Praesent tristique turpis dui, at ultri"
        expected.block2 = (0, 1, 1024)

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.block2 = (1, 0, 1024)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
                           "a imperdiet nisl. Quisque a iaculis libero, id tempus lacus. " \
                           "Aenean convallis est non justo consectetur, a hendrerit enim consequat. In accumsan ante " \
                           "a egestas luctus. Etiam quis neque nec eros vestibulum faucibus. Nunc viverra ipsum " \
                           "lectus, vel scelerisque dui dictum a. Ut orci enim, ultrices a ultrices nec, pharetra " \
                           "in quam. Donec accumsan sit amet eros eget fermentum." \
                           "Vivamus ut odio ac odio malesuada accumsan. Aenean vehicula diam at tempus ornare. " \
                           "Phasellus dictum mauris a mi consequat, vitae mattis nulla fringilla. Ut laoreet " \
                           "tellus in nisl efficitur, a luctus justo tempus. Fusce finibus libero eget velit " \
                           "finibus iaculis. Morbi rhoncus purus vel vestibulum ullamcorper. Sed ac metus in urna " \
                           "fermentum feugiat. Nulla nunc diam, sodales aliquam mi id, varius porta nisl. Praesent " \
                           "vel nibh ac turpis rutrum laoreet at non odio. Phasellus ut posuere mi. Suspendisse " \
                           "malesuada velit nec mauris convallis porta. Vivamus sed ultrices sapien, at cras amet."

        expected.token = token
        expected.block2 = (1, 0, 1024)
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 2
        expected.code = defines.Code.CONTENT
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683
        expected.payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
                           "Cras accumsan tellus quis dui lacinia eleifend. Proin ultrices rutrum orci vitae luctus. " \
                           "Nullam malesuada pretium elit, at aliquam odio vehicula in. Etiam nec maximus elit. " \
                           "Etiam at erat ac ex ornare feugiat. Curabitur sed malesuada orci, id aliquet nunc. Phasellus " \
                           "nec leo luctus, blandit lorem sit amet, interdum metus. Duis efficitur volutpat magna, ac " \
                           "ultricies nibh aliquet sit amet. Etiam tempor egestas augue in hendrerit. Nunc eget augue " \
                           "ultricies, dignissim lacus et, vulputate dolor. Nulla eros odio, fringilla vel massa ut, " \
                           "facilisis cursus quam. Fusce faucibus lobortis congue. Fusce consectetur porta neque, id " \
                           "sollicitudin velit maximus eu. Sed pharetra leo quam, vel finibus turpis cursus ac. " \
                           "Aenean ac nisi massa. Cras commodo arcu nec ante tristique ullamcorper. Quisque eu hendrerit" \
                           " urna. Cras fringilla eros ut nunc maximus, non porta nisl mollis. Aliquam in rutrum massa." \
                           " Praesent tristique turpis dui, at ultri"
        expected.block2 = (0, 1, 1024)

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        req = Message()
        req.code = defines.Code.EMPTY
        req.type = defines.Type.ACK
        req.mid = self.server_mid + 2
        req.destination = self.server_address
        req.token = token

        transaction = await client.send_request(req)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_14(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_14")
        path = "/not-obs"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "NotObservable"
        expected.token = token
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_15(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_15")
        path = "/stable"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Stable"
        expected.token = token
        expected.observe = 2
        expected.max_age = 20
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
        expected.payload = "Stable"
        expected.token = token
        expected.observe = 2
        expected.max_age = 20
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 60)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_16(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_16")
        path = "/stable"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.NON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Stable"
        expected.token = token
        expected.observe = 2
        expected.max_age = 20
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid + 2
        expected.code = defines.Code.CONTENT
        expected.payload = "Stable"
        expected.token = token
        expected.observe = 2
        expected.max_age = 20
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 60)

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_17(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_17")
        path = "/stable"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.observe = 0

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Stable"
        expected.token = token
        expected.observe = 2
        expected.max_age = 20
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        await asyncio.sleep(120)

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 1
        expected.code = defines.Code.CONTENT
        expected.payload = "Stable"
        expected.token = token
        expected.observe = 2
        expected.max_age = 20
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)
        else:
            print("Received #1")

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 1
        expected.code = defines.Code.CONTENT
        expected.payload = "Stable"
        expected.token = token
        expected.observe = 2
        expected.max_age = 20
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)
        else:
            print("Received #2")

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 1
        expected.code = defines.Code.CONTENT
        expected.payload = "Stable"
        expected.token = token
        expected.observe = 2
        expected.max_age = 20
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)
        else:
            print("Received #3")

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid + 1
        expected.code = defines.Code.CONTENT
        expected.payload = "Stable"
        expected.token = token
        expected.observe = 2
        expected.max_age = 20
        expected.source = "127.0.0.1", 5683

        transaction.response = None
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)
        else:
            print("Received #4")

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)
