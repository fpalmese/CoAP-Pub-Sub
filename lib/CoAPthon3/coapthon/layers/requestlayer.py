from coapthon.messages.response import Response
from coapthon.layers.observelayer import ObserveItem
from coapthon import defines
import time
__author__ = 'Giacomo Tanganelli'


class RequestLayer(object):
    """
    Class to handle the Request/Response layer
    """
    def __init__(self, server):
        self._server = server

    def receive_request(self, transaction):
        """
        Handle the request and execute the requested method

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the edited transaction with the response to the request
        """
        method = transaction.request.code
        if method == defines.Codes.GET.number:
            transaction = self._handle_get(transaction)
        elif method == defines.Codes.POST.number:
            transaction = self._handle_post(transaction)
        elif method == defines.Codes.PUT.number:
            transaction = self._handle_put(transaction)
        elif method == defines.Codes.DELETE.number:
            transaction = self._handle_delete(transaction)
        else:
            transaction.response = None
        return transaction

    def send_request(self, request):
        """
         Dummy function. Used to not break the layered architecture.

        :type request: Request
        :param request: the request
        :return: the request unmodified
        """
        return request

    def _handle_get(self, transaction):
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
        if path== "/" or path=="/ps":
            transaction.response.code = defines.Codes.METHOD_NOT_ALLOWED.number
            return transaction
        elif path == defines.DISCOVERY_URL:
            return self._server.resourceLayer.discover(transaction)
        else:
            try:
                resource = self._server.root[path]
            except KeyError:
                resource = None
            if resource is None:
                # Not Found
                transaction.response.code = defines.Codes.NOT_FOUND.number
                transaction.response.payload = path+ " NOT FOUND"
                return transaction
            transaction.resource = resource
            if(transaction.request.uri_query is not None and transaction.request.uri_query!=""):
                return self._server.resourceLayer.discover_subtopics(transaction)
            transaction = self._server.resourceLayer.get_resource(transaction)
            """
                BLOCKING READ HERE
            """
            if transaction.response.payload is None or transaction.response.payload == "":
                transaction.response.code = defines.Codes.NO_CONTENT.number
                [host,port] = transaction.request.source
                key = hash(str(host)+str(port))
                if key in self._server._observeLayer._readers[resource.name]:
                    allowed = True
                else:
                    allowed = False
                self._server._observeLayer._readers[resource.name][key] = ObserveItem(time.time(), 0, allowed, transaction)
                return transaction

        return transaction

    def _handle_put(self, transaction):
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
        if path== "/":
            transaction.response.code = defines.Codes.FORBIDDEN.number
            return transaction
        return self._server.resourceLayer.update_resource(transaction)

    def _handle_post(self, transaction):
        """
        Handle POST requests

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the edited transaction with the response to the request
        """
        path = str("/"+transaction.request.uri_path)
        transaction.response = Response()
        transaction.response.destination = transaction.request.source
        transaction.response.token = transaction.request.token
        if path== "/":
            transaction.response.code = defines.Codes.FORBIDDEN.number
            return transaction
        # Create request
        transaction = self._server.resourceLayer.create_resource(path, transaction)
        return transaction

    def _handle_delete(self, transaction):
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
        if path== "/":
            transaction.response.code = defines.Codes.FORBIDDEN.number
            return transaction
        try:
            resource = self._server.root[path]
        except KeyError:
            resource = None

        if resource is None:
            transaction.response.code = defines.Codes.NOT_FOUND.number
        else:
            # Delete
            transaction.resource = resource
            transaction = self._server.resourceLayer.delete_resource(transaction, path)
        return transaction

