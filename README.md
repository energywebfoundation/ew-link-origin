# Hardware Link for [COO](https://github.com/energywebfoundation/ewf-coo)
[![](https://img.shields.io/badge/version-dev-red.svg)](https://softwareengineering.stackexchange.com/questions/61726/define-production-ready)

[Energyweb](energyweb.org) link is a hardware oriented project to integrate energy assets to the [Origin DAPP](](https://github.com/energywebfoundation/ewf-coo)).

This is the `x64_32` branch. Requires `Docker` and `docker-compose` installed.

### Instructions
1. Register the user and assets by filling spreadsheet and executing the [Origin](](https://github.com/energywebfoundation/ew-origin)) deployment script, it will deploy these contracts in the blockchain.
    1. Note down the wallet address and private key that these Assets accounts were created
    2. Note down each of this assets ids and if they are Producer or Consumer
    3. Note down the AssetProducingLogic and AssetProducingLogic contract addresses
2. Write the values in `consumer.json` and `producer.json` for `contract_address`, `wallet_addr` and `wallet_pwd`
3. Run `docker-compose up`

#### Running with Parity locally
1. Add theses lines to `docker-compose.yml`:
```yaml
  parity:
    image: parity/parity:v2.1.6
    command:
    - --chain
    - tobalaba
    - --log-file
    - /app/logs/parity.log
    - --db-compaction
    - ssd
    - --jsonrpc-interface
    - all
    volumes:
    - ./logs/:/app/logs/:rw
```
2. Change the Client url in the configs to `http://parity:8545`
3. Run for the first time will fail to log with `Out of sync` message until parity syncs.

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
