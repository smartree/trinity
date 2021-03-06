# coding: utf-8
from asyncio import Protocol, get_event_loop, iscoroutine
from config import cg_end_mark, cg_bytes_encoding

class ClientManage():
    def __init__(self):
        self.transports = set()

    def register(self, transport):
        self.transports.add(transport)

    def unregister(self, transport):
        self.transports.remove(transport)

climanage_singleton = ClientManage()

class ClientProtocol(Protocol):
    """
    asyncio.Protocol 继承类 不要手动实例化\n
    每个protocol 匹配一个transport\n
    每个client连接会创建一个新的protocol(同时匹配一个transport)
    """
    def __init__(self):
        super().__init__()
        self._transport = None
        self.received = []
        self.state = None
    
    def connection_made(self, transport):
        self.state = "connected"
        self._transport = transport
        climanage_singleton.register(self._transport)
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))

    def data_received(self, data):
        self.received.append(data)
        last_index = len(cg_end_mark)
        if cg_end_mark.encode(cg_bytes_encoding) == data[-last_index:]:
            complete_bdata = b"".join(self.received)
            print("++++++",len(complete_bdata),"+++++++++")
            from gateway import gateway_singleton
            gateway_singleton.handle_tcp_request(self._transport, complete_bdata)
            self.received = []
        else:
            print("tcp data transport by blocking")

    def connection_lost(self, exc):
        from gateway import gateway_singleton
        from utils import del_dict_item_by_value
        self.state = "closed"
        climanage_singleton.unregister(self._transport)
        self._transport.close()
        print("Connection lost", exc)
        del_dict_item_by_value(gateway_singleton.tcp_pk_dict, self._transport)
        del self

    def pause_writing(self):
        print(self._transport.get_write_buffer_size())
        self.state = "paused"

    def resume_writing(self):
        print(self._transport.get_write_buffer_size())
        self.state = "resumed"


def find_connection(url):
    """
    has connected the host of the addr
    then communicate with the exist connection
    or create a new connection
    """
    from gateway import gateway_singleton
    from utils import get_public_key
    pk = get_public_key(url)
    exist_transport = gateway_singleton.tcp_pk_dict.get(pk)
    if exist_transport in (gateway_singleton.tcpserver.transports | gateway_singleton.client.transports):
        return exist_transport
    # disconnected
    else:
        return None

async def send_tcp_msg_coro(url, bdata):
    """
    :param bdata: bytes type
    """
    from gateway import gateway_singleton
    from utils import get_addr, get_public_key
    addr = get_addr(url)
    pk = get_public_key(url)
    result = await get_event_loop().create_connection(ClientProtocol, addr[0], addr[1])
    gateway_singleton.tcp_pk_dict[pk] = result[0]
    result[0].write(bdata)

