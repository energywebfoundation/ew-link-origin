# EWF-link for [COO](https://github.com/energywebfoundation/ewf-coo)
Service designed to be a general oracle for reading, parsing and writing energy industry related data to and from the blockchain.

EWF-link Origin is currently deployed on `x86_64`, `arm64` and `armv8` architecture devices using [resin.io](resin.io). The devices logs carbon emission and generated/consumed power data into [certificate of origin](https://github.com/energywebfoundation/certificate_of_origin) smart-contracts.

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

### Requesting access and burning the SDCard
1. Artik710 development kit board. [Buy it on Mouser](https://www.mouser.de/ProductDetail/Samsung-ARTIK/SIP-KITNXE001?qs=sGAEpiMZZMve4%2fbfQkoj%252bITJFZOYkcE6OmmcL7bZCu8=). Or Raspberrypi v3 with python 3 installed.
2. Ask EWF Ramp-up team for OS images.
3. Burn the image using `dd` or `etcher`.
4. Follow the [official guide](https://developer.artik.io/documentation/developer-guide/update-image/updating-artik-image.html) to update the MMC and boot from it.

## Running on the local environment

Even though the core library is designed to be platform agnostic, `bond.py` is designed to run on top of EWF containerization platform. To enable community development of new input and output modules a local alternative is provided in the repository.

### Stepping stones to test Bond locally

1. Blockchain client. For EWF Tobalaba test chain try one of the flavors below:
    1. [Energyweb client](https://energyweb.org/blockchain/) installed and running.
    2. [Parity](https://github.com/paritytech/parity/releases)  v1.10.8 or later with `parity --jsonrpc-apis all --reserved-peers /assets/tobalaba-peers --chain tobalaba`.
    3. Docker version of Parity `docker run parity/parity:latest --chain tobalaba --jsonrpc-apis all`.
    4. More stable Docker version of Parity, change directory to `ewf-client\` and run `docker run -v $(pwd):/data parity/parity:v1.9.3 --jsonrpc-apis all --reserved-peers /data/tobalaba-peers --chain /data/chain.json`.
2. [COO](https://github.com/energywebfoundation/certificate_of_origin) contract deployed on the designated blockchain.
3. Python 3 and dependencies installed. Follow the [guide](#installing-dependencies) bellow.
4. Edit `local-producer.json` on `carbonemission` with [Wattime](http://watttime.org/) credentials.
5. Edit `local-producer.json` on `origin` with [COO](https://github.com/energywebfoundation/certificate_of_origin) contract address, asset number and credentials. The ones provided are **not working** and are just examples of format and size.
6. If the path `\mnt\data\tobalaba` does not exist it will be created at runtime. To change it edit the `PERSISTENCE` constant in `core/helper.py`.
7. With the virtual environment activated run `python local-producer.py` on the root folder of this repo.
8. Try repeating the steps with `local-consumer.json` and `local-consumer.py`.
9. Check the transactions on the [block explorer](https://tobalaba.etherscan.com/).

### Installing dependencies
Install python 3 and libraries from the os package manager. Here is an example using `apt` but different ones might apply.
```sh
sudo apt-get install python3 python-dev python3-dev \
build-essential libssl-dev libffi-dev \
libxml2-dev libxslt1-dev zlib1g-dev \
python-pip -y
```
Update python 3 in case it is previously installed but not in the latest version.
```
sudo apt-get upgrade python3 -y
```
Upgrade python package manager.
```
pip install --upgrade pip
```
Install Virtual Environment python package. Might ask for superuser permissions to install it globally.
```
pip install virtualenv
```
Create the virtual environment files in the current folder. Best on the root folder of this repo.
```
virtualenv -p python3 venv
```
After the virtual environment is created, its files are inside `venv` folder and are activated via a shell script. Run the command on the same folder the latest step was run.
```
source venv/bin/activate
```
Install the project python dependencies listed on `requirements.txt` into the current virtual environment.
```
pip install -r requirements.txt
```
