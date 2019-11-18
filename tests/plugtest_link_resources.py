from typing import Union, Tuple, Callable

from resources.resource import Resource


class Type1Resource(Resource):
    def __init__(self, name="Type1Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type1"

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class Type2Resource(Resource):
    def __init__(self, name="Type2Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type2"

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupType1Resource(Resource):
    def __init__(self, name="GroupType1Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type1 Type2"

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupType2Resource(Resource):
    def __init__(self, name="GroupType2Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type2 Type3"

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupType3Resource(Resource):
    def __init__(self, name="GroupType3Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type1 Type3"

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupType4Resource(Resource):
    def __init__(self, name="GroupType4Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = ""

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupIf1Resource(Resource):
    def __init__(self, name="GroupIf1Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_if = "if1"

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupIf2Resource(Resource):
    def __init__(self, name="GroupIf2Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_if = "if2"

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupIf3Resource(Resource):
    def __init__(self, name="GroupIf3Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_if = "foo"

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class GroupIf4Resource(Resource):
    def __init__(self, name="GroupIf4Resource"):
        super().__init__(name)
        self.payload = ""

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class SzResource(Resource):
    def __init__(self, name="SzResource"):
        super().__init__(name)
        self.payload = ""
        self.size = "10"

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response


class LinkResource(Resource):
    def __init__(self, name="LinkResource"):
        super().__init__(name)
        self.payload = ""

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        response.core_ct = self.core_ct
        return self, response
