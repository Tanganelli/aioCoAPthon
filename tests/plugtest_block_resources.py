from typing import Union, Tuple, Callable

from resources.resource import Resource


class LargeResource(Resource):  # pragma: no cover
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

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        return self, response


class LargeUpdateResource(Resource):
    def __init__(self, name="LargeUpdateResource"):
        super().__init__(name)
        self.payload = ""

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
        response.payload = self.payload
        return self, response

    async def handle_put(self, request: "Request", response: "Response"):
        self.payload = request.payload
        return self, response


class LargeCreateResource(Resource):
    def __init__(self, name="LargeCreateResource"):
        super().__init__(name)
        self.payload = ""

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:
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

