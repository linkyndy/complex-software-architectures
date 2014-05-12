import math


class Requestor(object):
    @classmethod
    def send(cls):
        raise NotImplementedError()

    @classmethod
    def receive(cls):
        raise NotImplementedError()


class Replyer(object):
    @classmethod
    def send(cls):
        raise NotImplementedError()

    @classmethod
    def receive(cls):
        raise NotImplementedError()


class Marshaller(object):
    @classmethod
    def marshall(cls):
        raise NotImplementedError()

    @classmethod
    def unmarshall(cls):
        raise NotImplementedError()


class _ProxiedMethod(object):
    """
    Represents a proxied server method, as used in the ClientProxy class
    """

    def __init__(self, proxy_obj, method):
        self.proxy_obj = proxy_obj
        self.method = method

    def __call__(self, *args):
        """
        If the proxied method exists, marshalls the method and the arguments
        it was called with, send the request, intercepts the response,
        unmarshalls it and returns the result
        """

        if not hasattr(self.proxy_obj.server, method):
            raise AttributeError('Method %s is not defined '
                                 'on %s' % (method, self.proxy_obj.server))

        Requestor.send(Marshaller.marshall(method, *args))
        response = Requestor.receive()
        return Marshaller.unmarshall(response)


class Client(object):
    pass


class ClientProxy(object):
    def __init__(self, server):
        self.server = server

    def __getattr__(self, name):
        return _ProxiedMethod(self, name)


class Server(object):
    proxy = None


class ServerProxy(object):
    def __init__(self, server):
        self.server = server

    def run(self):
        """
        Awaits for a message, unmarshalls it, calls the appropiate service on
        bound server, marshalls the response and sends a message back
        """

        while(True):
            message = Replyer.receive()
            method, params = Marshaller.unmarshall(message)
            response = getattr(self.server, method)(*params)
            Replyer.send(Marshaller.marshall(response))


class Broker(object):
    def __init__(self):
        self.servers = {}

    def register(self, server, name):
        """
        Registers a server with given name, creates a proxy for it and runs
        the proxy
        """

        self.servers[name] = server
        server.proxy = ServerProxy(server)
        server.proxy.run()

    def find(self, name):
        """
        Finds a registered server by name, creates a client proxy for this
        server and returns it
        """

        server = self.servers[name]
        proxy = ClientProxy(server)
        return proxy

broker = Broker()


class InfoClient(Client):
    @staticmethod
    def actions():
        """
        Test actions which demonstrate how a client works
        """

        server = broker.find('info_server_1')
        print server.road_info(1)


class InfoServer(Server):
    def road_info(self, road_id):
        data = {
            1: 'free',
            2: 'high traffic',
            3: 'jammed'
        }
        return data[road_id]

    def temperature(self, city):
        data = {
            'London': 20,
            'Paris': 14,
            'Hawaii': 30
        }
        return data[city]


class MathServer(Server):
    def add(self, a, b):
        return a+b

    def sqrt(self, a):
        return math.sqrt(a)


if __name__ == '__main__':
    info_server_1 = InfoServer()
    broker.register(info_server_1, 'info_server_1')

    InfoClient.actions()
