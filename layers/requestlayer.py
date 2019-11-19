import logging

from utilities import defines, utils
from utilities.transaction import Transaction
from layers.resourcelayer import ResourceLayer
from messages.response import Response
from resources.resource import Resource

__author__ = 'Giacomo Tanganelli'

logger = logging.getLogger(__name__)


class RequestLayer(object):
    """
    Class to handle the Request/Response layer
    """

    def __init__(self):
        # Resource directory
        root = Resource('root', visible=False, observable=False, allow_children=None)
        root.path = '/'
        self._root = utils.Tree()
        self._root["/"] = root
        self._resourceLayer = ResourceLayer()

    def add_resource(self, path, resource):
        """
        Helper function to add resources to the resource directory during server initialization.

        :param path: the path for the new created resource
        :type resource: Resource
        :param resource: the resource to be added
        """

        assert isinstance(resource, Resource)
        path = path.strip("/")
        path = "/" + path
        try:
            self._root[path]
        except KeyError:
            resource.path = path
            self._root[path] = resource
            return True
        return False  # pragma: no cover

    # def remove_resource(self, path):
    #     """
    #     Helper function to remove resources.
    #
    #     :param path: the path for the unwanted resource
    #     :rtype : the removed object
    #     """
    #
    #     path = path.strip("/")
    #     path = "/" + path
    #     try:
    #         res = self._root[path]
    #     except KeyError:
    #         return False
    #     if res is not None:
    #         del self._root[path]
    #     return True
    #
    # def get_resources(self, prefix=None):
    #     lst = self._root.dump()
    #     if prefix is None:
    #         return lst
    #     else:
    #         ret = []
    #         for uri in lst:
    #             assert isinstance(uri, str)
    #             if uri.startswith(prefix):
    #                 ret.append(uri)
    #         return ret

    async def receive_request(self, transaction: Transaction) -> Transaction:
        """
        Handle request and execute the requested method

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the edited transaction with the response to the request
        """
        method = transaction.request.code
        if method == defines.Code.GET:
            transaction = await self._handle_get(transaction)
        elif method == defines.Code.POST:
            transaction = await self._handle_post(transaction)
        elif method == defines.Code.PUT:
            transaction = await self._handle_put(transaction)
        elif method == defines.Code.DELETE:
            transaction = await self._handle_delete(transaction)
        return transaction

    async def _handle_get(self, transaction: Transaction) -> Transaction:
        """
        Handle GET requests

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the edited transaction with the response to the request
        """
        path = str("/" + transaction.request.uri_path)
        transaction.response = Response()
        transaction.response.destination = transaction.request.source
        transaction.response.token = transaction.request.token
        if path == defines.DISCOVERY_URL:
            resources = []
            for i in self._root.dump():
                if i == "/":
                    continue
                resource = self._root[i]
                if resource.visible:
                    resources.append(resource)

            transaction = await self._resourceLayer.discover(transaction, resources)
        else:
            try:
                resource = self._root[path]
            except KeyError:
                resource = None
            if resource is None or path == '/':
                # Not Found
                transaction.response.code = defines.Code.NOT_FOUND
            else:
                transaction = await self._resourceLayer.get_resource(transaction, resource)
        return transaction

    async def _handle_put(self, transaction: Transaction) -> Transaction:
        """
        Handle PUT requests

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the edited transaction with the response to the request
        """
        path = str("/" + transaction.request.uri_path)
        transaction.response = Response()
        transaction.response.destination = transaction.request.source
        transaction.response.token = transaction.request.token
        try:
            resource = self._root[path]

            # If-None-Match
            if transaction.request.if_none_match:
                transaction.response.code = defines.Code.PRECONDITION_FAILED
                return transaction

        except KeyError:
            # If-Match empty string
            if transaction.request.if_match:
                if "".encode("utf-8") in transaction.request.if_match:
                    transaction.response.code = defines.Code.PRECONDITION_FAILED
                    return transaction

            lst = self._root.get_ascending(path)

            max_len = 0
            imax = None

            for i in lst:
                if len(i.path) > max_len:
                    imax = i
                    max_len = len(i.path)

            parent_resource = imax
            if parent_resource.allow_children is not None:
                resource = parent_resource.allow_children()
                resource.path = path
                transaction.resource = resource
                self._root[resource.path] = transaction.resource
                transaction.response.code = defines.Code.CREATED
            else:
                transaction.response.code = defines.Code.NOT_FOUND
        else:
            transaction = await self._resourceLayer.put_resource(transaction, resource)

        return transaction

    async def _handle_post(self, transaction: Transaction) -> Transaction:
        """
        Handle POST requests

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the edited transaction with the response to the request
        """
        path = str("/" + transaction.request.uri_path)
        transaction.response = Response()
        transaction.response.destination = transaction.request.source
        transaction.response.token = transaction.request.token

        try:
            resource = self._root[path]
            # If-None-Match
            if transaction.request.if_none_match:
                transaction.response.code = defines.Code.PRECONDITION_FAILED
                return transaction

        except KeyError:
            transaction.response.code = defines.Code.NOT_FOUND
        else:
            # post
            transaction = await self._resourceLayer.post_resource(transaction, resource)

            if transaction.resource is not None and resource.__repr__() != transaction.resource.__repr__():
                # new resource created by the method
                try:
                    resource = self._root[transaction.resource.path]
                    # If-None-Match
                    if transaction.request.if_none_match:
                        transaction.response.code = defines.Code.PRECONDITION_FAILED
                        transaction.resource = None
                        transaction.response.clear_options()
                        transaction.response.payload = None
                        return transaction
                    self._root[transaction.resource.path] = transaction.resource
                except KeyError:
                    # If-Match empty string
                    if transaction.request.if_match:
                        if "".encode("utf-8") in transaction.request.if_match:
                            transaction.response.code = defines.Code.PRECONDITION_FAILED
                            transaction.resource = None
                            transaction.response.clear_options()
                            transaction.response.payload = None
                            return transaction

                    self._root[transaction.resource.path] = transaction.resource
                    transaction.response.code = defines.Code.CREATED

                except AttributeError:
                    transaction.response.code = defines.Code.BAD_REQUEST
                    transaction.response.clear_options()
                    transaction.response.payload = "A resource should be specified."

        return transaction

    async def _handle_delete(self, transaction: Transaction) -> Transaction:
        """
        Handle DELETE requests

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the edited transaction with the response to the request
        """
        path = str("/" + transaction.request.uri_path)
        transaction.response = Response()
        transaction.response.destination = transaction.request.source
        transaction.response.token = transaction.request.token
        try:
            resource = self._root[path]
        except KeyError:
            transaction.response.code = defines.Code.NOT_FOUND
        else:
            # Delete
            transaction.resource = resource
            transaction = await self._resourceLayer.delete_resource(transaction, resource)
            if transaction.resource.deleted:
                del self._root[path]
        return transaction

