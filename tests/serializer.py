import unittest
from aiounittest import async_test

from utilities import defines
from messages.request import Request
from utilities.serializer import Serializer


class Tests(unittest.TestCase):

    @async_test
    async def test_serialization(self):
        message = Request()
        message.source = ("127.0.0.1", 5000)
        message.destination = ("ff80::1", 5683)
        message.mid = 1
        message.type = defines.Type.CON
        message.code = defines.Code.GET
        message.token = b'ABCD'
        message.uri_path = "temp/test"
        message.uri_query = "foo&bar=4"
        message.no_response = True
        message.payload = "Test Payload"
        str_message = str(message)
        serializer = Serializer()
        datagram = await serializer.serialize(message)
        message = await serializer.deserialize(datagram, ("127.0.0.1", 5000), ("ff80::1", 5683))
        self.assertEqual(str_message, str(message))

    def main(self):
        unittest.main()