from typing import Optional, Union, List, Tuple, Callable

from utilities import defines
from utilities import utils

__author__ = 'Giacomo Tanganelli'


class Resource(object):
    """
    The Resource class. Represents the base class for all resources.
    """

    def __init__(self, name, visible=True, observable=True, allow_children=None):
        """
        Initialize a new Resource.

        :param name: the name of the resource.
        :param visible: if the resource is visible
        :param observable: if the resource is observable
        """
        # The attributes of this resource.
        self._attributes = {}

        # The resource name.
        self.name = name

        # The resource path.
        self._path = None

        # Indicates whether this resource is visible to clients.
        self._visible = visible

        self._allow_children = allow_children

        # Indicates whether this resource is observable by clients.
        self._observable = observable
        if self._observable:
            self._attributes["obs"] = ""

        self._observe_count = 2

        self._payload = utils.CoAPPayload()

        self._content_type = None

        self._etag = None

        self._location_query = []

        self._deleted = False

        self._changed = False

        self.notify_queue = None

    async def notify(self):
        if self.notify_queue is not None:
            await self.notify_queue.put(self)

    @property
    def deleted(self) -> bool:
        """
        Check if the resource has been deleted. For observing purpose.

        :rtype: bool
        :return: True, if deleted
        """
        return self._deleted

    @deleted.setter
    def deleted(self, b: bool):
        """
        Set the deleted parameter. For observing purpose.

        :type b: bool
        :param b: True, if deleted
        """
        self._deleted = b

    @property
    def changed(self) -> bool:
        """
        Check if the resource has been changed. For observing purpose.

        :rtype: bool
        :return: True, if changed
        """
        return self._changed

    @changed.setter
    def changed(self, b: bool):
        """
        Set the changed parameter. For observing purpose.

        :type b: bool
        :param b: True, if changed
        """
        self._changed = b

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, v: str):
        path = v.strip("/")
        self._path = "/" + path

    @property
    def etag(self) -> Optional[bytes]:
        """
        Get the last valid ETag of the resource.

        :return: the last ETag value or None if the resource doesn't have any ETag
        """
        return self._etag

    @etag.setter
    def etag(self, etag: Union[bytes, str]):
        """
        Set the ETag of the resource.

        :param etag: the ETag
        """
        if isinstance(etag, str):
            etag = etag.encode("utf-8")
        self._etag = etag

    @property
    def location_query(self) -> List[str]:
        """
        Get the Location-Query of a resource.

        :return: the Location-Query
        """
        return self._location_query

    @location_query.setter
    def location_query(self, lq: List[str]):
        """
        Set the Location-Query.

        :param lq: the Location-Query
        """
        self._location_query = lq

    @location_query.deleter
    def location_query(self):
        """
        Delete the Location-Query.

        """
        self._location_query = []

    @property
    def attributes(self) -> dict:
        """
        Get the CoRE Link Format attribute of the resource.

        :return: the attribute of the resource
        """
        return self._attributes

    @attributes.setter
    def attributes(self, att: dict):
        # TODO assert
        """
        Set the CoRE Link Format attribute of the resource.

        :param att: the attributes
        """
        self._attributes = att

    @property
    def visible(self) -> bool:
        """
        Get if the resource is visible.

        :return: True, if visible
        """
        return self._visible

    @property
    def observable(self) -> bool:
        """
        Get if the resource is observable.

        :return: True, if observable
        """
        return self._observable

    @property
    def allow_children(self):
        """
        Get if the resource allow children.

        :return: True, if allow children
        """
        return self._allow_children

    @property
    def observe_count(self) -> int:
        """
        Get the Observe counter.

        :return: the Observe counter value
        """
        return self._observe_count

    @observe_count.setter
    def observe_count(self, v: int):
        """
        Set the Observe counter.

        :param v: the Observe counter value
        """
        assert isinstance(v, int)
        self._observe_count = (v % defines.MAX_OBSERVE_COUNT)
        if self._observe_count == 0 and v != 0:
            self._observe_count += 2
        elif self._observe_count == 1 and v != 1:
            self._observe_count += 1

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, v: defines.ContentType):
        self._content_type = v

    @property
    def core_ct(self) -> str:  # pragma: no cover
        """
        Get the CoRE Link Format ct attribute of the resource.

        :return: the CoRE Link Format ct attribute
        """
        value = ""
        lst = self._attributes.get("ct")
        if lst is not None and len(lst) > 0:
            value = "ct="
            for v in lst:
                value += str(v) + " "
        if len(value) > 0:
            value = value[:-1]
        return value

    @core_ct.setter
    def core_ct(self, lst: Union[None, str, defines.ContentType, List[str],
                                 List[defines.ContentType]]):  # pragma: no cover
        """
        Set the CoRE Link Format ct attribute of the resource.

        :param lst: the list of CoRE Link Format ct attribute of the resource
        """
        try:
            del self._attributes["ct"]
        except KeyError:
            pass
        if lst is not None:
            if isinstance(lst, str) or isinstance(lst, defines.ContentType):
                self.add_content_type(lst)
            elif isinstance(lst, list):
                for ct in lst:
                    self.add_content_type(ct)

    def add_content_type(self, ct: Union[str, defines.ContentType]):  # pragma: no cover
        """
        Add a CoRE Link Format ct attribute to the resource.

        :param ct: the CoRE Link Format ct attribute
        """
        lst = self._attributes.get("ct")
        if lst is None:
            lst = []
        if isinstance(ct, str):
            ct = defines.ContentType(lst)
        lst.append(ct)
        self._attributes["ct"] = lst

    @property
    def core_rt(self) -> str:  # pragma: no cover
        """
        Get the CoRE Link Format rt attribute of the resource.

        :return: the CoRE Link Format rt attribute
        """
        value = "rt="
        lst = self._attributes.get("rt")
        if lst is None:
            value = ""
        else:
            value += "\"" + str(lst) + "\""
        return value

    @core_rt.setter
    def core_rt(self, rt: str):  # pragma: no cover
        """
        Set the CoRE Link Format rt attribute of the resource.

        :param rt: the CoRE Link Format rt attribute
        """
        if not isinstance(rt, str):
            rt = str(rt)
        self._attributes["rt"] = rt

    @property
    def core_if(self) -> str:  # pragma: no cover
        """
        Get the CoRE Link Format if attribute of the resource.

        :return: the CoRE Link Format if attribute
        """
        value = "if="
        lst = self._attributes.get("if")
        if lst is None:
            value = ""
        else:
            value += "\"" + str(lst) + "\""
        return value

    @core_if.setter
    def core_if(self, ift: str):  # pragma: no cover
        """
        Set the CoRE Link Format if attribute of the resource.

        :param ift: the CoRE Link Format if attribute
        """
        if not isinstance(ift, str):
            ift = str(ift)
        self._attributes["if"] = ift

    @property
    def size(self) -> str:  # pragma: no cover
        """
        Get the CoRE Link Format sz attribute of the resource.

        :return: the CoRE Link Format if attribute
        """
        value = "sz="
        lst = self._attributes.get("sz")
        if lst is None:
            value = ""
        else:
            value += "\"" + str(lst) + "\""
        return value

    @size.setter
    def size(self, ift: str):  # pragma: no cover
        """
        Set the CoRE Link Format sz attribute of the resource.

        :param ift: the CoRE Link Format if attribute
        """
        if not isinstance(ift, str):
            ift = str(ift)
        self._attributes["sz"] = ift

    @property
    def core_obs(self) -> str:  # pragma: no cover
        """
        Get the CoRE Link Format obs attribute of the resource.

        :return: the CoRE Link Format obs attribute
        """
        if self._observable:
            return "obs"

    @property
    def payload(self):
        """
        Get the payload of the resource

        :return: the payload.
        """
        return self._payload

    @payload.setter
    def payload(self, p: bytes):
        """
        Set the payload of the resource.

        :param p: the new payload
        """
        if isinstance(p, str):
            p = p.encode("utf-8")
        elif isinstance(p, utils.CoAPPayload):
            p = p.raw
        self._payload.payload = p

    async def handle_get(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:  # pragma: no cover
        """
        Method to be redefined to render a GET request on the resource.

        :param response: the response
        :param request: the request
        :return: a tuple with (the resource, the response) or a callback
        """
        raise NotImplementedError

    async def handle_put(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                  Callable]:  # pragma: no cover
        """
        Method to be redefined to render a PUTT request on the resource.

        :param response: the partially filled response
        :param request: the request
        :return: a tuple with (the resource, the response) or a callback
        """
        raise NotImplementedError

    async def handle_post(self, request: "Request", response: "Response") -> Union[Tuple["Resource", "Response"],
                                                                                   Callable]:  # pragma: no cover
        """
        Method to be redefined to render a POST request on the resource.

        :param response: the partially filled response
        :param request: the request
        :return: a tuple with (the resource, the response) or a callback
        """
        raise NotImplementedError

    async def handle_delete(self, request: "Request", response: "Response") -> Union[Tuple[bool, "Response"],
                                                                                     Callable]:  # pragma: no cover
        """
        Method to be redefined to render a DELETE request on the resource.

        :param response: the partially filled response
        :param request: the request
        :return: a tuple with a boolean and the response or a callback
        """
        raise NotImplementedError
