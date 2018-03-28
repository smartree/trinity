# coding: utf-8
import json
import asyncio
from aiohttp import web, ClientSession
from jsonrpcserver.aio import methods
from jsonrpcclient.aiohttp_client import aiohttpClient
from config import cg_local_jsonrpc_addr, cg_remote_jsonrpc_addr

@methods.add
async def ping(msg):
    from gateway import gateway_singleton
    return gateway_singleton.handle_jsonrpc_request('ping', msg)
    """
    """
    # print(msg)
    # res = {
    #     "msgtype": "ack",
    #     "result": "ok"
    # }
    # from gateway import gateway_singleton
    # gateway_singleton.handle_jsonrpc(response)
    # return json.dumps(res)
    

class AsyncJsonRpc():
    @staticmethod
    async def handle(request):
        request = await request.text()
        # print(request)
        response = await methods.dispatch(request)
        if response.is_notification:
            return web.Response()
        else:
            return web.json_response(response, status=response.http_status)

    @staticmethod
    def start_jsonrpc_serv():
        app = web.Application()
        app.router.add_post('/', AsyncJsonRpc.handle)
        web.run_app(app, host=cg_local_jsonrpc_addr[0], port=cg_local_jsonrpc_addr[1])
        
    @staticmethod
    async def jsonrpc_request(loop, method, msg):
        async with ClientSession(loop=loop) as session:
            edpoint = 'http://' + cg_remote_jsonrpc_addr[0] + ":" + str(cg_remote_jsonrpc_addr[1])
            client = aiohttpClient(session, endpoint)
            response = await client.request(method, msg)
            from gateway import gateway_singleton
            gateway_singleton.handle_jsonrpc_response(response)

if __name__ == "__main__":
    AsyncJsonRpc.start_jsonrpc_serv()