import asyncio
import logging
import random
import unittest

from aiounittest import async_test

from aiocoapthon.client.coap_client import CoAPClient
from aiocoapthon.messages.request import Request
from aiocoapthon.server.coap_server import CoAPServer
from aiocoapthon.tests.plugtest_link_resources import *
from aiocoapthon.utilities import defines, utils
from aiocoapthon.messages.response import Response

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


class PlugtestLinkClass(unittest.TestCase):  # pragma: no cover
    def setUp(self):
        self.server_address = ("127.0.0.1", 5683)
        self.server_mid = random.randint(1000, 2000)

    async def start_client_server(self):
        server = CoAPServer(self.server_address[0], self.server_address[1], starting_mid=self.server_mid)
        server.add_resource('type1/', Type1Resource())
        server.add_resource('type2/', Type2Resource())
        server.add_resource('group-type1/', GroupType1Resource())
        server.add_resource('group-type2/', GroupType2Resource())
        server.add_resource('group-type3/', GroupType3Resource())
        server.add_resource('group-type4/', GroupType4Resource())
        server.add_resource('group-if1/', GroupIf1Resource())
        server.add_resource('group-if2/', GroupIf2Resource())
        server.add_resource('group-if3/', GroupIf3Resource())
        server.add_resource('group-if4/', GroupIf4Resource())
        server.add_resource('sz/', SzResource())
        server.add_resource('link1/', LinkResource())
        server.add_resource('link2/', LinkResource())
        server.add_resource('link3/', LinkResource())

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
    async def test_td_coap_link_01(self):
        client, server = await self.start_client_server()
        print("TD_COAP_LINK_01")
        path = "/.well-known/core"
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
        expected.payload = '</group-if1>;if="if1",obs,</group-if2>;if="if2",obs,</group-if3>;if="foo",obs,' \
                           '</group-if4>;obs,</group-type1>;obs,rt="Type1 Type2",</group-type2>;obs,rt="Type2 Type3",' \
                           '</group-type3>;obs,rt="Type1 Type3",</group-type4>;obs,rt,</link1>;obs,</link2>;obs,' \
                           '</link3>;obs,</sz>;obs,sz="10",</type1>;obs,rt="Type1",</type2>;obs,rt="Type2"'

        expected.token = req.token
        expected.content_type = defines.ContentType.application_link_format
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
    async def test_td_coap_link_02(self):
        client, server = await self.start_client_server()
        print("TD_COAP_LINK_02")
        path = "/.well-known/core"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.uri_query = "?rt=Type1"
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = '</group-type1>;obs,rt="Type1 Type2",</group-type3>;obs,rt="Type1 Type3",' \
                           '</type1>;obs,rt="Type1"'
        expected.token = req.token
        expected.content_type = defines.ContentType.application_link_format
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
    async def test_td_coap_link_03(self):
        client, server = await self.start_client_server()
        print("TD_COAP_LINK_03")
        path = "/.well-known/core"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.uri_query = "?rt=*"
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = '</group-type1>;obs,rt="Type1 Type2",</group-type2>;obs,rt="Type2 Type3",' \
                           '</group-type3>;obs,rt="Type1 Type3",</group-type4>;obs,rt,</type1>;obs,rt="Type1",' \
                           '</type2>;obs,rt="Type2"'

        expected.token = req.token
        expected.content_type = defines.ContentType.application_link_format
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
    async def test_td_coap_link_04(self):
        client, server = await self.start_client_server()
        print("TD_COAP_LINK_04")
        path = "/.well-known/core"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.uri_query = "?rt=Type2"
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = '</group-type1>;obs,rt="Type1 Type2",</group-type2>;obs,rt="Type2 Type3",' \
                           '</type2>;obs,rt="Type2"'
        expected.token = req.token
        expected.content_type = defines.ContentType.application_link_format
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
    async def test_td_coap_link_05(self):
        client, server = await self.start_client_server()
        print("TD_COAP_LINK_05")
        path = "/.well-known/core"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.uri_query = "?if=if*"
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = '</group-if1>;if="if1",obs,</group-if2>;if="if2",obs'
        expected.token = req.token
        expected.content_type = defines.ContentType.application_link_format
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
    async def test_td_coap_link_06(self):
        client, server = await self.start_client_server()
        print("TD_COAP_LINK_06")
        path = "/.well-known/core"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.uri_query = "?sz=*"
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = '</sz>;obs,sz="10"'
        expected.token = req.token
        expected.content_type = defines.ContentType.application_link_format
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
    async def test_td_coap_link_07(self):
        client, server = await self.start_client_server()
        print("TD_COAP_LINK_07")
        path = "/.well-known/core"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.uri_query = "?href=/link1"
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = '</link1>;obs'
        expected.token = req.token
        expected.content_type = defines.ContentType.application_link_format
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
    async def test_td_coap_link_08(self):
        client, server = await self.start_client_server()
        print("TD_COAP_LINK_08")
        path = "/.well-known/core"
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.uri_query = "?href=/link*"
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = '</link1>;obs,</link2>;obs,</link3>;obs'
        expected.token = req.token
        expected.content_type = defines.ContentType.application_link_format
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
