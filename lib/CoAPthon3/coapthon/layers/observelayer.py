import logging
import time
from coapthon import defines

__author__ = 'Giacomo Tanganelli'

logger = logging.getLogger(__name__)


class ObserveItem(object):
    def __init__(self, timestamp, non_counter, allowed, transaction):
        """
        Data structure for the Observe option

        :param timestamp: the timestamop of last message sent
        :param non_counter: the number of NON notification sent
        :param allowed: if the client is allowed as observer
        :param transaction: the transaction
        """
        self.timestamp = timestamp
        self.non_counter = non_counter
        self.allowed = allowed
        self.transaction = transaction


class ObserveLayer(object):
    """
    Manage the observing feature. It store observing relationships.
    """
    def __init__(self):
        self._relations = {}
        self._readers = {}

    def send_request(self, request):
        """
        Add itself to the observing list

        :param request: the request
        :return: the request unmodified
        """
        if request.observe == 0:
            # Observe request
            host, port = request.destination
            key_token = hash(str(host) + str(port) + str(request.token))
            self._relations[key_token] = ObserveItem(time.time(), None, True, None)
        elif request.observe==1:
            self.remove_subscribe_client(request)
        return request

    def receive_response(self, transaction):
        """
        Sets notification's parameters.

        :type transaction: Transaction
        :param transaction: the transaction
        :rtype : Transaction
        :return: the modified transaction
        """
        host, port = transaction.response.source
        key_token = hash(str(host) + str(port) + str(transaction.response.token))
        if key_token in self._relations and transaction.response.type == defines.Types["CON"]:
            transaction.notification = True
        return transaction

    def send_empty(self, message):
        """
        Eventually remove from the observer list in case of a RST message.

        :type message: Message
        :param message: the message
        :return: the message unmodified
        """
        host, port = message.destination
        key_token = hash(str(host) + str(port) + str(message.token))
        if key_token in self._relations and message.type == defines.Types["RST"]:
            del self._relations[key_token]
        return message

    def receive_request(self, transaction):
        """
        Manage the observe option in the request end eventually initialize the client for adding to
        the list of observers or remove from the list.

        :type transaction: Transaction
        :param transaction: the transaction that owns the request
        :rtype : Transaction
        :return: the modified transaction
        """
        if transaction.request.code != defines.Codes.GET.number:
            return transaction
        path = "/" + transaction.request.uri_path
        if path not in self._relations:
            return transaction
        if transaction.request.observe == 0:
            # Observe request
            """
            host, port = transaction.request.source
            key_token = hash(str(host) + str(port) + str(transaction.request.token))
            non_counter = 0
            if key_token in self._relations:
                # Renew registration
                allowed = True
            else:
                allowed = False
            """
            host, port = transaction.request.source
            key = hash(str(host) + str(port))
            non_counter = 0

            if key in self._relations[path]:
                allowed = True
            else:
                allowed = False
            self._relations[path][key] = ObserveItem(time.time(), non_counter, allowed, transaction)
        elif transaction.request.observe == 1:
            self.remove_subscriber(transaction.request)
        return transaction

    def receive_empty(self, empty, transaction):
        """
        Manage the observe feature to remove a client in case of a RST message receveid in reply to a notification.

        :type empty: Message
        :param empty: the received message
        :type transaction: Transaction
        :param transaction: the transaction that owns the notification message
        :rtype : Transaction
        :return: the modified transaction
        """
        if empty.type == defines.Types["RST"]:
            self.remove_subscriber(empty)
            transaction.completed = True
        return transaction

    def send_response_old(self, transaction):
        """
        Finalize to add the client to the list of observer.

        :type transaction: Transaction
        :param transaction: the transaction that owns the response
        :return: the transaction unmodified
        """
        host, port = transaction.request.source
        key_token = hash(str(host) + str(port) + str(transaction.request.token))
        if key_token in self._relations:
            if transaction.response.code == defines.Codes.CONTENT.number:
                if transaction.resource is not None and transaction.resource.observable:

                    transaction.response.observe = transaction.resource.observe_count
                    self._relations[key_token].allowed = True
                    self._relations[key_token].transaction = transaction
                    self._relations[key_token].timestamp = time.time()
                else:
                    del self._relations[key_token]
            elif transaction.response.code >= defines.Codes.ERROR_LOWER_BOUND:
                del self._relations[key_token]
        return transaction

    def send_response(self, transaction):
        """
        Finalize to add the client to the list of observer.

        :type transaction: Transaction
        :param transaction: the transaction that owns the response
        :return: the transaction unmodified
        """
        host, port = transaction.request.source
        path = "/" + transaction.request.uri_path
        key = hash(str(host) + str(port))
        try:
            relations = self._relations[path]
        except KeyError:
            return transaction
        if key in relations:
            if transaction.response.code == defines.Codes.CONTENT.number:
                if transaction.resource is not None and transaction.resource.observable:
                    transaction.response.observe = transaction.resource.observe_count
                    self._relations[path][key].allowed = True
                    self._relations[path][key].transaction = transaction
                    self._relations[path][key].timestamp = time.time()
                else:
                    del self._relations[path][key]
            elif transaction.response.code >= defines.Codes.ERROR_LOWER_BOUND:
                del self._relations[path][key]
        return transaction

    def notify_old(self, resource, root=None):
        """
        Prepare notification for the resource to all interested observers.

        :rtype: list
        :param resource: the resource for which send a new notification
        :param root: deprecated
        :return: the list of transactions to be notified
        """
        ret = []
        if root is not None:
            resource_list = root.with_prefix_resource(resource.path)
        else:
            resource_list = [resource]
        for key in list(self._relations.keys()):
            if self._relations[key].transaction.resource in resource_list:
                if self._relations[key].non_counter > defines.MAX_NON_NOTIFICATIONS \
                        or self._relations[key].transaction.request.type == defines.Types["CON"]:
                    self._relations[key].transaction.response.type = defines.Types["CON"]
                    self._relations[key].non_counter = 0
                elif self._relations[key].transaction.request.type == defines.Types["NON"]:
                    self._relations[key].non_counter += 1
                    self._relations[key].transaction.response.type = defines.Types["NON"]
                self._relations[key].transaction.resource = resource
                del self._relations[key].transaction.response.mid
                del self._relations[key].transaction.response.token
                ret.append(self._relations[key].transaction)
        return ret

    def notify(self, resource, root=None):
        """
        Prepare notification for the resource to all interested observers.

        :rtype: list
        :param resource: the resource for which send a new notification
        :return: the list of transactions of observers to be notified
        """
        ret = []
        path = resource.path
        if root is not None:
            resource_list = root.with_prefix_resource(path)
        else:
            resource_list = [resource]
        try:
            relations=self._relations[path]
        except KeyError:
            relations = {}
        for key in list(relations):
            if self._relations[path][key].non_counter > defines.MAX_NON_NOTIFICATIONS \
                    or self._relations[path][key].transaction.request.type == defines.Types["CON"]:
                self._relations[path][key].transaction.response.type = defines.Types["CON"]
                self._relations[path][key].non_counter = 0
            elif self._relations[path][key].transaction.request.type == defines.Types["NON"]:
                self._relations[path][key].non_counter += 1
                self._relations[path][key].transaction.response.type = defines.Types["NON"]
            self._relations[path][key].transaction.resource = resource
            del self._relations[path][key].transaction.response.mid
            del self._relations[path][key].transaction.response.token
            ret.append(self._relations[path][key].transaction)
        return ret

    def notify_read(self,resource):
        """
                Prepare notification for the resource to all interested readers.

                :rtype: list
                :param resource: the resource for which send a new notification
                :return: the list of transactions of readers to be notified
                """
        ret = []
        try:
            readers = self._readers[resource.path]
        except:
            return ret
        for i in readers:
            if readers[i].non_counter > defines.MAX_NON_NOTIFICATIONS \
                    or readers[i].transaction.request.type == defines.Types["CON"]:
                readers[i].transaction.response.type = defines.Types["CON"]
                readers[i].non_counter = 0
            elif readers[i].transaction.request.type == defines.Types["NON"]:
                readers[i].non_counter += 1
                readers[i].transaction.response.type = defines.Types["NON"]
            readers[i].transaction.resource = resource
            del readers[i].transaction.response.mid
            del readers[i].transaction.response.token
            ret.append(readers[i].transaction)
        self._readers[resource.path] = {}
        return ret

    def remove_subscriber_old(self, message):
        """
        Remove a subscriber based on token.

        :param message: the message
        """
        logger.debug("Remove Subcriber")
        host, port = message.source
        key_token = hash(str(host) + str(port) + str(message.token))
        try:
            self._relations[key_token].transaction.completed = True
            del self._relations[key_token]
        except KeyError:
            logger.warning("No Subscriber")

    def remove_subscriber(self, message):
        """
        Remove a subscriber based on received message:
        if it's a RESET then remove from the token,
        if it's an UNSUBSCRIBE then remove from the uri_path and request source.

        :param message: the message
        """
        logger.debug("Remove Subcriber")
        host, port = message.source
        key = hash(str(host) + str(port))
        try:
            path = "/"+message.uri_path
        except:
            #coming from receive_empty: message is a RST
            self._remove_rst_relation(message)
            return
        try:
            self._relations[path][key].transaction.completed = True
            del self._relations[path][key]
        except KeyError:
            logger.warning("No Subscriber")

    def _remove_relations_old(self, resource):
        """
        Removes all the relations(subscribers and readers) to a specific resource

        :param resource: the resource involved in the relations to remove
        """
        for relation in list(self._relations):
            try:
                path = "/" + self._relations[relation].transaction.request.uri_path
            except:
                path = None
            if path == resource.path:
                del self._relations[relation]
        del self._readers[resource.path]

    def _remove_relations(self, resource):
        """
        Removes all the relations(subscribers and readers) to a specific resource

        :param resource: the resource involved in the relations to remove
        """
        del self._relations[resource.path]
        del self._readers[resource.path]

    def _remove_rst_relation(self, empty):
        [host,port] = empty.source
        key_client = hash(str(host)+str(port))
        for topic in self._relations:
            if key_client in self._relations[topic]:
                if self._relations[topic][key_client].transaction.request.token == empty.token:
                    del self._relations[topic][key_client]

    def remove_subscribe_client(self, request):
        """
        Remove a subscriber based on token.

        :param message: the message
        """
        host, port = request.destination
        key_token = hash(str(host) + str(port) + str(request.token))
        try:
            self._relations[key_token].transaction.completed = True
            del self._relations[key_token]
        except KeyError:
            #error you were not subscribed
            pass