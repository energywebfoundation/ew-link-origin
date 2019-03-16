import asyncio
import datetime
import json
import pprint
import uuid
from dataclasses import dataclass

import websockets

IP = '192.168.123.220'
PORT = 8080
SELECTOR = 0
TAG_ID = '69'
"""
1 - Unlock
2 - StartTransaction
3 - StopTransaction
"""


async def ocpp_handler(websocket, path):

    @dataclass
    class Response:
        msg_id: str
        body: dict
        msg_type: int = 3

        def serialize(self):
            msg = [self.msg_type, self.msg_id, self.body]
            return msg

        def console_log(self, direction: str):
            pp = pprint.PrettyPrinter(indent=4)
            print(f"{direction} {pp.pformat(self.serialize())}\n")

    @dataclass
    class Request(Response):
        msg_id: str
        command: str
        body: dict
        msg_type: int = 2

        def serialize(self):
            msg = [self.msg_type, self.msg_id, self.command, self.body]
            return msg

    @dataclass
    class ChargingStation:
        connectors: [int]
        tags: [str]

    def command(verb: str, body: dict) -> Request:
        req = Request(str(uuid.uuid4()), verb, body)
        await websocket.send(json.dumps(req.serialize()))
        req.console_log('>>')
        return req

    def answer(req: Request, body: dict) -> Response:
        res = Response(req.msg_id, body)
        await websocket.send(json.dumps(res.serialize()))
        res.console_log('>>')
        return res

    def listen() -> Request:
        req = Request(*json.loads(await websocket.recv()))
        req.console_log('<<')
        return req

    def health_check(request: Request, response: Response, status: str) -> bool:
        if response.msg_type == 3 and response.msg_id == request.msg_id and response.body['status'] == status:
            return True
        return False

    #################################################################
    # Cycle Starts

    status_req = listen()
    if status_req.command == 'StatusNotification':
        answer(status_req, {})

    elif status_req.command == 'Heartbeat' or status_req.command == 'BootNotification':
        answer(status_req, {'currentTime': datetime.datetime.utcnow().isoformat()})

    elif status_req.command == 'BootNotification':
        answer(status_req, {'status': 'Accepted',
                            'currentTime': datetime.datetime.utcnow().isoformat(),
                            'interval': 14400})

    if SELECTOR == 1:
        req = command('UnlockConnector', {'connectorId': 1})
        res = answer(req)
        if not health_check(req, res, 'Unlocked'):
            print('[FAILED] Unlocked')
        else:
            print('[SUCCESS] Unlocked')
        return

    if SELECTOR == 2:
        req = command('RemoteStartTransaction', {'connectorId': 1, 'idTag': TAG_ID})
        if not health_check(req, listen(), 'Accepted'):
            print('[FAILED] Transaction Start')
            return
        auth_req = listen()
        expiry_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        answer(auth_req, {'idTagInfo': {'status': 'Accepted', 'expiryDate': expiry_date.isoformat()}})
        start_req = listen()
        answer(start_req, {"transactionId": 3, "idTagInfo": {"status": "Accepted", "expiryDate": expiry_date.isoformat()}})
        # Meter read is in body from start_req as 'meterStart'
        status_req = listen()
        answer(status_req, {})
        if status_req.body['status'] == 'Charging' and status_req.body['errorCode']:
            print('[SUCCESS] Charging')
        return

server = websockets.serve(ws_handler=ocpp_handler, host=IP, port=PORT, subprotocols=['ocpp1.6'])

if __name__ == '__main__':
    try:
        print('Server started')
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
    except:
        server.ws_server.close()
        print('Server stopped')
