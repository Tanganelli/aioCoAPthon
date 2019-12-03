from aiocoapthon.resources.resource import Resource


class Type1Resource(Resource):
    def __init__(self, name="Type1Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type1"


class Type2Resource(Resource):
    def __init__(self, name="Type2Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type2"


class GroupType1Resource(Resource):
    def __init__(self, name="GroupType1Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type1 Type2"


class GroupType2Resource(Resource):
    def __init__(self, name="GroupType2Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type2 Type3"


class GroupType3Resource(Resource):
    def __init__(self, name="GroupType3Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = "Type1 Type3"


class GroupType4Resource(Resource):
    def __init__(self, name="GroupType4Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_rt = ""


class GroupIf1Resource(Resource):
    def __init__(self, name="GroupIf1Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_if = "if1"


class GroupIf2Resource(Resource):
    def __init__(self, name="GroupIf2Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_if = "if2"


class GroupIf3Resource(Resource):
    def __init__(self, name="GroupIf3Resource"):
        super().__init__(name)
        self.payload = ""
        self.core_if = "foo"


class GroupIf4Resource(Resource):
    def __init__(self, name="GroupIf4Resource"):
        super().__init__(name)
        self.payload = ""


class SzResource(Resource):
    def __init__(self, name="SzResource"):
        super().__init__(name)
        self.payload = ""
        self.size = "10"


class LinkResource(Resource):
    def __init__(self, name="LinkResource"):
        super().__init__(name)
        self.payload = ""


