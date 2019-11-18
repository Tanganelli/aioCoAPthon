import logging
import random
import unittest

import asyncio
from aiounittest import async_test

from client.coap_client import CoAPClient
from server.coap_server import CoAPServer
from tests.plugtest_block_resources import *
from utilities import defines
from utilities import utils
from messages.request import Request
from messages.response import Response

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


class PlugtestBlockClass(unittest.TestCase):
    def setUp(self):
        self.server_address = ("127.0.0.1", 5683)
        self.server_mid = random.randint(1000, 2000)

    async def start_client_server(self):
        server = CoAPServer(self.server_address[0], self.server_address[1], starting_mid=self.server_mid)
        server.add_resource('large/', LargeResource())
        server.add_resource('large-update/', LargeUpdateResource())
        server.add_resource('large-create/', LargeCreateResource())

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
    async def test_td_coap_block_01(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_01")
        path = "/large"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.block2 = (0, 0, 1024)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
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

        expected.token = token
        expected.block2 = (0, 1, 1024)
        expected.source = "127.0.0.1", 5683

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
        expected.payload = "cies lorem fermentum at. Vivamus sit amet ornare neque, "\
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

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_01b(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_01B")
        path = "/large"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.block2 = (0, 0, 1024)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
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

        expected.token = token
        expected.block2 = (0, 1, 1024)
        expected.source = "127.0.0.1", 5683

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
        req.block2 = (1, 0, 512)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "cies lorem fermentum at. Vivamus sit amet ornare neque, a imperdiet nisl. Quisque a " \
                           "iaculis libero, id tempus lacus. Aenean convallis est non justo consectetur, a " \
                           "hendrerit enim consequat. In accumsan ante a egestas luctus. Etiam quis neque nec " \
                           "eros vestibulum faucibus. Nunc viverra ipsum lectus, vel scelerisque dui dictum a. " \
                           "Ut orci enim, ultrices a ultrices nec, pharetra in quam. Donec accumsan sit amet eros " \
                           "eget fermentum.Vivamus ut odio ac odio malesuada accumsan. Aenean vehicula diam at " \
                           "tempus ornare. "

        expected.token = token
        expected.block2 = (1, 1, 512)
        expected.source = "127.0.0.1", 5683

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
        req.block2 = (2, 0, 512)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Phasellus dictum mauris a mi consequat, vitae mattis nulla fringilla. Ut laoreet tellus " \
                           "in nisl efficitur, a luctus justo tempus. Fusce finibus libero eget velit finibus " \
                           "iaculis. Morbi rhoncus purus vel vestibulum ullamcorper. Sed ac metus in urna " \
                           "fermentum feugiat. Nulla nunc diam, sodales aliquam mi id, varius porta nisl. " \
                           "Praesent vel nibh ac turpis rutrum laoreet at non odio. Phasellus ut posuere mi. " \
                           "Suspendisse malesuada velit nec mauris convallis porta. Vivamus sed ultrices sapien, " \
                           "at cras amet."

        expected.token = token
        expected.block2 = (2, 0, 512)
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
    async def test_td_coap_block_02(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_02")
        path = "/large"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin " \
                           "fermentum ornare. " \
                           "Cras accumsan tellus quis dui lacinia eleifend. Proin ultrices rutrum orci vitae luctus. " \
                           "Nullam malesuada pretium elit, at aliquam odio vehicula in. Etiam nec maximus elit. " \
                           "Etiam at erat ac ex ornare feugiat. Curabitur sed malesuada orci, id aliquet nunc. " \
                           "Phasellus " \
                           "nec leo luctus, blandit lorem sit amet, interdum metus. " \
                           "Duis efficitur volutpat magna, ac " \
                           "ultricies nibh aliquet sit amet. Etiam tempor egestas augue in hendrerit. " \
                           "Nunc eget augue " \
                           "ultricies, dignissim lacus et, vulputate dolor. Nulla eros odio, fringilla vel massa ut, " \
                           "facilisis cursus quam. Fusce faucibus lobortis congue. Fusce consectetur porta neque, id " \
                           "sollicitudin velit maximus eu. Sed pharetra leo quam, vel finibus turpis cursus ac. " \
                           "Aenean ac nisi massa. Cras commodo arcu nec ante tristique ullamcorper. " \
                           "Quisque eu hendrerit" \
                           " urna. Cras fringilla eros ut nunc maximus, non porta nisl mollis. Aliquam in " \
                           "rutrum massa." \
                           " Praesent tristique turpis dui, at ultri"

        expected.token = token
        expected.block2 = (0, 1, 1024)
        expected.source = "127.0.0.1", 5683

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

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_02b(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_02B")
        path = "/large"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin " \
                           "fermentum ornare. " \
                           "Cras accumsan tellus quis dui lacinia eleifend. Proin ultrices rutrum orci vitae luctus. " \
                           "Nullam malesuada pretium elit, at aliquam odio vehicula in. Etiam nec maximus elit. " \
                           "Etiam at erat ac ex ornare feugiat. Curabitur sed malesuada orci, id aliquet nunc. " \
                           "Phasellus " \
                           "nec leo luctus, blandit lorem sit amet, interdum metus. " \
                           "Duis efficitur volutpat magna, ac " \
                           "ultricies nibh aliquet sit amet. Etiam tempor egestas augue in hendrerit. " \
                           "Nunc eget augue " \
                           "ultricies, dignissim lacus et, vulputate dolor. Nulla eros odio, fringilla vel massa ut, " \
                           "facilisis cursus quam. Fusce faucibus lobortis congue. Fusce consectetur porta neque, id " \
                           "sollicitudin velit maximus eu. Sed pharetra leo quam, vel finibus turpis cursus ac. " \
                           "Aenean ac nisi massa. Cras commodo arcu nec ante tristique ullamcorper. " \
                           "Quisque eu hendrerit" \
                           " urna. Cras fringilla eros ut nunc maximus, non porta nisl mollis. Aliquam in " \
                           "rutrum massa." \
                           " Praesent tristique turpis dui, at ultri"

        expected.token = token
        expected.block2 = (0, 1, 1024)
        expected.source = "127.0.0.1", 5683

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
        req.block2 = (1, 0, 512)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "cies lorem fermentum at. Vivamus sit amet ornare neque, a imperdiet nisl. Quisque a " \
                           "iaculis libero, id tempus lacus. Aenean convallis est non justo consectetur, a " \
                           "hendrerit enim consequat. In accumsan ante a egestas luctus. Etiam quis neque nec " \
                           "eros vestibulum faucibus. Nunc viverra ipsum lectus, vel scelerisque dui dictum a. " \
                           "Ut orci enim, ultrices a ultrices nec, pharetra in quam. Donec accumsan sit amet eros " \
                           "eget fermentum.Vivamus ut odio ac odio malesuada accumsan. Aenean vehicula diam at " \
                           "tempus ornare. "

        expected.token = token
        expected.block2 = (1, 1, 512)
        expected.source = "127.0.0.1", 5683

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
        req.block2 = (2, 0, 512)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
        expected.payload = "Phasellus dictum mauris a mi consequat, vitae mattis nulla fringilla. Ut laoreet tellus " \
                           "in nisl efficitur, a luctus justo tempus. Fusce finibus libero eget velit finibus " \
                           "iaculis. Morbi rhoncus purus vel vestibulum ullamcorper. Sed ac metus in urna " \
                           "fermentum feugiat. Nulla nunc diam, sodales aliquam mi id, varius porta nisl. " \
                           "Praesent vel nibh ac turpis rutrum laoreet at non odio. Phasellus ut posuere mi. " \
                           "Suspendisse malesuada velit nec mauris convallis porta. Vivamus sed ultrices sapien, " \
                           "at cras amet."

        expected.token = token
        expected.block2 = (2, 0, 512)
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
    async def test_td_coap_block_03(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_03")
        path = "/large-update"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.block1 = (0, 1, 1024)
        req.payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTINUE
        expected.token = token
        expected.block1 = (0, 1, 1024)
        expected.source = "127.0.0.1", 5683

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
        req.token = token
        req.block1 = (1, 0, 1024)
        req.payload = "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CHANGED
        expected.token = token
        expected.block1 = (1, 0, 1024)
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
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

        expected.token = token
        expected.block2 = (0, 1, 1024)
        expected.source = "127.0.0.1", 5683

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

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_03b(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_03B")
        path = "/large-update"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.PUT
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.block1 = (0, 1, 2048)
        req.payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc malesuada eget nunc " \
                      "interdum rutrum. In cursus mauris tortor, pulvinar mollis nibh sollicitudin et. Cras " \
                      "malesuada magna eu vestibulum semper. Cras sit amet molestie dolor. Class aptent " \
                      "taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Praesent " \
                      "tortor velit, tempor ac interdum eget, fermentum vitae turpis. Etiam nisi sem, " \
                      "porta vel euismod quis, malesuada non lorem. Phasellus commodo nisl id justo efficitur, " \
                      "eu dapibus est semper.Sed vel sollicitudin purus. Ut viverra est facilisis ligula volutpat," \
                      " faucibus vestibulum nunc porttitor. Donec arcu elit, aliquam nec mattis eget, faucibus " \
                      "sit amet libero. Donec at mi eget dui ullamcorper malesuada at ut lorem. Maecenas varius" \
                      " congue augue nec convallis. Aenean sed urna non mi finibus fermentum. Aliquam vestibulum " \
                      "pharetra felis nec finibus. Nunc leo orci, commodo sit amet diam vel, facilisis tincidunt " \
                      "odio.Sed libero quam, eleifend at ante ac, gravida interdum tellus. Aliquam mattis ultrices " \
                      "viverra. Aliquam ultrices finibus erat, vel semper diam. Pellentesque auctor tortor vel " \
                      "erat laoreet venenatis. Nam mauris metus, egestas at dapibus quis, efficitur et quam. " \
                      "Vestibulum tempor, erat sit amet consectetur pellentesque, dui orci iaculis tellus, at " \
                      "volutpat tellus lacus congue libero. Suspendisse potenti. Aliquam placerat ut mauris ac " \
                      "mollis. Vestibulum eget urna lacus. Aenean ut laoreet velit. Pellentesque quis consectetur " \
                      "risus, eget tristique diam. Quisque ut mollis erat, et semper ipsum.Phasellus porta quam in " \
                      "nisl rutrum, at pretium lorem maximus. Donec a dapibus tellus, id suscipit orci. Suspendisse" \
                      " in porta tellus. Donec et accumsan felis. Donec non tempor diam, eu ornare libero. Morbi vel " \
                      "consequat lectus, eget facilisis sapien. Duis magna justo, dictum et tellus et, pulvinar " \
                      "cursus nisl. Proin vitae tincidunt sem. Nam et accumsan purus, at finibus augue. Praesent " \
                      "tellus tortor, sodales a neque id, fringilla tincidunt lectus. Ut quis augue eu nulla " \
                      "lobortis ultrices id ne"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTINUE
        expected.token = token
        expected.block1 = (0, 1, 1024)
        expected.source = "127.0.0.1", 5683

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
        req.token = token
        req.block1 = (1, 1, 1024)
        req.payload = "c est. In vestibulum viverra facilisis. Aliquam posuere lectus " \
                      "eget facilisis faucibus. In hac habitasse platea dictumst.Vestibulum ornare lorem ac " \
                      "consequat volutpat. Fusce tristique nisi quis lorem congue, tincidunt pellentesque mi " \
                      "facilisis. Aliquam nec orci mollis, mollis metus id, maximus ex. Nunc sit amet purus " \
                      "non quam luctus posuere sit amet nec dui. Nulla suscipit erat sem, ac facilisis justo " \
                      "rutrum eget. Cras neque augue, blandit a imperdiet nec, dignissim non elit. Pellentesque " \
                      "vitae sem ac neque ornare posuere id sed elit. Aliquam erat volutpat. Nulla facilisi.Etiam " \
                      "quis ultrices nunc. Proin elit sapien, rutrum id felis sed, eleifend dignissim mi. Nulla " \
                      "non est gravida, placerat tortor quis, dapibus lectus. Aliquam tempus velit vitae est " \
                      "posuere, nec sodales massa luctus. Duis feugiat ex in facilisis posuere. Quisque in mi " \
                      "massa. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus " \
                      "mus. Nullam semper massa id arcu lobortis lobortis. Donec pulvinar auctor massa, imperdi"

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTINUE
        expected.token = token
        expected.block1 = (1, 1, 1024)
        expected.source = "127.0.0.1", 5683

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
        req.token = token
        req.block1 = (2, 0, 1024)
        req.payload = "et " \
                      "varius tortor.Nunc rhoncus sit amet ipsum nec pulvinar. Duis vel luctus nunc, nec hendrerit " \
                      "nulla. Sed suscipit elit ornare tempus imperdiet. Nulla vel aliquet arcu. Vivamus tristique " \
                      "quam dignissim nulla tempus ultricies. Fusce eu arcu egestas, aliquet ipsum non, iaculis ex. " \
                      "Mauris ut hendrerit velit, a faucibus metus. Quisque consectetur nec mi quis egestas. Cras " \
                      "sodales ipsum sapien, at varius lectus elementum nec. Nullam dictum mattis maximus. Fusce " \
                      "hendrerit rutrum condimentum. Cras malesuada risus sed hendrerit dignissim.Vestibulum vel " \
                      "velit eu urna consequat ullamcorper. Ut ut eros ac quam molestie feugiat. Mauris vehicula " \
                      "pharetra purus sed aliquam. Maecenas eget placerat nisi, ut pharetra dui. Mauris in dictum" \
                      " sem. Duis lacinia erat nec turpis semper euismod. In cursus non felis quis varius. Fusce " \
                      "mauris nunc, dapibus at bibendum vel, molestie vitae dolor. Donec ut orci at lorem tristique " \
                      "tincidunt. Nullam condimentum a lacus ut scelerisque. Vivamus sed leo ipsum. Sed in felis " \
                      "eget eros cras amet."

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CHANGED
        expected.token = token
        expected.block1 = (2, 0, 1024)
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
    async def test_td_coap_block_04(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_04")
        path = "/large-create"

        token = utils.generate_random_hex(2)
        req = Request()
        req.code = defines.Code.POST
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token
        req.block1 = (0, 1, 1024)
        req.payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTINUE
        expected.token = token
        expected.block1 = (0, 1, 1024)
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
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
        req.token = token
        req.block1 = (1, 0, 1024)
        req.payload = "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CREATED
        expected.token = token
        expected.block1 = (1, 0, 1024)
        expected.source = "127.0.0.1", 5683
        expected.location_path = "/large-create/ps"

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)
        path = expected.location_path
        req = Request()
        req.code = defines.Code.GET
        req.uri_path = path
        req.type = defines.Type.CON
        req.mid = random.randint(1, 1000)
        req.destination = self.server_address
        req.token = token

        expected = Response()
        expected.type = defines.Type.ACK
        expected.mid = req.mid
        expected.code = defines.Code.CONTENT
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

        expected.token = token
        expected.block2 = (0, 1, 1024)
        expected.source = "127.0.0.1", 5683

        transaction = await client.send_request(req)
        ret = await client.receive_response(transaction, 10)

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())
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

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        self.stop_client_server(client, server)
