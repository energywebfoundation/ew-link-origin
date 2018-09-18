# Hardware Link for [COO](https://github.com/energywebfoundation/ewf-coo)
[![](https://img.shields.io/badge/version-dev-red.svg)](https://softwareengineering.stackexchange.com/questions/61726/define-production-ready)

[Energyweb](energyweb.org) link is a hardware oriented project to integrate energy assets to the [Origin DAPP](](https://github.com/energywebfoundation/ewf-coo)).

It is currently deployed on `x86_64`, `arm64` and `armv8` architecture devices using [resin.io](resin.io). The devices logs carbon emission and generated/consumed power data into [certificate of origin](https://github.com/energywebfoundation/certificate_of_origin) smart-contracts.

### Origin App
![Origin App Entity-Controller-Boundry Diagram](https://github.com/energywebfoundation/ewf-link-origin/blob/master/media/origin-ecb.png)

### Over simplified lifecycle
1. Read or Create `PERSISTENCE` path pointed at `core\helper.py`.
2. Open and parse the designated configuration file.
3. Instantiate classes by reflecting the objects in the config file.
4. In case of failure on steps above throws.
5. Log configuration.
6. Schedule measurements.
7. Wake up and try to read from input modules.
8. Log success or failure.
9. Create and sign a transaction to the designates smart contract.
10. Try to reach blockchain client and send the transaction.
11. Log success of failure.
12. Back to step 6.

## Deploying on hardware
For a decentralized network infrastructure, it is fundamental that every power generating site runs and maintains its energyweb client, providing all participants the ability to be independent and part of the consensus regarding the state of the smart contracts it runs.

To facilitate the deployment and updating of these devices we use a continuous integration and fleet management platform.

## EWF Affiliates
### Requesting access and burning the SDCard
1. Artik710 development kit board. [Buy it on Mouser](https://www.mouser.de/ProductDetail/Samsung-ARTIK/SIP-KITNXE001?qs=sGAEpiMZZMve4%2fbfQkoj%252bITJFZOYkcE6OmmcL7bZCu8=). Or Raspberrypi v3 with python 3 installed.
2. Ask EWF Ramp-up team for OS images.
3. Burn the image using `dd` or `etcher`.
4. Follow the [official guide](https://developer.artik.io/documentation/developer-guide/update-image/updating-artik-image.html) to update the MMC and boot from it.

### Stepping stones

1. Blockchain client. For EWF Tobalaba test chain try one of the flavors below:
    1. [Energyweb client](https://energyweb.org/blockchain/) installed and running.
    2. [Parity](https://github.com/paritytech/parity/releases)  v1.10.8 or later with `parity --jsonrpc-apis all --reserved-peers /assets/tobalaba-peers --chain tobalaba`.
    3. Docker version of Parity `docker run parity/parity:latest --chain tobalaba --jsonrpc-apis all`.
    4. More stable Docker version of Parity, change directory to `ewf-client\` and run `docker run -v $(pwd):/data parity/parity:v1.9.3 --jsonrpc-apis all --reserved-peers /data/tobalaba-peers --chain /data/chain.json`.
2. [COO](https://github.com/energywebfoundation/certificate_of_origin) contract deployed on the designated blockchain.
3. Check the transactions on the [block explorer](https://tobalaba.etherscan.com/).

## Non-Affiliate 
### Using this repository: 
- create a new project in `resin.io`
- select `artik710`, add a new device, download the image
- follow the instruction on screen to flash your device,
- after your device is available on the dashboard, open your `terminal` fo some cli fun.
- change to this repository folder and run `git remote add resin <USERNAME>@git.resin.io:<USERNAME>/<APPNAME>.git` with your resin.io credentials.
- run `source ./sendToResin.sh`. You should now see the resin.io unicorn on your terminal.
- your device should start updating with the code you deployed.
- on the dashboard open your device, then open the `Service Variables` tab.
- create a variable for `origin-producer` named `producer` with the configuration file written __in one line__.
- create a variable for `origin-consumer` named `consumer` with the configuration file written __in one line__.

__production configuration example:__
```json
{
  "production": [
    {
      "energy": {
        "module": "core.input.fronius",
        "class_name": "LoxoneTest",
        "class_parameters": {
          "ip": "http://0.0.0.0:123",
          "source": "Produced",
          "user": "123",
          "password": "123"
        }
      },
      "carbonemission": {
        "module": "core.input.carbonemission",
        "class_name": "Wattime",
        "class_parameters": {
          "usr": "energyweb",
          "pwd": "en3rgy!web",
          "ba": "FR",
          "hours_from_now": 24
        }
      },
      "origin": {
        "module": "core.abstract.bond",
        "class_name": "OriginCredentials",
        "class_parameters": {
          "asset_id": 2,
          "contract_address": "0xc73728651f498682ab56a2a82ca700e06949b9b4",
          "wallet_add": "0x00C4D3aaB56dC8Be0dFE3AD7B1d418210172C578",
          "wallet_pwd": "ea793f1e52af6d9dc650ee91bb6f0b701bff5f60b021cb06b1cb78574954ae91"
        }
      },
      "name": "TestProducer"
    }
  ],
  "client": {
    "module": "core.output.energyweb",
    "class_name": "RemoteClientOriginProducer",
    "class_parameters": {
      "url": "https://tobalaba.slock.it/rpc:8545"
    }
  }
}
```

__consumption configuration example:__
```json
{
  "consumption": [
    {
      "energy": {
        "module": "core.input.fronius",
        "class_name": "LoxoneTest",
        "class_parameters": {
          "ip": "http://0.0.0.0:123",
          "source": "Consumed",
          "user": "123",
          "password": "123"
        }
      },
      "origin": {
        "module": "core.abstract.bond",
        "class_name": "OriginCredentials",
        "class_parameters": {
          "asset_id": 2,
          "contract_address": "0xc68fb291a6ddf3d4d9e3a061de39563bf269d868",
          "wallet_add": "0x0088fF114071cD11D910A3C4C999215DbbF320fF",
          "wallet_pwd": "8cc3187a123770c8b6b89ccee765fbfafc36d64d80a6f33d7e4ffc4ff638097f"
        }
      },
      "name": "TestConsumer"
    }
  ],
  "client": {
    "module": "core.output.energyweb",
    "class_name": "RemoteClientOriginConsumer",
    "class_parameters": {
      "url": "https://tobalaba.slock.it/rpc:8545"
    }
  }
}
```
