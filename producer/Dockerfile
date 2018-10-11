FROM python:3.7

# Set our working directory
WORKDIR /usr/src/app

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Remove warnings
ENV PYTHONWARNINGS="ignore"
ENV PRODUCER='{"production": [{"energy": {"module": "core.input.bond_api", "class_name": "BondAPIv1", "class_parameters": {"base_url": "http://29253730.ngrok.io/v1", "source": "produced", "device_id": "10338172"}}, "carbonemission": {"module": "core.input.carbonemission", "class_name": "Wattime", "class_parameters": {"usr": "energyweb", "pwd": "en3rgy!web", "ba": "FR", "hours_from_now": 24}}, "origin": {"module": "core.abstract.bond", "class_name": "OriginCredentials", "class_parameters": {"asset_id": 0, "contract_address": "0x90EaE2895d941c58eada25bDBe46e98Cd67A0819", "wallet_add": "0xD3d6285c621D0310426E45E15480cc8054602690", "wallet_pwd": "42ff8dd7c3ced6aada168b4cf3a9fcf4ffad86a6abb517db05187c0e3c90e220"}}, "name": "WirepassP"}], "client": {"module": "core.output.energyweb", "class_name": "RemoteClientOriginProducer", "class_parameters": {"url": "http://parity:8545"}}}'

# bond.py will run when container starts up on the device
CMD ["python","origin-producer.py"]