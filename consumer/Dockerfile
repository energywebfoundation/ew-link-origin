FROM python:3.7

# Set our working directory
WORKDIR /usr/src/app

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Remove warnings
ENV PYTHONWARNINGS="ignore"
ENV CONSUMER='{"consumption": [{"energy": {"module": "core.input.bond_api", "class_name": "BondAPIv1", "class_parameters": {"base_url": "http://29253730.ngrok.io/v1", "source": "produced", "device_id": "10338172"}}, "origin": {"module": "core.abstract.bond", "class_name": "OriginCredentials", "class_parameters": {"asset_id": 2, "contract_address": "0x8De517a4a7F58bbC288969778274376381644c45", "wallet_add": "0xDC52418f46c7C186eB31d8881F8d8A7Fb3Cb899b", "wallet_pwd": "0477434918183aa279fea6fd5e305986d84c0b97af2243dfe59000dacf85fbf0"}}, "name": "WirepassC"}], "client": {"module": "core.output.energyweb", "class_name": "RemoteClientOriginConsumer", "class_parameters": {"url": "http://parity:8545"}}}'

# bond.py will run when container starts up on the device
CMD ["python","origin-consumer.py"]