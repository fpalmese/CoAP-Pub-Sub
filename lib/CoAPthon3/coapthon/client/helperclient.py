import random
from multiprocessing import Queue
from queue import Empty
import threading,time
from coapthon.messages.message import Message
from coapthon import defines
from coapthon.client.coap import CoAP
from coapthon.messages.request import Request
from coapthon.utils import generate_random_token
import coapthon.utils
__author__ = 'Giacomo Tanganelli'

"""
class subThread(threading.Thread):
    def __init__(self,request,callback, target, *args, **kwargs):
        super(subThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()
        self.function = target
        self.args = (request,callback)
        print("SPAWNED A SUBTHREAD")

    def stop(self):
        self._stop.set()
        print("KILLED A SUBTHREAD")

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while True:
            if self.stopped():
                return
            else:
                print("executing subthread")
                self.function(self.args[0],self.args[1])
"""

#this class includes the function "thread body"
class subThread(threading.Thread):
    def __init__(self,client,request,callback, *args, **kwargs):
        super(subThread, self).__init__(*args, **kwargs)
        self.toStop = False
        self.args = (request,callback)
        self.client = client
        #self.daemon = True

    def stopit(self):
        self.toStop = True

    def stopped(self):
        return self.toStop

    def run(self):
        while True:
            if self.stopped():
                return
            else:
                #wait for any incoming response (for any of the pending request)
                response = self.client.queue.get(block=True)
                if response is None:
                    continue
                try:
                    request = self.client.pendingRequests[response.token]
                except:
                    continue
                if hasattr(request,"uri_path"):
                    response.uri_path = request.uri_path
                #Call the callback
                # self.args[1](response)
                #the line down here is made to print the put response with the put payload (only for testing)
                if request.code == defines.Codes.PUT.number:
                    response.payload = request.payload
                # the 2 lines down are to call the callback but with an other thread (to not block here and go on)
                cbthread = threading.Thread(target=self.args[1], args=([response]))
                cbthread.start()

                #receive response for UNSUBSCRIBE here
                if response.code == defines.Codes.NO_CONTENT.number:
                    if request.observe== 1 and request.code == defines.Codes.GET.number:
                        for token in list(self.client.pendingRequests):
                            req = self.client.pendingRequests[token]
                            if request.uri_path == req.uri_path and req.code == defines.Codes.GET.number and req.observe == 0:
                                del self.client.pendingRequests[token]
                        #delete unsubscribe from incoming responses
                        del self.client.pendingRequests[request.token]

                #if response is a NOT_FOUND you can remove the current request from pending request(a read or a subscribe too)
                elif response.code == defines.Codes.NOT_FOUND.number:
                    del self.client.pendingRequests[response.token]

                #if you receive a message that is not a NO_CONTENT then you can remove the normal READS (not subs) from pending requests
                elif response.code != defines.Codes.NO_CONTENT.number:
                    if request.observe != 0:
                        del self.client.pendingRequests[response.token]

                #if there are no pending requests you can kill the thread
                if not self.client.pendingRequests:
                    self.client.runningThread = None
                    self.stopit()



class HelperClient(object):
    """
    Helper Client class to perform requests to remote servers in a simplified way.
    """
    def __init__(self, server,qos=1,sock=None, cb_ignore_read_exception=None, cb_ignore_write_exception=None):
        """
        Initialize a client to perform request to a server.

        :param server: the remote CoAP server
        :param sock: if a socket has been created externally, it can be used directly
        :param cb_ignore_read_exception: Callback function to handle exception raised during the socket read operation
        :param cb_ignore_write_exception: Callback function to handle exception raised during the socket write operation 
        """
        self.qos = qos
        self.server = server
        self.protocol = CoAP(self.server, random.randint(1, 65535), self._wait_response, sock=sock,
                             cb_ignore_read_exception=cb_ignore_read_exception, cb_ignore_write_exception=cb_ignore_write_exception)
        self.queue = Queue()
        self.runningThread = None
        self.pendingRequests = {}

    def _wait_response(self, message):
        """
        Private function to get responses from the server.

        :param message: the received message
        """
        if message is None or message.code != defines.Codes.CONTINUE.number:
            self.queue.put(message)

    def stop(self):
        """
        Stop the client.
        """
        self.protocol.close()
        self.queue.put(None)

    def close(self):
        """
        Close the client.
        """
        self.stop()

    def _thread_body(self, request, callback):
        """
        Private function. Send a request, wait for response and call the callback function.

        :param request: the request to send
        :param callback: the callback function
        """
        #self.protocol.send_message(request)
        response = self.queue.get(block=True)
        callback(response)

    def cancel_observing(self, response, send_rst):  # pragma: no cover
        """
        Delete observing on the remote server.

        :param response: the last received response
        :param send_rst: if explicitly send RST message
        :type send_rst: bool
        """
        if send_rst:
            message = Message()
            message.destination = self.server
            message.code = defines.Codes.EMPTY.number
            message.type = defines.Types["RST"]
            message.token = response.token
            message.mid = response.mid
            self.protocol.send_message(message)
        self.stop()

    def get(self, path, callback=None, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a GET on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.mk_request(defines.Codes.GET, path)
        if (request.uri_query is not None and request.uri_query != ""):
                request.content_type = defines.Content_types["application/link-format"]
        request.token = generate_random_token(2)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout)

    def get_non(self, path, callback=None, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a GET on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.mk_request_non(defines.Codes.GET, path)
        if (request.uri_query is not None and request.uri_query != ""):
                request.content_type = defines.Content_types["application/link-format"]
        request.token = generate_random_token(2)

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout)

    def observe(self, path, callback, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a GET with observe = 0 on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon notifications
        :param timeout: the timeout of the request
        :return: the response to the observe request
        """
        request = self.mk_request(defines.Codes.GET, path)
        request.token = generate_random_token(2)
        request.observe = 0
        if self.qos == 0:
            request.type = defines.Types["NON"]

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout)


#function added by Fabio Palmese. Necessary to send the unsubscribe.
    def remove_observe(self, path,callback=None,timeout=None,**kwargs):  # pragma: no cover
        """
        Perform a GET with observe = 1 on a certain path.

        :param path: the path
        :param timeout: the timeout of the request
        :param no_response: the no_response option to include in the request
        :return: the response to the observe request
        """
        request = self.mk_request(defines.Codes.GET, path)
        request.token = generate_random_token(2)
        request.observe = 1

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)
        #kill the thread listening on the topic

        if self.qos == 0:
            request.type = defines.Types["NON"]

        self.pendingRequests[request.token]=request

        return self.send_request(request,timeout,no_response=26)

    def delete(self, path, callback=None, timeout=None, no_response = 0,**kwargs):  # pragma: no cover
        """
        Perform a DELETE on a certain path.

        :param path: the path
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :param no_response: the no_response option to include in the request
        :return: the response
        """
        request = self.mk_request(defines.Codes.DELETE, path)

        if self.qos==0:
            request.type = defines.Types["NON"]
        if no_response!=0:
            request.add_no_response(no_response)
        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)
        return self.send_request(request, callback, timeout, no_response=no_response)

    def post(self, path, payload, callback=None, timeout=None, no_response=0, **kwargs):  # pragma: no cover
        """
        Perform a POST on a certain path.

        :param path: the path
        :param payload: the request payload
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :param no_response: the no_response option to include in the request
        :return: the response
        """
        request = self.mk_request(defines.Codes.POST, path)
        request.token = generate_random_token(2)
        request.payload = payload
        if no_response!=0:
            request.add_no_response(no_response)
        if self.qos==0:
            request.type = defines.Types["NON"]

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout, no_response=no_response)

    def put(self, path, payload, callback=None, timeout=None, no_response=0, **kwargs):  # pragma: no cover
        """
        Perform a PUT on a certain path.

        :param path: the path
        :param payload: the request payload
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :param no_response: the no_response option to include in the request
        :return: the response
        """
        request = self.mk_request(defines.Codes.PUT, path)
        request.token = generate_random_token(2)
        request.payload = payload

        if no_response!=0:
            request.add_no_response(no_response)
        if self.qos==0:
            request.type = defines.Types["NON"]

        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout, no_response=no_response)

    def discover(self, callback=None, timeout=None, **kwargs):  # pragma: no cover
        """
        Perform a Discover request on the server.

        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        request = self.mk_request(defines.Codes.GET, defines.DISCOVERY_URL)
        request.content_type = defines.Content_types["application/link-format"]
        if self.qos==0:
            request.type = defines.Types["NON"]
        for k, v in kwargs.items():
            if hasattr(request, k):
                setattr(request, k, v)

        return self.send_request(request, callback, timeout)

    def send_request(self, request, callback=None, timeout=None, no_response=0):  # pragma: no cover
        """
        Send a request to the remote server.

        :param request: the request to send
        :param callback: the callback function to invoke upon response
        :param timeout: the timeout of the request
        :return: the response
        """
        self.protocol.send_message(request)
        if no_response==26:
            return
        if callback is not None:
            self.pendingRequests[request.token] = request
            if self.runningThread is None:
                self.runningThread = subThread(self, request, callback)
                self.runningThread.start()
        else:
            try:
                response = self.queue.get(block=True, timeout=timeout)
            except Empty:
                #if timeout is set
                response = None
            return response

    def send_empty(self, empty):  # pragma: no cover
        """
        Send empty message.

        :param empty: the empty message
        """
        self.protocol.send_message(empty)

    def mk_request(self, method, path):
        """
        Create a request.

        :param method: the CoAP method
        :param path: the path of the request
        :return:  the request
        """
        request = Request()
        request.destination = self.server
        request.code = method.number
        request.uri_path = path
        return request

    def mk_request_non(self, method, path):
        """
        Create a request.

        :param method: the CoAP method
        :param path: the path of the request
        :return:  the request
        """
        request = Request()
        request.destination = self.server
        request.code = method.number
        request.uri_path = path
        request.type = defines.Types["NON"]
        return request


