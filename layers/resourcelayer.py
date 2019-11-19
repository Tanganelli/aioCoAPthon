import asyncio
import functools
import logging
import concurrent.futures
from typing import Callable, List

from utilities import errors, defines
from messages.response import Response
from messages.request import Request
from resources.resource import Resource
from utilities.transaction import Transaction

__author__ = 'Giacomo Tanganelli'

logger = logging.getLogger(__name__)


class ResourceLayer(object):
    """
    Handles the Resources.
    """

    @staticmethod
    async def call_method(method: Callable, request: Request, response: Response):

        if not asyncio.iscoroutinefunction(method):
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                ret = await loop.run_in_executor(pool, functools.partial(method, request=request,
                                                                         response=response))
        else:
            ret = await method(request=request, response=response)
        return ret

    @staticmethod
    async def discover(transaction: Transaction, resources: List[Resource]) -> Transaction:
        """
        Render a GET request to the .well-know/core link.

        :param resources:
        :param transaction: the transaction
        :return: the transaction
        """
        transaction.response.code = defines.Code.CONTENT
        payload = ""
        for resource in resources:
            ret = ResourceLayer.valid(transaction.request.uri_query, resource.attributes, resource.path)
            if ret:
                payload += ResourceLayer.corelinkformat(resource)

        transaction.response.payload = payload[:-1]
        transaction.response.content_type = defines.ContentType.application_link_format
        return transaction

    @classmethod
    async def get_resource(cls, transaction: Transaction, resource: Resource) -> Transaction:
        """
        Render a GET request.

        :param resource:
        :param transaction: the transaction
        :return: the transaction
        """

        transaction.resource = resource
        # If-Match
        if transaction.request.if_match:
            if None not in transaction.request.if_match and transaction.resource.etag \
                    not in transaction.request.if_match:
                transaction.response.code = defines.Code.PRECONDITION_FAILED
                return transaction

        method = getattr(resource, "handle_get", None)
        try:
            ret = await cls.call_method(method, request=transaction.request, response=transaction.response)

            if isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[1], Response) \
                    and isinstance(ret[0], Resource):
                resource_rep, response = ret

            elif isinstance(ret, Callable):
                if not transaction.request.acknowledged:
                    transaction.send_separate.set()
                    await transaction.separate_task
                callback = ret

                ret = await cls.call_method(callback, request=transaction.request, response=transaction.response)
                resource_rep, response = ret

            else:  # pragma: no cover
                raise errors.InternalError("Resource handler is not correctly implemented",
                                           defines.Code.INTERNAL_SERVER_ERROR, transaction=transaction,
                                           related=defines.MessageRelated.REQUEST)

            # Accept
            if transaction.request.accept is not None and response.content_type is not None \
                    and transaction.request.accept != response.content_type:
                transaction.response.code = defines.Code.NOT_ACCEPTABLE
                transaction.response.clear_options()
                transaction.response.payload = "Request representation is not acceptable."
                return transaction

            transaction.resource, transaction.response = resource_rep, response
            if transaction.response.code is None or transaction.response.code == defines.Code.EMPTY:
                if resource.etag in transaction.request.etag:
                    transaction.response.code = defines.Code.VALID
                    transaction.response.payload = None
                else:
                    transaction.response.code = defines.Code.CONTENT

            return transaction

        except NotImplementedError:  # pragma: no cover
            transaction.response.code = defines.Code.METHOD_NOT_ALLOWED
            transaction.response.clear_options()
            transaction.response.payload = "GET method is not allowed."
            return transaction
        except Exception:  # pragma: no cover
            raise errors.InternalError("Resource handler is not correctly implemented",
                                       defines.Code.INTERNAL_SERVER_ERROR, transaction=transaction,
                                       related=defines.MessageRelated.REQUEST)

    @classmethod
    async def put_resource(cls, transaction: Transaction, resource: Resource) -> Transaction:
        """
        Render a PUT on a resource.

        :param transaction: the transaction
        :param resource: the resource
        :return: the response
        """
        # If-Match
        if transaction.request.if_match:
            if None not in transaction.request.if_match and resource.etag \
                    not in transaction.request.if_match:
                transaction.response.code = defines.Code.PRECONDITION_FAILED
                return transaction

        method = getattr(resource, "handle_put", None)
        try:
            ret = await cls.call_method(method, request=transaction.request, response=transaction.response)

            if isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[1], Response) \
                    and isinstance(ret[0], Resource):
                resource_rep, response = ret

            elif isinstance(ret, Callable):
                if not transaction.request.acknowledged:
                    transaction.send_separate.set()
                    await transaction.separate_task
                callback = ret
                ret = await cls.call_method(callback, request=transaction.request, response=transaction.response)
                resource_rep, response = ret
            else:  # pragma: no cover
                raise errors.InternalError("Resource handler is not correctly implemented",
                                           defines.Code.INTERNAL_SERVER_ERROR, transaction=transaction)

            transaction.resource, transaction.response = resource_rep, response
            transaction.resource.changed = True
            transaction.resource.observe_count += 1

            if transaction.response.code is None or transaction.response.code == defines.Code.EMPTY:
                transaction.response.code = defines.Code.CHANGED

        except NotImplementedError:  # pragma: no cover
            transaction.response.code = defines.Code.METHOD_NOT_ALLOWED
            transaction.response.clear_options()
            transaction.response.payload = "PUT method is not allowed."
        except Exception:  # pragma: no cover
            raise errors.InternalError("Resource handler is not correctly implemented",
                                       defines.Code.INTERNAL_SERVER_ERROR, transaction=transaction,
                                       related=defines.MessageRelated.REQUEST)
        return transaction

    @classmethod
    async def post_resource(cls, transaction: Transaction, resource: Resource) -> Transaction:
        """
        Render a POST request.

        :param resource: the resource
        :param transaction: the transaction
        :return: the response
        """
        # If-Match
        if transaction.request.if_match:
            if None not in transaction.request.if_match and resource.etag \
                    not in transaction.request.if_match:
                transaction.response.code = defines.Code.PRECONDITION_FAILED
                return transaction

        method = getattr(resource, "handle_post", None)
        try:
            ret = await cls.call_method(method, request=transaction.request, response=transaction.response)

            if isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[1], Response) \
                    and isinstance(ret[0], Resource):
                resource_rep, response = ret

            elif isinstance(ret, Callable):
                if not transaction.request.acknowledged:
                    transaction.send_separate.set()
                    await transaction.separate_task
                callback = ret
                ret = await cls.call_method(callback, request=transaction.request, response=transaction.response)
                resource_rep, response = ret
            else:  # pragma: no cover
                raise errors.InternalError("Resource handler is not correctly implemented",
                                           defines.Code.INTERNAL_SERVER_ERROR, transaction=transaction)

            transaction.resource, transaction.response = resource_rep, response
            transaction.resource.changed = True
            transaction.resource.observe_count += 1

            if transaction.response.code is None or transaction.response.code == defines.Code.EMPTY:
                transaction.response.code = defines.Code.CHANGED

        except NotImplementedError:  # pragma: no cover
            transaction.response.code = defines.Code.METHOD_NOT_ALLOWED
            transaction.response.clear_options()
            transaction.response.payload = "POST method is not allowed."
        except Exception:  # pragma: no cover
            raise errors.InternalError("Resource handler is not correctly implemented",
                                       defines.Code.INTERNAL_SERVER_ERROR, transaction=transaction,
                                       related=defines.MessageRelated.REQUEST)

        return transaction

    @classmethod
    async def delete_resource(cls, transaction: Transaction, resource: Resource) -> Transaction:
        """
        Render a DELETE request.

        :param transaction: the transaction
        :param resource: the resource
        :return: the response
        """

        transaction.resource = resource
        # If-Match
        if transaction.request.if_match:
            if None not in transaction.request.if_match and transaction.resource.etag \
                    not in transaction.request.if_match:
                transaction.response.code = defines.Code.PRECONDITION_FAILED
                return transaction

        method = getattr(resource, "handle_delete", None)
        try:
            ret = await cls.call_method(method, request=transaction.request, response=transaction.response)

            if isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[1], Response) \
                    and isinstance(ret[0], bool):
                deleted, response = ret

            elif isinstance(ret, Callable):
                if not transaction.request.acknowledged:
                    transaction.send_separate.set()
                    await transaction.separate_task
                callback = ret
                ret = await cls.call_method(callback, request=transaction.request, response=transaction.response)
                deleted, response = ret
            else:  # pragma: no cover
                raise errors.InternalError("Resource handler is not correctly implemented",
                                           defines.Code.INTERNAL_SERVER_ERROR, transaction=transaction)

            transaction.response = response
            transaction.resource = resource
            if deleted:
                transaction.resource.deleted = True
                transaction.resource.observe_count += 1

            if transaction.response.code is None or transaction.response.code == defines.Code.EMPTY:
                transaction.response.code = defines.Code.DELETED

            return transaction

        except NotImplementedError:  # pragma: no cover
            transaction.response.code = defines.Code.METHOD_NOT_ALLOWED
            transaction.response.clear_options()
            transaction.response.payload = "GET method is not allowed."
            return transaction
        except Exception:  # pragma: no cover
            raise errors.InternalError("Resource handler is not correctly implemented",
                                       defines.Code.INTERNAL_SERVER_ERROR, transaction=transaction,
                                       related=defines.MessageRelated.REQUEST)

    @staticmethod
    def valid(query, attributes, path):
        if query is None:
            return True
        query = query.strip("?")
        query = query.split("&")
        for q in query:
            q = str(q)
            assert(isinstance(q, str))
            tmp = q.split("=")
            k = tmp[0]
            if k not in attributes and k != "href":
                return False
            v = None
            pos_star = -1
            if len(tmp) > 1:
                v = tmp[1]
                try:
                    pos_star = v.index("*")
                except ValueError:
                    pos_star = -1
                if pos_star == 0:
                    continue
            if k == "href":
                if pos_star == -1 and path == v:
                    return True
                else:
                    if pos_star != -1 and path.startswith(v[:pos_star]):
                        return True
                    else:
                        return False
            if v is None:
                continue
            tmp = attributes[k].split(" ")
            found = False
            for i in tmp:
                if pos_star == -1:
                    if v == i:
                        found = True
                        break
                else:
                    if i.startswith(v[:pos_star]):
                        found = True
                        break
            if not found:
                return False
        return True

    @staticmethod
    def corelinkformat(resource):
        """
        Return a formatted string representation of the corelinkformat in the tree.

        :return: the string
        """
        msg = ["<{0}>;".format(resource.path)]
        assert(isinstance(resource, Resource))
        keys = sorted(list(resource.attributes.keys()))
        for k in keys:
            v = resource.attributes[k]
            if v is not None and v != "":
                if isinstance(v, str):
                    tmp = v.split(" ")
                    if len(tmp) == 1:
                        v = tmp[0]
                    else:
                        v = tmp
                if isinstance(v, list):
                    lst = ""
                    for vd in v:
                        lst += "{0} ".format(vd)
                    msg.append("{0}=\"{1}\",".format(k, lst[:-1]))
                else:
                    v = "\"{0}\"".format(v)
                    msg.append("{0}={1},".format(k, v))
            else:
                msg.append("{0},".format(k))
        return "".join(msg)
