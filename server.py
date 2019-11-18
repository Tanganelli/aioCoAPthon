#!/usr/bin/env python3.6
import signal
import sys

import asyncio
import logging.config

from server.coap_server import CoAPServer
from utilities import defines
from utilities import utils
from messages.request import Request
from messages.response import Response
from resources.resource import Resource

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

__author__ = 'Giacomo Tanganelli'


class BasicResource(Resource):
    def __init__(self, name="Advanced"):
        super(BasicResource, self).__init__(name)
        self.payload = "Advanced resource"

    def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.max_age = 20
        return self, response

    def handle_post(self, request: "Request", response: "Response"):
        self.payload = request.payload
        response.payload = "Response changed through POST"
        return self, response

    def handle_put(self, request: "Request", response: "Response"):
        self.payload = request.payload
        response.payload = "Response changed through PUT"
        return self, response

    def handle_delete(self, request: "Request", response: "Response"):
        response.payload = "Response deleted"
        return True, response


class SeparateResource(Resource):
    def __init__(self, name="Advanced"):
        super(SeparateResource, self).__init__(name)
        self.payload = "Advanced resource Separate"

    def handle_get(self, request: "Request", response: "Response"):
        return self.get_callback

    def handle_post(self, request: "Request", response: "Response"):
        return self.post_callback

    def handle_put(self, request: "Request", response: "Response"):
        return self.put_callback

    def handle_delete(self, request: "Request", response: "Response"):
        return self.delete_callback

    def get_callback(self, request: "Request", response: "Response"):
        import time
        time.sleep(5)
        response.payload = self.payload
        response.max_age = 20
        return self, response

    def post_callback(self, request: "Request", response: "Response"):
        import time
        time.sleep(5)
        self.payload = request.payload
        response.payload = "Resource changed through POST"
        return self, response

    def put_callback(self, request: "Request", response: "Response"):
        import time
        time.sleep(5)
        self.payload = request.payload
        response.payload = "Resource changed through PUT"
        return self, response

    def delete_callback(self, request: "Request", response: "Response"):
        import time
        time.sleep(5)
        response.payload = "Resource deleted"
        return True, response


class LargeResource(Resource):
    def __init__(self, name="LargeResource"):
        super().__init__(name)
        self.payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                       " Praesent tristique turpis dui, at ultricies lorem fermentum at. Vivamus sit amet ornare neque, " \
                       "a imperdiet nisl. Quisque a iaculis libero, id tempus lacus. Aenean convallis est non justo " \
                       "consectetur, a hendrerit enim consequat. In accumsan ante a egestas luctus. Etiam quis neque " \
                       "nec eros vestibulum faucibus. Nunc viverra ipsum lectus, vel scelerisque dui dictum a. Ut orci " \
                       "enim, ultrices a ultrices nec, pharetra in quam. Donec accumsan sit amet eros eget fermentum." \
                       "Vivamus ut odio ac odio malesuada accumsan. Aenean vehicula diam at tempus ornare. Phasellus " \
                       "dictum mauris a mi consequat, vitae mattis nulla fringilla. Ut laoreet tellus in nisl efficitur," \
                       " a luctus justo tempus. Fusce finibus libero eget velit finibus iaculis. Morbi rhoncus purus " \
                       "vel vestibulum ullamcorper. Sed ac metus in urna fermentum feugiat. Nulla nunc diam, sodales " \
                       "aliquam mi id, varius porta nisl. Praesent vel nibh ac turpis rutrum laoreet at non odio. " \
                       "Phasellus ut posuere mi. Suspendisse malesuada velit nec mauris convallis porta. Vivamus " \
                       "sed ultrices sapien, at cras amet."

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        return self, response


class LargeUpdateResource(Resource):
    def __init__(self, name="LargeUpdateResource"):
        super().__init__(name)
        self.payload = ""

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        return self, response

    async def handle_put(self, request: "Request", response: "Response"):
        self.payload = request.payload
        return self, response


class LargeCreateResource(Resource):
    def __init__(self, name="LargeCreateResource"):
        super().__init__(name)
        self.payload = ""

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        return self, response

    async def handle_post(self, request: "Request", response: "Response"):
        resource = LargeCreateResource(name="dynamically_created")
        resource.path = "/large-create/ps"
        resource.payload = request.payload
        if request.content_type is not None:
            resource.content_type = request.content_type
        response.location_path = resource.path
        return resource, response


class TestResource(Resource):
    def __init__(self, name="test"):
        super().__init__(name)
        self.payload = "Test"
        self.content_type = defines.ContentType.TEXT_PLAIN

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.content_type = self.content_type
        return self, response

    async def handle_delete(self, request: "Request", response: "Response"):
        return True, response

    async def handle_put(self, request: "Request", response: "Response"):
        self.payload = request.payload
        self.content_type = request.content_type
        return self, response

    async def handle_post(self, request: "Request", response: "Response"):
        if request.uri_query is not None:
            resource = TestResource(name="dynamically_created")
            resource.path = "/location1/location2/location3"
            resource.payload = request.payload
            if request.content_type is not None:
                resource.content_type = request.content_type
            response.location_path = resource.path
            return resource, response
        else:
            self.payload = request.payload
            self.content_type = request.content_type
            return self, response
        

class ComposedResource(Resource):
    def __init__(self, name="composed"):
        super().__init__(name)
        self.payload = "Composed"
        self.content_type = defines.ContentType.TEXT_PLAIN

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.content_type = self.content_type
        return self, response


class QueryResource(Resource):
    def __init__(self, name="query"):
        super().__init__(name)
        self.payload = "Query"
        self.content_type = defines.ContentType.TEXT_PLAIN

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        if request.uri_query is not None:
            for q in request.uri_query_list:
                k, v = utils.parse_uri_query(q)
                if k == "first" and v == "1":
                    response.payload += "1"
                if k == "second" and v == "2":
                    response.payload += "2"

        response.content_type = self.content_type
        return self, response


class LocationQueryResource(Resource):
    def __init__(self, name="test"):
        super().__init__(name)
        self.payload = "Test"
        self.content_type = defines.ContentType.TEXT_PLAIN

    async def handle_post(self, request: "Request", response: "Response"):
        resource = LocationQueryResource(name="dynamically_created")
        resource.path = "/location-query/location-query1"
        resource.payload = request.payload
        if request.content_type is not None:
            resource.content_type = request.content_type
        response.location_path = resource.path
        resource.location_query = "?first=1&second=2"
        return resource, response


class MultiFormatResource(Resource):
    def __init__(self, name="multi-format"):
        super().__init__(name)
        self.value = 1

    async def handle_get(self, request: "Request", response: "Response"):
        if request.accept == defines.ContentType.TEXT_PLAIN:
            response.payload = "{0}".format(self.value)
            response.content_type = defines.ContentType.TEXT_PLAIN
        elif request.accept == defines.ContentType.application_xml:
            response.payload = "<value>{0}</value>".format(self.value)
            response.content_type = defines.ContentType.application_xml
        return self, response


class ValidateResource(Resource):
    def __init__(self, name="validate"):
        super().__init__(name)
        self.payload = "Validate"
        self.__etag = 1
        self.etag = self.__etag.to_bytes(length=1, byteorder="big")

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.etag = self.etag
        return self, response

    async def handle_put(self, request: "Request", response: "Response"):
        self.payload = request.payload
        self.__etag += 1
        self.etag = self.__etag.to_bytes(length=1, byteorder="big")
        return self, response


class StorageResource(Resource):
    def __init__(self, name="StorageResource"):
        super().__init__(name, visible=True, observable=True, allow_children=ChildResource)
        self.payload = "Storage Resource for PUT, POST and DELETE"

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        return self, response

class ChildResource(Resource):
    def __init__(self, name="ChildResource"):
        super().__init__(name)
        self.payload = ""

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.content_type = self.content_type
        return self, response


class Type1Resource(Resource):
    def __init__(self, name="Type1Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type1"

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class Type2Resource(Resource):
    def __init__(self, name="Type2Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type2"

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupType1Resource(Resource):
    def __init__(self, name="GroupType1Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type1 Type2"

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupType2Resource(Resource):
    def __init__(self, name="GroupType2Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type2 Type3"

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupType3Resource(Resource):
    def __init__(self, name="GroupType3Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type1 Type3"

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupType4Resource(Resource):
    def __init__(self, name="GroupType4Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = ""

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupIf1Resource(Resource):
    def __init__(self, name="GroupIf1Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_if = "if1"

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupIf2Resource(Resource):
    def __init__(self, name="GroupIf2Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_if = "if2"

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupIf3Resource(Resource):
    def __init__(self, name="GroupIf3Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_if = "foo"

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupIf4Resource(Resource):
    def __init__(self, name="GroupIf4Resource"):
        super().__init__(name)
        self.payload = ""

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class SzResource(Resource):
    def __init__(self, name="SzResource"):
        super().__init__(name)
        self.payload = ""
        self.size = "10"

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class LinkResource(Resource):
    def __init__(self, name="LinkResource"):
        super().__init__(name)
        self.payload = ""

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class SlowResource(Resource):

    def __init__(self, name="Long"):
        super(SlowResource, self).__init__(name, visible=True, observable=True, allow_children=True)
        self.payload = "Long Time"

    def handle_get(self, request: "Request", response: "Response"):
        import time
        time.sleep(10)
        response.payload = self.payload
        return self, response


class ETAGResource(Resource):
    def __init__(self, name="ETag"):
        super(ETAGResource, self).__init__(name)
        self.count = 0
        self.payload = "ETag resource"
        self.etag = str(self.count)

    def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        return self, response

    def handle_post(self, request: "Request", response: "Response"):
        self.payload = request.payload
        self.count += 1
        self.etag = str(self.count)
        return self, response

    def handle_put(self, request: "Request", response: "Response"):
        self.payload = request.payload
        return self, response


class MultipleEncodingResource(Resource):
    def __init__(self, name="MultipleEncoding"):
        super(MultipleEncodingResource, self).__init__(name)
        self.value = 0
        self.content_type = [defines.ContentType.application_json, defines.ContentType.application_xml,
                             defines.ContentType.TEXT_PLAIN]

    def handle_get(self, request: "Request", response: "Response"):
        if request.accept == defines.ContentType.application_xml:
            response.payload = "<value>"+str(self.value)+"</value>"
            response.content_type = defines.ContentType.application_xml
        elif request.accept == defines.ContentType.application_json:
            response.payload = "{'value': '"+str(self.value)+"'}"
            response.content_type = defines.ContentType.application_json
        else:
            response.payload = str(self.value)
        return self, response

    def handle_put(self, request: "Request", response: "Response"):
        if request.content_type == defines.ContentType.application_json:
            import json
            value = json.loads(request.payload)
            self.value = value["value"]
        elif request.content_type is None or request.content_type == defines.ContentType.TEXT_PLAIN:
            self.value = int(request.payload.raw)
        else:
            response.code = defines.Code.NOT_ACCEPTABLE
        return self, response

    def handle_post(self, request: "Request", response: "Response"):
        self.value += 1
        return self, response


class ObserveResource(Resource):
    def __init__(self, name="ObserveResource"):
        super().__init__(name)
        self.value = 5
        self.period = 5
        self.loop = asyncio.get_event_loop()
        self.update_task = self.loop.create_task(self.update_value())
        self.content_type = None

    async def handle_get(self, request: "Request", response: "Response"):
        if self.content_type is None or self.content_type == defines.ContentType.TEXT_PLAIN:
            response.payload = "{0}".format(self.value)
        elif self.content_type == defines.ContentType.application_json:
            response.payload = "{ \"value\": " + str(self.value) + "}"
        return self, response

    async def handle_put(self, request: "Request", response: "Response"):
        if request.content_type == defines.ContentType.application_json:
            import json
            payload = json.loads(str(request.payload))
            self.value = int(payload["value"])
            self.content_type = defines.ContentType.application_json
        else:
            self.value = int(str(request.payload))
            self.content_type = None
        return self, response

    async def handle_delete(self, request: "Request", response: "Response"):
        return True, response

    async def update_value(self):
        while True:
            await asyncio.sleep(self.period)
            self.value += 1
            self.observe_count += 1
            await self.notify()


class LargeObserveResource(Resource):
    def __init__(self, name="LargeObserveResource"):
        super().__init__(name)
        self.period = 5
        self.loop = asyncio.get_event_loop()
        self.update_task = self.loop.create_task(self.update_value())
        self.payload = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sollicitudin fermentum ornare. " \
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
                       " Praesent tristique turpis dui, at ultricies lorem fermentum at. Vivamus sit amet ornare neque, " \
                       "a imperdiet nisl. Quisque a iaculis libero, id tempus lacus. Aenean convallis est non justo " \
                       "consectetur, a hendrerit enim consequat. In accumsan ante a egestas luctus. Etiam quis neque " \
                       "nec eros vestibulum faucibus. Nunc viverra ipsum lectus, vel scelerisque dui dictum a. Ut orci " \
                       "enim, ultrices a ultrices nec, pharetra in quam. Donec accumsan sit amet eros eget fermentum." \
                       "Vivamus ut odio ac odio malesuada accumsan. Aenean vehicula diam at tempus ornare. Phasellus " \
                       "dictum mauris a mi consequat, vitae mattis nulla fringilla. Ut laoreet tellus in nisl efficitur," \
                       " a luctus justo tempus. Fusce finibus libero eget velit finibus iaculis. Morbi rhoncus purus " \
                       "vel vestibulum ullamcorper. Sed ac metus in urna fermentum feugiat. Nulla nunc diam, sodales " \
                       "aliquam mi id, varius porta nisl. Praesent vel nibh ac turpis rutrum laoreet at non odio. " \
                       "Phasellus ut posuere mi. Suspendisse malesuada velit nec mauris convallis porta. Vivamus " \
                       "sed ultrices sapien, at cras amet."

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        return self, response

    async def update_value(self):
        while True:
            await asyncio.sleep(self.period)
            self.observe_count += 1
            await self.notify()


def usage():  # pragma: no cover
    print("server.py -i <ip address> -p <port>")


def main(argv):  # pragma: no cover
    ip, port = utils.parse_arguments(argv)

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)
    server = CoAPServer(ip, port, loop=loop)
    server.add_resource('basic/', BasicResource())
    server.add_resource('separate/', SeparateResource())
    server.add_resource('large/', LargeResource())
    server.add_resource('large-update/', LargeUpdateResource())
    server.add_resource('large-create/', LargeCreateResource())
    server.add_resource('slow/', SlowResource())
    server.add_resource('etag/', ETAGResource())
    server.add_resource('multiple/', MultipleEncodingResource())
    server.add_resource('obs/', ObserveResource())
    server.add_resource('obs-large/', LargeObserveResource())
    server.add_resource('test/', TestResource())
    server.add_resource('separate/', SeparateResource())
    server.add_resource('seg1/seg2/seg3/', ComposedResource())
    server.add_resource('query/', QueryResource())
    server.add_resource('location-query/', LocationQueryResource())
    server.add_resource('multi-format/', MultiFormatResource())
    server.add_resource('validate/', ValidateResource())
    server.add_resource('storage/', StorageResource())
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

    print(server.get_resources())

    try:
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(shutdown(loop, s, server)))
        loop.set_exception_handler(handle_exception)

        loop.create_task(server.create_server())

        loop.run_forever()

    finally:

        loop.close()


def handle_exception(loop, context):
    # context["message"] will always be there; but context["exception"] may not
    msg = context.get("exception", context["message"])
    logging.error(f"Caught exception: {msg}")
    logging.error(repr(context))


async def shutdown(loop, sig, server):
    logging.info(f"Received exit signal {sig.name}...")
    logging.info("Closing server")
    server.stop()
    tasks = [t for t in asyncio.Task.all_tasks() if t is not
             asyncio.Task.current_task()]

    [task.cancel() for task in tasks]
    logging.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
