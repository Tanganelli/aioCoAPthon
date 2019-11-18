import random
import logging
import unittest

from aiounittest import async_test

from client.coap_client import CoAPClient
from server.coap_server import CoAPServer
from utilities import utils
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


class PlugtestObserveClientClass(unittest.TestCase):
    def setUp(self):
        self.server_address = ("127.0.0.1", 5683)
        self.server_mid = random.randint(1000, 2000)

    async def start_client_server(self):
        server = CoAPServer(self.server_address[0], self.server_address[1], starting_mid=self.server_mid)
        server.add_resource('obs/', ObserveResource())
        server.add_resource('obs-large/', LargeObserveResource())

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

    async def consumer(self, receive_queue, expected_queue):
        while not expected_queue.empty():
            ret = await receive_queue.get()
            receive_queue.task_done()
            expected = await expected_queue.get()
            self.assertIsInstance(ret, Response)
            expected.mid = ret.mid

            if ret != expected:
                print("Received: {0}".format(ret))
                print("Expected: {0}".format(expected))
                self.assertEqual(ret, expected)
            expected_queue.task_done()

    @async_test
    async def test_td_coap_obs_01(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_CLIENT_01")
        path = "/obs"

        token = utils.generate_random_hex(2)

        receive_queue = asyncio.Queue()
        expected_queue = asyncio.Queue()
        event = asyncio.Event()

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CONTENT
        expected.payload = "5"
        expected.token = token
        expected.observe = 2
        expected.source = "127.0.0.1", 5683

        await expected_queue.put(expected)

        expected = Response()
        expected.type = defines.Type.CON
        expected.mid = self.server_mid
        expected.code = defines.Code.CONTENT
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        await expected_queue.put(expected)

        asyncio.get_event_loop().create_task(self.consumer(receive_queue, expected_queue))

        asyncio.get_event_loop().create_task(client.observe(path, queue=receive_queue, stop=event, timeout=60,
                                                            token=token))

        await expected_queue.join()
        event.set()

        print("PASS")

        self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_obs_02(self):
        client, server = await self.start_client_server()
        print("TD_COAP_OBS_CLIENT_02")
        path = "/obs"

        token = utils.generate_random_hex(2)

        receive_queue = asyncio.Queue()
        expected_queue = asyncio.Queue()
        event = asyncio.Event()

        expected = Response()
        expected.type = defines.Type.NON
        expected.code = defines.Code.CONTENT
        expected.payload = "5"
        expected.token = token
        expected.observe = 2
        expected.source = "127.0.0.1", 5683

        await expected_queue.put(expected)

        expected = Response()
        expected.type = defines.Type.NON
        expected.mid = self.server_mid
        expected.code = defines.Code.CONTENT
        expected.payload = "6"
        expected.token = token
        expected.observe = 3
        expected.source = "127.0.0.1", 5683

        await expected_queue.put(expected)

        asyncio.get_event_loop().create_task(self.consumer(receive_queue, expected_queue))

        asyncio.get_event_loop().create_task(client.observe_non(path, queue=receive_queue, stop=event, timeout=60,
                                                                token=token))

        await expected_queue.join()
        event.set()

        print("PASS")

        self.stop_client_server(client, server)
