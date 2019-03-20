import asyncio
import json
import pprint

import websockets

from app.ocpp16.protocol import aggregator, dispatcher, Response, Request, ChargingStation

IP = '192.168.123.220'
PORT = 8080


async def ocpp_router(websocket, path):

    def console_log(msg: Request or Response, direction: str):
        pp = pprint.PrettyPrinter(indent=4)
        print(f"{direction} {pp.pformat(msg.serialize())}\n")

    #   - Send Messages from all charging stations queues
    for outcoming in aggregator():
        await websocket.send(json.dumps(outcoming.serialize()))  # TODO: check about awaiting or not
        console_log(outcoming, '>>')

    #   - Receive a new message and route it
    packet = json.loads(await websocket.recv())  # TODO: check about awaiting or not
    if len(packet) < 1 or packet[0] not in (2, 3):
        print(f'<< UNKNOWN PACKET {packet}')
        return None
    incoming = Request(*packet) if packet[0] == 2 else Response(*packet)
    console_log(incoming, '<<')
    cs = ChargingStation(*websocket.remote_address())  # remote_address returns host, port
    dispatcher(cs=cs, incoming=incoming)


server = websockets.serve(ws_handler=ocpp_router, host=IP, port=PORT, subprotocols=['ocpp1.6'])

if __name__ == '__main__':
    try:
        print('Server started')
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
    except:
        server.ws_server.close()
        print('Server stopped')
