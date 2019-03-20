# Based on OCPP 1.6-JSON
import uuid
from dataclasses import dataclass, field

from app.ocpp16.memorydao import MemoryDAOFactory, Model

FACTORY = MemoryDAOFactory()


@dataclass
class Request:
    msg_type: int
    msg_id: str
    command: str
    body: dict

    def serialize(self):
        msg = [self.msg_type, self.msg_id, self.command, self.body]
        return msg


@dataclass
class Response:
    msg_type: int
    msg_id: str
    body: dict
    req: Request = None

    def serialize(self):
        msg = [self.msg_type, self.msg_id, self.body]
        return msg


@dataclass
class ChargingStation(Model):

    host: str
    port: int
    req_queue: dict = field(default_factory=dict)
    res_queue: dict = field(default_factory=dict)
    connectors: dict = field(default_factory=dict)
    tags: [str] = field(default_factory=list)  # TODO: Use eth address as tag id
    last_heartbeat: dict = None
    reg_id = host

    def update_connector(self, number: int, body: str):
        @dataclass
        class Connector:
            number: int
            meter_read: str
            meter_unit: str
            last_status: str
        if number not in self.connectors:
            self.connectors[number] = Connector(number, '1', 'a', '∂')
        return self.connectors[number]

    def follow_protocol(self, message: Request or Response):
        if isinstance(message, Response):
            response = message
            # TODO: Gather responses
            request = self.req_queue.pop(message.msg_id)
            if request.command == 'penis' and response.body['status'] == 'Accepted':
                return
            else:
                print(f'Request {request.serialize()} failed')
                raise Exception('Command failed, please check Charging Station.')
        else:
            ocpp_server_protocol(message)


stateful_cs = FACTORY.get_instance(ChargingStation)


def dispatcher(cs: ChargingStation, incoming: Request or Response):

    cs = stateful_cs.persist(cs)
    if isinstance(incoming, Response):
        if incoming.msg_id not in cs.req_queue:
            raise ConnectionError('Out-of-sync: Response for an unsent message.')
        incoming.req = cs.req_queue[incoming.msg_id]
    cs.follow_protocol(message=incoming)
    stateful_cs.update(cs)


def aggregator() -> [Request or Response]:
    requests, responses = [], []
    requests = [requests + cs.req_queue for cs in stateful_cs.retrieve_all()]
    responses = [responses + cs.res_queue for cs in stateful_cs.retrieve_all()]
    return responses + requests


def ocpp_server_protocol(req: Request) -> Response:

    def command(verb: str, body: dict) -> Request:
        req = Request(str(uuid.uuid4()), verb, body)
        return req

    def answer(req: Request, body: dict) -> Response:
        res = Response(req.msg_id, body)
        return res
    if req.command == 'StatusNotification':
        answer(status_req, {})

    elif status_req.command == 'Heartbeat':
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
