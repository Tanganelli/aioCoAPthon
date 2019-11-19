from typing import Union, Tuple, Callable

from utilities import defines
from utilities import utils
from resources.resource import Resource


class TestResource(Resource):
    def __init__(self, name="test"):
        super().__init__(name)
        self.payload = "Test"
        self.content_type = defines.ContentType.TEXT_PLAIN

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
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


class SeparateResource(Resource):

    def __init__(self, name="separate"):
        super().__init__(name)
        self.payload = "Separate"
        self.content_type = defines.ContentType.TEXT_PLAIN

    def handle_get(self, request: "Request", response: "Response"):
        return self.get_callback

    def get_callback(self, request: "Request", response: "Response"):
        import time
        time.sleep(1)
        response.payload = self.payload
        response.content_type = self.content_type
        return self, response

    def handle_post(self, request: "Request", response: "Response"):
        return self.post_callback

    def handle_put(self, request: "Request", response: "Response"):
        return self.put_callback

    def handle_delete(self, request: "Request", response: "Response"):
        return self.delete_callback

    def post_callback(self, request: "Request", response: "Response"):
        import time
        time.sleep(1)
        self.payload = request.payload
        response.payload = "Resource changed through POST"
        return self, response

    def put_callback(self, request: "Request", response: "Response"):
        import time
        time.sleep(1)
        self.payload = request.payload
        response.payload = "Resource changed through PUT"
        return self, response

    def delete_callback(self, request: "Request", response: "Response"):
        import time
        time.sleep(1)
        response.payload = "Resource deleted"
        return True, response


class ComposedResource(Resource):
    def __init__(self, name="composed"):
        super().__init__(name)
        self.payload = "Composed"
        self.content_type = defines.ContentType.TEXT_PLAIN

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.content_type = self.content_type
        return self, response


class QueryResource(Resource):
    def __init__(self, name="query"):
        super().__init__(name)
        self.payload = "Query"
        self.content_type = defines.ContentType.TEXT_PLAIN

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
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
        response.location_query = "?first=1&second=2"
        return resource, response


class MultiFormatResource(Resource):
    def __init__(self, name="multi-format"):
        super().__init__(name)
        self.value = 1

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
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

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
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


class ChildResource(Resource):
    def __init__(self, name="ChildResource"):
        super().__init__(name)
        self.payload = ""

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.content_type = self.content_type
        return self, response

