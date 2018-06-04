# Bond: An energy data oracle for blockchain smart contracts
Service designed to be a general oracle for reading, parsing and writting energy industry related data to and from the blockchain.

Right now it logs carbon emission and generated power data into [certificate of origin](https://github.com/energywebfoundation/certificate_of_origin)smart-contracts.

## Deploying on hardware
For a decentralized network infrastructure it is fundamental that every power generating site runs and maintains its own energyweb client. This gives all the participants the ability to be independent and part of the consensus regarding the state of the smart contracts it runs.

To facilitate the deployment and updating of these devices we use a continuous integration and fleet management platform. Right now only Artik 710 is supported.

### Requirements
1. Artik710 development kit board. [Buy it on Mouser](https://www.mouser.de/ProductDetail/Samsung-ARTIK/SIP-KITNXE001?qs=sGAEpiMZZMve4%2fbfQkoj%252bITJFZOYkcE6OmmcL7bZCu8=)
2. Ask EWF Ramp-up team for OS images.
3. Burn the image using `dd` or `etcher`.
4. Follow the [official guide](https://developer.artik.io/documentation/developer-guide/update-image/updating-artik-image.html) to update the MMC and boot from it.

## Running on local environment

1. [Energyweb client](https://github.com/energywebfoundation/energyweb-client) installed and running.
2. Python 3 and dependencies installed. Follow the [guide](#installing-dependencies) bellow.
3. With the virtual environment activated run `python test.py` on the root folder of this repo.

### Installing dependencies
Install python 3 and libraries from the os package manager. This is an example using `apt` but different ones might apply.
```sh
sudo apt-get install python3 python-dev python3-dev \
build-essential libssl-dev libffi-dev \
libxml2-dev libxslt1-dev zlib1g-dev \
python-pip -y
```
Update python 3 in case it is previously installed nut not in the latest version.
```
sudo apt-get upgrade python3 -y
```
Upgrade python package manager.
```
pip install --upgrade pip
```
Install Virtual Environment python package. Might ask for super user permissions to install it globally.
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


