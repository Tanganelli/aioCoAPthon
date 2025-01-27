import random
import asyncio
import logging
import unittest

from aiounittest import async_test

from aiocoapthon.client.coap_client import CoAPClient
from aiocoapthon.server.coap_server import CoAPServer
from aiocoapthon.utilities import defines, utils
from aiocoapthon.messages.response import Response
from aiocoapthon.tests.plugtest_block_resources import *

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


class PlugtestBlockClientClass(unittest.TestCase):  # pragma: no cover
    def setUp(self):
        self.server_address = ("127.0.0.1", 5683)
        self.server_mid = random.randint(1000, 2000)

    async def start_client_server(self):
        server = CoAPServer(self.server_address[0], self.server_address[1], starting_mid=self.server_mid)
        server.add_resource('large/', LargeResource())
        server.add_resource('large-update/', LargeUpdateResource())
        server.add_resource('large-create/', LargeCreateResource())

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
    async def test_td_coap_block_01(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_01")
        path = "/large"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get(path, timeout=10, block2=(0, 0, 1024), token=token)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_02(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_02")
        path = "/large"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get(path, timeout=10, token=token)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_03(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_03")
        path = "/large-update"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CHANGED
        expected.token = token
        expected.block1 = (1, 0, 1024)
        expected.source = "127.0.0.1", 5683

        payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                  " Praesent tristique turpis dui, at ultri" \
                  "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.put(path, payload, timeout=10, block1=(0, 1, 1024), token=token)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get(path, timeout=10, block2=(0, 0, 1024), token=token)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_03b(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_03B")
        path = "/large-update"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CHANGED
        expected.token = token
        expected.block1 = (1, 0, 1024)
        expected.source = "127.0.0.1", 5683

        payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                  " Praesent tristique turpis dui, at ultri" \
                  "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.put(path, payload, timeout=10, token=token)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get(path, timeout=10, token=token)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_04(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_04")
        path = "/large-create"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.token = token
        expected.location_path = "/large-create/ps"
        expected.block1 = (1, 0, 1024)
        expected.source = "127.0.0.1", 5683

        payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                  " Praesent tristique turpis dui, at ultri" \
                  "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.post(path, payload, timeout=10, block1=(0, 1, 1024), token=token)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get("/large-create/ps", timeout=10, block2=(0, 0, 1024), token=token)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_04b(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_04B")
        path = "/large-create"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.token = token
        expected.block1 = (1, 0, 1024)
        expected.source = "127.0.0.1", 5683
        expected.location_path = "/large-create/ps"

        payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                  " Praesent tristique turpis dui, at ultri" \
                  "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.post(path, payload, timeout=10, token=token)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get("/large-create/ps", timeout=10, token=token)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_05(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_05")
        path = "/large"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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
        expected.block2 = (7, 0, 256)
        expected.source = "127.0.0.1", 5683

        ret = await client.get(path, timeout=10, block2=(0, 0, 256), token=token)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)
        expected.token = token
        del expected.block2
        expected.block2 = (15, 0, 128)

        ret = await client.get(path, timeout=10, block2=(0, 0, 128), token=token)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)
        expected.token = token
        del expected.block2
        expected.block2 = (31, 0, 64)

        ret = await client.get(path, timeout=10, block2=(0, 0, 64), token=token)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)
        expected.token = token
        del expected.block2
        expected.block2 = (63, 0, 32)

        ret = await client.get(path, timeout=10, block2=(0, 0, 32), token=token)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)
        expected.token = token
        del expected.block2
        expected.block2 = (127, 0, 16)

        ret = await client.get(path, timeout=10, block2=(0, 0, 16), token=token)
        self.assertIsInstance(ret, Response)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_06(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_06")
        path = "/large-create"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.token = token
        expected.location_path = "/large-create/ps"
        expected.block1 = (3, 0, 512)
        expected.source = "127.0.0.1", 5683

        payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                  " Praesent tristique turpis dui, at ultri" \
                  "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.post(path, payload, timeout=10, block1=(0, 1, 512), token=token)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get("/large-create/ps", timeout=10, block2=(0, 0, 1024), token=token)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_07(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_07")
        path = "/large-create"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.token = token
        expected.location_path = "/large-create/ps"
        expected.block1 = (7, 0, 256)
        expected.source = "127.0.0.1", 5683

        payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                  " Praesent tristique turpis dui, at ultri" \
                  "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.post(path, payload, timeout=10, block1=(0, 1, 256), token=token)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get("/large-create/ps", timeout=10, block2=(0, 0, 1024), token=token)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_08(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_08")
        path = "/large-create"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.token = token
        expected.location_path = "/large-create/ps"
        expected.block1 = (15, 0, 128)
        expected.source = "127.0.0.1", 5683

        payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                  " Praesent tristique turpis dui, at ultri" \
                  "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.post(path, payload, timeout=10, block1=(0, 1, 128), token=token)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get("/large-create/ps", timeout=10, block2=(0, 0, 1024), token=token)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_09(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_09")
        path = "/large-create"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.token = token
        expected.location_path = "/large-create/ps"
        expected.block1 = (31, 0, 64)
        expected.source = "127.0.0.1", 5683

        payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                  " Praesent tristique turpis dui, at ultri" \
                  "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.post(path, payload, timeout=10, block1=(0, 1, 64), token=token)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get("/large-create/ps", timeout=10, block2=(0, 0, 1024), token=token)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_10(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_10")
        path = "/large-create"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.token = token
        expected.location_path = "/large-create/ps"
        expected.block1 = (63, 0, 32)
        expected.source = "127.0.0.1", 5683

        payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                  " Praesent tristique turpis dui, at ultri" \
                  "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.post(path, payload, timeout=10, block1=(0, 1, 32), token=token)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get("/large-create/ps", timeout=10, block2=(0, 0, 1024), token=token)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)

    @async_test
    async def test_td_coap_block_11(self):
        client, server = await self.start_client_server()
        print("TD_COAP_BLOCK_CLIENT_11")
        path = "/large-create"

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
        expected.code = defines.Code.CREATED
        expected.token = token
        expected.location_path = "/large-create/ps"
        expected.block1 = (127, 0, 16)
        expected.source = "127.0.0.1", 5683

        payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                  " Praesent tristique turpis dui, at ultri" \
                  "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.post(path, payload, timeout=10, block1=(0, 1, 16), token=token)
        expected.mid = ret.mid

        if ret != expected:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            self.assertEqual(ret, expected)

        token = utils.generate_random_hex(2)

        expected = Response()
        expected.type = defines.Type.ACK
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
                           " Praesent tristique turpis dui, at ultri" \
                           "cies lorem fermentum at. Vivamus sit amet ornare neque, " \
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

        ret = await client.get("/large-create/ps", timeout=10, block2=(0, 0, 1024), token=token)
        expected.mid = ret.mid

        if ret == expected:
            print("PASS")
        else:
            print("Received: {0}".format(ret))
            print("Expected: {0}".format(expected))
            print(ret.pretty_print())

        self.assertEqual(ret, expected)

        await self.stop_client_server(client, server)