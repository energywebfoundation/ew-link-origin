# artik710-logger
Test integration between Artik710 and industrial Data Logger.

##Setting up the Artik Environment
1. Artik710 or Artik520 (not tested yet) development kit 
2. Ubuntu running on the SD card or eMMC
3. EWF client installed and running
    - Clone the [repo](https://github.com/energywebfoundation/energyweb-client) and follow the instructions on README.
4. Python 3 installed
5. Hardware integration

##Installing dependencies
- `pip install virtualenv`
- `virtualenv -p python3 venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`

##Deploy test the contact
- Insert you own account address and pwd in `deploy.py`.
- Run `python deploy.py`
- Copy the contract address, insert you own account address and pwd in `text.py`
- Run `test.py` as many times as you want to create the log.
- Code the hardware interface to trigger the logging.