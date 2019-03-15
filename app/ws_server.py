import asyncio
import json
import pprint
from dataclasses import dataclass

import websockets

import energyweb

IP = '192.168.123.220'
PORT = 8080


@dataclass
class Message:
    msg_type: int
    msg_id: str
    description: str or None
    body: dict or None

    def serialize(self):
        msg = [self.msg_type, self.msg_id]
        if self.description: msg.append(self.description)
        if self.body: msg.append(self.body)
        return msg


async def ocpp_handler(websocket, path):
    raw_msg = json.loads(await websocket.recv())
    new_msg = Message(*raw_msg)
    pp = pprint.PrettyPrinter(indent=4)
    print(f"< {pp.pformat(raw_msg)}")

    if new_msg.description == 'StatusNotification':
        ack_msg = Message(3, new_msg.msg_id, None, {})
        await websocket.send(json.dumps(ack_msg.serialize()))
        print(f"> {pp.pformat(ack_msg.serialize())}")


server = websockets.serve(ws_handler=ocpp_handler, host=IP, port=8080, subprotocols=['ocpp1.6'])

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

    '[2,"8eed4fee-64bd-487f-aaa7-40b8bc3636fd","GetConfiguration",{"key":["ConnectionTimeOut"]}]'
    '[2,"fc7bec32-1807-4dee-aacf-bbe96599db64","GetConfiguration",{"key":["MeterValuesSampledData"]}]'
    '8235ade0-fe6f-8fad-3b65-fff45f3e8249' 'MD5 hash'
