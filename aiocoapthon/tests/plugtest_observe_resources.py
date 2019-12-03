import asyncio

from aiocoapthon.utilities import defines
from aiocoapthon.resources.resource import Resource


class ObserveResource(Resource):
    def __init__(self, name="ObserveResource"):
        super().__init__(name)
        self.value = 5
        self.period = 5
        self.loop = asyncio.get_event_loop()
        self.update_task = self.loop.create_task(self.update_value())

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


class NotObservableResource(Resource):
    def __init__(self, name="test"):
        super().__init__(name, observable=False)
        self.payload = "NotObservable"
        self.content_type = defines.ContentType.TEXT_PLAIN

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        return self, response


class StableResource(Resource):
    def __init__(self, name="stable"):
        super().__init__(name)
        self.payload = "Stable"
        self.content_type = defines.ContentType.TEXT_PLAIN

    async def handle_get(self, request: "Request", response: "Response"):
        response.payload = self.payload
        response.max_age = 20
        return self, response
