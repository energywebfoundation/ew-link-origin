# EWF_CoO

## install
To install the certificate of origin simply run <code>npm install</code>.

## clients 
The certificate of origin app can be deployed on any ethereum-network. For testing purposes we recommend deploying it on a local ganache-rpc. We already preconfigured ganache-cli, so with the command <code>npm run start-ganache</code> a preconfigured ganache cli will start. 

## migration

In order to deploy the contracts on your chosen network, simply run <code>npm run migrate</code>. 

## preconfigured accounts

(0) 0x3b07f15efb10f29b3fc222fb7e717e9af0cc4243  <br />-> TopAdmin-account, owner of the coo contracts, Trader <br />
(1) 0x71c31ff1faa17b1cb5189fd845e0cca650d215d3 <br />-> userAdmin, Trader, AssetManager <br />
(2) 0xcea1c413a570654fa85e78f7c17b755563fec5a5 <br />-> assetAdmin <br />
(3) 0x583b3e16a27f3db4bdc4c1a5452eeed14619c8da <br />
(4) 0x33496f621350cea01b18ea5b5c43c6c233c3f72d <br />
(5) 0x51ba6877a2c4580d50f7ceece02e2f24e78ef123 <br />
(6) 0xfeebf1e463e39d09d5f8a40a6ed08d604ab01360 <br />
(7) 0x585cc5c7829b1fd303ef5c019ed23815a205a59e <br />
(8) 0x343854a430653571b4de6bf2b8c475f828036c30 <br />-> Matcher <br />
(9) 0x84a2c086ffa013d06285cdd303556ec9be5a1ff7 <br />-> Trader <br />
(10) 0x00f4af465162c05843ea38d203d37f7aad2e2c17 <br />-> agreementAdmin<br />

## roles
* owner of CoO.sol contract - has all roles by default
* topAdmin: allowed to onboard new users and their roles, assets, demands, admins
* userAdmin: allowed to onboard new users
* assetAdmin: allowed to onboard new assets
* agreementAdmin: allowed to onboard new agreements
* trader: allowed to trade and buy certificates
* assetManager: allowed to be the owner of an asset
* matcher: allowed to match energy with demands

## consuming assets
### create / onboard

In order to onboard a new asset you have to call the <code>createAsset()</code>-function of the consumingAssetRegistry-contract as either a TopAdmin or assetAdmin. That function will return a new assetId in an event. You have to use this received assetId in the next steps. <br />
After you received your assetId you can call the functions <code>initGeneral (uint _assetId, address _smartMeter, address _owner, uint _operationalSince, uint _capacityWh, bool maxCapacitySet,bool _active)</code> and <code>initLocation (uint _assetId, bytes32 _country, bytes32 _region, bytes32 _zip, bytes32 _city, bytes32 _street, bytes32 _houseNumber, bytes32 _gpsLatitude, bytes32 _gpsLongitude)</code>.  After the last of those init-transactions you should get a LogAssetFullyInitialized-event with your assetId

### logging energy

In order to log consumed energy you have to call the <code>saveSmartMeterRead(uint _assetId, uint _newMeterRead, bytes32 _lastSmartMeterReadFileHash, bool _smartMeterDown)</code> function. 

## producing assets
### create / onboard
The procedure for onboadring a producing asset is nearly the same like the consuming ones: First you have to call the <code>createAsset()</code>-function of the producingAssetRegistry-contract as either a TopAdmin or assetAdmin. It will return your new assetId as event. 
Afterwards you have to call the functions <code>initProducingProperties(uint _assetId, AssetType _assetType, uint _capacityWh, Compliance _registryCompliance, bytes32 _otherGreenAttributes, bytes32 _typeOfPublicSupport)</code>, <code>initGeneral(uint _assetId, address _smartMeter, address _owner, uint _operationalSince, bool _active) </code> and <code>initLocation (uint _assetId, bytes32 _country, bytes32 _region, bytes32 _zip, bytes32 _city, bytes32 _street, bytes32 _houseNumber, bytes32 _gpsLatitude, bytes32 _gpsLongitude)</code>. After the last of those init-transactions you should get a LogAssetFullyInitialized-event with your assetId.

### logging energy
The logging of the produced energy is done by the <code>saveSmartMeterRead(uint _assetId, uint _newMeterRead, bool _smartMeterDown, bytes32 _lastSmartMeterReadFileHash, uint _CO2OffsetMeterRead, bool _CO2OffsetServiceDown)</code>.

## users
A TopAdmin or an userAdmin can onboard new users with the following command: <code>setUser(address _user, bytes32 _firstName, bytes32 _surname, bytes32 _organization,  bytes32 _street, bytes32 _number, bytes32 _zip, bytes32 _city, bytes32 _country, bytes32 _state)</code>.
Afterwards the roles of the users have to be added by either calling the <code>setRoles(address _user, uint _rights)</code> functions or by calling the add...Role-functions. 

## demands
### creation
A TopAdmin or an agreementAdmin is able to create new demands. First they have to call the <code>createDemand([])</code>-function of the demandLogic-contract. You have to provide an array with 10 elements for the different properties that are enabled or disabled (see smart contracts). 
Afterwards you have to call the functions <code>initGeneralAndCoupling(uint _demandId, address _originator, address _buyer, uint _startTime, uint _endTime, TimeFrame _tf, uint _pricePerCertifiedKWh, Currency _currency, uint _prodAsset, uint _consAsset)</code>
, <code>initMatchProperties(uint _demandId, uint _kWAmountPerPeriod, uint _productionLastSetInPeriod, address _matcher)</code>and <code>initPriceDriving(uint _demandId, bytes32 _locationCountry, bytes32 _locationRegion, AssetProducingRegistryLogic.AssetType _type,
 uint _minCO2Offset, uint _registryCompliance, bytes32 _otherGreenAttributes, bytes32 _typeOfPublicSupport)</code>.<br />
 The smart contract will also check different things when creating a demand:

* it is not allowed to have both an originator and a specific producing asset
* if a producing asset is enabled, the producing asset has to exist
* if a consuming asset is enabled, the consuming asset has to exist 
* the matcher-address has to have to matcher-role
### matching
There are 2 types of matching:
* <code>matchCertificate(uint _demandId, uint _certificateId)</code> for matching an existing certificate to a demand
* <code>matchDemand(uint _demandId, uint _wCreated, uint _prodAssetId)</code> for matching produced energy with a demand

Internally both functions are calling the same functions for checking the fitting of the demand and the energy / certificate. Those functions can also be called before and without a transaction, enabling checking if it would fit on where / if an error would occur:
* <code>checkDemandCoupling(uint _demandId, uint _prodAssetId, uint _wCreated)</code>
* <code>checkDemandGeneral(uint _demandId, uint _prodAssetId)</code>
* <code>checkMatcher(uint _demandId, uint _wCreated)</code>
* <code>checkPriceDriving(uint _demandId, uint _prodAssetId, uint _wCreated, uint _co2Saved)</code>

If the matching of produced energy with a demand was successfull a new certificate is created with the buyer as new owner. If a demand is successfully matched with a certificate the owner gets transfered.

If produced energy does not match any demand a new certificate will be created with the assetOwner as certificate-owner and an escrow-address. Only those certificates are allowed to be matched with demands. 

## blockchain facade / JavaScript-interface
We provided an interface for interacting with the deployed smart contracts. (See src/blockchain-facade for details)
