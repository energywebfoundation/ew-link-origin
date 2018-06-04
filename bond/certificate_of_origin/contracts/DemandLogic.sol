// Copyright 2018 Energy Web Foundation
// This file is part of the Origin Application brought to you by the Energy Web Foundation,
// a global non-profit organization focused on accelerating blockchain technology across the energy sector, 
// incorporated in Zug, Switzerland.
//
// The Origin Application is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// This is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY and without an implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details, at <http://www.gnu.org/licenses/>.
//
// @authors: slock.it GmbH, Martin Kuechler, martin.kuchler@slock.it
pragma solidity ^0.4.19;

import "./DemandDb.sol";
import "./RoleManagement.sol";
import "./CertificateLogic.sol";
import "./Updatable.sol";
import "./CoO.sol";
import "./AssetProducingRegistryLogic.sol";
import "./AssetConsumingRegistryLogic.sol";


/// @title The logic contract for the AgreementDB of Origin list
contract DemandLogic is RoleManagement, Updatable {

    /// @notice database contract
    DemandDB public db;

    event createdEmptyDemand(address sender, uint indexed _demandId);
    event LogDemandFullyCreated(uint indexed _demandId);
    event LogDemandExpired(uint indexed _demandId);
    event LogMatcherPropertiesUpdate(uint indexed _demandId, uint currentWhPerPeriod, uint certInCurrentPeriod, uint currentPeriod, uint certID);

    enum TimeFrame{
        yearly,
        monthly,
        daily,
        hourly
    }   

    enum Currency{
        Euro,
        USD,
        SingaporeDollar,
        Ether
    }

    /*
    none:                0x0...0000000000
    originator:          0x0...---------1
    assetTyoe:           0x0...--------1-
    complaince:          0x0...-------1--
    country:             0x0...------1---
    region:              0x0...-----1----
    minCO2:              0x0...----1-----
    producing            0x0...---1------
    consuming            0x0...--1-------
    otherGreenAttributes 0x0...-1--------
    typeOfPublicSupport  0x0...1---------
    */
    enum DemandProperties {
        originator,
        assetType, 
        compliance, 
        country, 
        region, 
        minCO2, 
        producing, 
        consuming, 
        otherGreenAttributes,
        typeOfPublicSupport
    }

    modifier isInitialized {
        require((db) != address(0x0));
        _;
    }

    modifier doesNotExist(uint _demandId) {
        require(!db.demandExists(_demandId));
        _;
    }

    /// @notice constructor
    /// @param _cooContract coo-contract
    function DemandLogic(CoO _cooContract) 
        public
        RoleManagement(_cooContract) 
    {
  
    }

    /// @notice Function to create an empty demand, functions initGeneralandCouplong, initMatcherProperties and initPricedriving have to be called in order to fully create a demandc
    /// @param _properties array with the to be enabled demandproperties (see DemandProperties struct)
    /// @dev will return an event with the event-Id
    function createDemand(bool[] _properties)
        external
        isInitialized
        onlyRole(RoleManagement.Role.AgreementAdmin)
     {
        // if the 1st and the 6th property are set (originator and producing) we will abort because those properties are not allowed to be set at the same time
        if(_properties[0] && _properties[6]) revert();
        require(_properties.length == 10);
        uint demandID = db.createEmptyDemand(createDemandBitmask(_properties));
        createdEmptyDemand(msg.sender, demandID);
    }

    /// @notice fuction to set the database contract, can only be called once
    /// @param _dbAddress address of the database contract
    function init(DemandDB _dbAddress) 
        external
        onlyRole(RoleManagement.Role.TopAdmin)
    {
        require(address(db) == 0x0);
        db = _dbAddress;
    }

    /// @notice function to create a demand and coupling of a new demand, should be called 1st
    /// @param _demandId identifier
    /// @param _originator address of an energy-producer, can be 0x0
    /// @param _buyer address oh the buyer
    /// @param _pricePerCertifiedKWh price per certified kWh
    /// @param _currency currency to be used
    /// @param _tf timeFrame
    /// @param _prodAsset array with producing assets, can be empty
    /// @param _consAsset array with consuming assets, can be empty 
    function initGeneralAndCoupling(
        uint _demandId,
        address _originator,
        address _buyer,
        uint _startTime,   
        uint _endTime,
        TimeFrame _tf,     
        uint _pricePerCertifiedKWh,
        Currency _currency,
        uint _prodAsset,
        uint _consAsset
    )
        external
        onlyRole(RoleManagement.Role.AgreementAdmin)
        isInitialized
        doesNotExist(_demandId)
    {
        uint demandMask = db.getDemandMask(_demandId);
        createGeneralDemandInternal( 
             _demandId,
             _originator,
             _buyer,
             _startTime,   
             _endTime,
             _tf,     
             _pricePerCertifiedKWh,
             _currency);
        createCouplingInternal(_demandId, _prodAsset, _consAsset, demandMask);
        checkForFullDemand(_demandId);

    }

    /// @notice function to create the matcher-properties
    /// @param _demandId identifier
    /// @param _kWAmountPerPeriod amounts of KW per Period
    /// @param _productionLastSetInPeriod todo: needed?
    /// @param _matcher address of the matcher
    function initMatchProperties(
        uint _demandId,
        uint _kWAmountPerPeriod,
        uint _productionLastSetInPeriod,
        address _matcher
    )
        external
        onlyRole(RoleManagement.Role.AgreementAdmin) 
        isInitialized
        doesNotExist(_demandId)
    {
        require(isRole(RoleManagement.Role.Matcher,_matcher));
        db.createMatchProperties(_demandId, _kWAmountPerPeriod, 0, 0, _productionLastSetInPeriod, _matcher);
        checkForFullDemand(_demandId);
    }

    /// @notice function to create a priceDriving-struct
    /// @param _demandId identifier
    /// @param _locationCountry country where the energy should be generated
    /// @param _locationRegion region where the energy should be generated
    /// @param _type fueltype
    /// @param _minCO2Offset CO2-offset
    /// @param _registryCompliance compliance
    /// @param _otherGreenAttributes other green attributes
    /// @param _typeOfPublicSupport type of public support
    function initPriceDriving(
        uint _demandId,
        bytes32 _locationCountry,
        bytes32 _locationRegion,
        AssetProducingRegistryLogic.AssetType _type,
        uint _minCO2Offset,
        uint _registryCompliance,
        bytes32 _otherGreenAttributes,
        bytes32 _typeOfPublicSupport
        
    )
        external
        isInitialized
    {
        // we can't use modifier for this function due to the stack limitation. So we have to call the checking function that checks the requirements while bypassing the stacklimit
        checking(_demandId);
        db.createPriceDriving( _demandId, _locationCountry, _locationRegion, 0x0, 0x0, 0x0, 0, 0x0, 0x0, uint(_type), _minCO2Offset, _registryCompliance, _otherGreenAttributes, _typeOfPublicSupport);
        checkForFullDemand(_demandId);
    }

   

    /// @notice function to match a certificate to a demand
    /// @param _demandId the demand-id
    /// @param _certificateId the id of a non retired certificate
    function matchCertificate(uint _demandId, uint _certificateId) 
        external
        isInitialized
    {
        // we get all the needed data from a certificate
        var(prodAssetId, , powerInW, retired, , coSaved, escrow, creationTime) = CertificateLogic(address(cooContract.certificateRegistry())).getCertificate(_certificateId);
       
        // we accept only non retired certificates and they have to creates less then 1 year ago 
        // we also make sure that only the scrow-address (aka a matcher) is able to call this function
        require(!retired && (creationTime + 365 days) >= now && msg.sender == escrow);
        require(!hasDemandPropertySet(DemandProperties.consuming, db.getDemandMask(_demandId)));
       
        // we're trying to match the certificate to a demand. If there is a non-match the function will revert
        var (owner, currentWhPerPeriod, certInCurrentPeriod, currentPeriod) = matchInternal(_demandId, powerInW, prodAssetId, coSaved);
        
        // at the end we have to update the matcher-properties 
        db.updateMatchProperties(_demandId, currentWhPerPeriod,certInCurrentPeriod, currentPeriod);
        CertificateLogic(address(cooContract.certificateRegistry())).transferOwnershipByEscrow( _certificateId,  owner);
        LogMatcherPropertiesUpdate(_demandId, currentWhPerPeriod, certInCurrentPeriod, currentPeriod, _certificateId);
    }

    /// @notice function for internal matching, gets called by both matchDemand and matchCertificate
    /// @param _demandId demandid
    /// @param _wCreated amount of power created
    /// @param _prodAssetId id of the producing-asset
    /// @param _co2Saved amount of CO2-saved
    /// @return the owner, the new (increased) amount of CurrentWhPerPeriod, the new (increased) amount of certificatesCreated per period and the current period
    function matchInternal(uint _demandId, uint _wCreated, uint _prodAssetId, uint _co2Saved)
        internal
        view
        isInitialized 
        returns (address owner,  uint currentWhPerPeriod, uint certInCurrentPeriod, uint currentPeriod)
    {
        // we have to check if a demand with that identifier actually exists
        var (generalExists, priceDrivingExists, matcherExists) = getExistStatus(_demandId);
        require(generalExists && priceDrivingExists && matcherExists);
        bool passCheck;
       
        // we're comparing the demand-properties
        (owner, passCheck,) = checkDemandGeneral(_demandId, _prodAssetId);
        require(passCheck);
        (passCheck,) = checkPriceDriving(_demandId, _prodAssetId, _wCreated, _co2Saved);
        require(passCheck);
        (currentWhPerPeriod,certInCurrentPeriod, currentPeriod,passCheck,) = checkMatcher(_demandId, _wCreated); 
        require(passCheck);
        (passCheck,) = checkDemandCoupling(_demandId, _prodAssetId, _wCreated);
        require(passCheck);

    }

    /// @notice Updates the logic contract
    /// @param _newLogic Address of the new logic contract
    function update(address _newLogic) 
        external
        onlyAccount(address(cooContract))
    {
        db.changeOwner(_newLogic);
    }  

    /// @notice funciton to retrieve the identifier-hash of an active demand 
    /// @param _demandId position in the array
    /// @return identifier-hash
    function getActiveDemandIdAt(uint _demandId) external isInitialized view returns (uint) {
        return db.getActiveDemandIdAt(_demandId);
    }

    /// @notice function to return the length of the acticeDemands-array in the database
    /// @return length if the activeDemands-array in the database
    function getActiveDemandListLength() external isInitialized view returns (uint) {
        return db.getActiveDemandListLength();
    }

    /// @notice function to return the length of the allDemands-array in the database
    /// @return length of the allDemansa-array
    function getAllDemandListLength() external isInitialized view returns (uint) {
        return db.getAllDemandListLength();
    }

    /// @notice function to get the information if the coupling-struct
    /// @param _demandId identifier
    /// @return used timeFrame
    function getDemandCoupling(uint _demandId)
        external
        view 
        isInitialized
        returns(
            uint producingAssets,
            uint consumingAssets
        ) 
    {
       return db.getDemandCoupling(_demandId);
    }

    /// @notice function to retrieve the general informations of a demand
    /// @param _demandId identifier of the demand
    /// @return the originator, buyer, startTime, endTime, currency, coupled
    function getDemandGeneral(uint _demandId)
        external 
        isInitialized        
        view 
        returns (
            address originator,
            address buyer,
            uint startTime,
            uint endTime,
            uint timeframe,
            uint pricePerCertifiedKWh,
            uint currency,
            uint demandMask
        )
    {
        return db.getDemandGeneral(_demandId);
    }

    /// @notice function to get the matcher-properties of a demand
    /// @param _demandId identifier
    /// @return amount of Wh per Period, current Wh per Period, certificates in current Period, last Period where a consumption was set and the matcher-address
    function getDemandMatcherProperties(uint _demandId)
        external
        view 
        isInitialized
        returns (  
            uint targetWhPerPeriod,
            uint currentWhPerPeriod,
            uint certInCurrentPeriod,
            uint productionLastSetInPeriod,
            address matcher
        )
    {
       return db.getDemandMatcherProperties(_demandId);
    }

    /// @notice function to get the price-driving informations
    /// @param _demandId identifier
    /// @return location country and region, assettype, CO2-offset, compliance, green attributes and type of public support
    function getDemandPriceDriving(uint _demandId)
        external
        view
        isInitialized
        returns (
            bytes32 locationCountry,
            bytes32 locationRegion,
            uint assettype,
            uint minCO2Offset,
            uint registryCompliance,
            bytes32 _otherGreenAttributes,
            bytes32 _typeOfPublicSupport,
            bool isInit
        )
    {
      return db.getDemandPriceDriving(_demandId);
    }

    /// @notice function to get the existing status of the different demand-structs
    /// @param _demandId identifier
    /// @return returns existing of generalInformation, priceDriving and matcher-Properties
    function getExistStatus(uint _demandId)
        public
        view 
        returns (bool general, bool priceDriving, bool matchProp )
    {
       var(,buyer,,,,,,) = db.getDemandGeneral(_demandId);
       general = (buyer != address(0));
       var(,,,,matcher) = db.getDemandMatcherProperties(_demandId);
       matchProp = (matcher != address(0));
       (,,,,priceDriving) = db.getDemandPriceDriving(_demandId);

    }
    /// @notice funciton to remove an active demand, can only be successfully processed if the the endTime already passed
    /// @param _demandId index of the demand in the activeDemands-array
    function removeActiveDemand(uint _demandId)
        public 
    {
        var ( , , , endTime, , , , ) = db.getDemandGeneral(_demandId);
        require(endTime < now);
        db.removeActiveDemand( _demandId);
        LogDemandExpired(_demandId);
    }

    /// @notice function to check the coupling properties of a demand
    /// @param _demandId demand-Id
    /// @param _prodAssetId production-asset id
    /// @param _wCreated amount of Wh created
    /// @return flag if the check was successfull and a string with the result
    function checkDemandCoupling(uint _demandId, uint _prodAssetId, uint _wCreated)
        public
        view 
        returns (bool, string)
    {
        var (prodAsset, consAsset ) = db.getDemandCoupling(_demandId);

        if (hasDemandPropertySet(DemandProperties.producing, db.getDemandMask(_demandId))) {
           if (_prodAssetId != prodAsset)
            return (false, "wrong prodAssetId");
        }

        if (hasDemandPropertySet(DemandProperties.consuming, db.getDemandMask(_demandId))) {
          var (capacityWh, maxCapacitySet, certificatesUsedForWh) = AssetConsumingRegistryLogic(address(cooContract.assetConsumingRegistry())).getConsumingProperies(consAsset); 
               
            if(maxCapacitySet){
                if(certificatesUsedForWh + _wCreated > capacityWh )
                    return (false, "too much energy for max capacity");
            } else {
                var(wHAmountPerperiod, , , , ) = db.getDemandMatcherProperties(_demandId);
                if(certificatesUsedForWh + _wCreated > wHAmountPerperiod)
                    return (false, "too much energy for for consuming target");
            }
            
        }
        return(true,"");
    }

    /// @notice function to check the fitting of the general-demand information with a matching
    /// @param _demandId identifier
    /// @param _prodAssetId asset-id that produced some energy
    /// @return originator-address, coupled-flag, if there was an error and what check failed
    function checkDemandGeneral(uint _demandId, uint _prodAssetId)
        public
        view
        returns (address, bool, string)
    {
        var   ( originator, buyer, startTime, endTime, , , ,demandMask) = db.getDemandGeneral(_demandId);
        var ( , owner, , , , ) = AssetProducingRegistryLogic(address(cooContract.assetProducingRegistry())).getAssetGeneral(_prodAssetId);
        
        if(hasDemandPropertySet(DemandProperties.originator, demandMask)){
            if(originator != owner)
                return (0x0, false, "wrong originator");   
        }
        if(!( 
           startTime <= now && 
           endTime >= now
           && isRole(RoleManagement.Role.Trader,owner) 
           && isRole(RoleManagement.Role.Trader, buyer)
           && isRole(RoleManagement.Role.AssetManager, owner) 
        )) return (0x0, false, "starttime or rolecheck");
        return (buyer, true, "everything ok");
    }

    /// @notice function to check the matcher-properties
    /// @param _demandId identifier
    /// @param _wCreated Wh created 
    /// @return currentWhPerPeriod, certInCurrentPeriod, currentPeriod, if there was an error and what check failed
    function checkMatcher(uint _demandId, uint _wCreated)
        public
        view 
        returns (uint , uint , uint, bool, string )
    {

        var( whAmountPerPeriod, currentWhPerPeriod, certInCurrentPeriod, lastPeriod, matcher) = db.getDemandMatcherProperties(_demandId);
        whAmountPerPeriod = getMaxEnergyCoupling(_demandId, whAmountPerPeriod);
        if (matcher != msg.sender) return (0,0,0, false, "wrong matcher");
      
        uint currentPeriod = getCurrentPeriod(_demandId);

        if (currentPeriod == lastPeriod) {
            if(currentWhPerPeriod+_wCreated > whAmountPerPeriod) return (0,0,0, false, "too much whPerPeriode");  
         }            
            else {
                if(_wCreated > whAmountPerPeriod) return (0,0,0, false, "too much whPerPeriode and currentPeriod != lastPeriod");
                lastPeriod = currentPeriod;
                currentWhPerPeriod = 0;
                certInCurrentPeriod = 0;
            }
        currentWhPerPeriod += _wCreated;
        certInCurrentPeriod += 1;
        
        return (currentWhPerPeriod, certInCurrentPeriod, currentPeriod, true, "everything OK");
        
    }
    /// @notice function to check the priceDriving-oarameters for the matching
    /// @param _demandId identifier
    /// @param _prodAssetId the producing asset-id
    /// @param _wCreated the amount of energy created
    /// @param _co2Saved the amount of CO2 saved
    /// @return if there was an error and what check failed
    function checkPriceDriving(uint _demandId, uint _prodAssetId, uint _wCreated, uint _co2Saved)
        public
        view
        returns (bool, string)
    {
        if(_wCreated == 0) return (false, "no energy created");

        var (,,, minCO2OffsetDemand, compliance,,,) = db.getDemandPriceDriving(_demandId);
        
        var(checkRes, error) = checkAssetType(_demandId, _prodAssetId);
        if(!checkRes) return (checkRes,error);
        (checkRes, error) = checkLocation(_demandId, _prodAssetId);
        if(!checkRes) return (checkRes,error);

        if(hasDemandPropertySet(DemandProperties.compliance, db.getDemandMask(_demandId))){
           if(uint(AssetProducingRegistryLogic(cooContract.assetProducingRegistry()).getCompliance(_prodAssetId)) !=compliance) return (false, "wrong compliance");
        }

        if(hasDemandPropertySet(DemandProperties.minCO2, db.getDemandMask(_demandId))){
            if(_co2Saved == 0)
                _co2Saved = AssetProducingRegistryLogic(cooContract.assetProducingRegistry()).getCoSaved(_prodAssetId, _wCreated); 
            uint co2PerWh = ((_co2Saved * 1000) / _wCreated)/10;

            if(co2PerWh < minCO2OffsetDemand)
                return (false, "wrong CO2");
        }

        if(hasDemandPropertySet(DemandProperties.otherGreenAttributes, db.getDemandMask(_demandId))){
            if(!checkGreenAttributes(_demandId, _prodAssetId)) return (false,"wrong Green Attribute");
        }

        if(hasDemandPropertySet(DemandProperties.typeOfPublicSupport, db.getDemandMask(_demandId))){
            if(!checkTypeOfPublicSupport(_demandId, _prodAssetId)) return (false,"wrong Type of public support");
        }

        return (true,"everything OK");
    }

    /// @notice function to calculate the current Period for a demand
    /// @param _demandId identifier
    /// @return current Period 
    function getCurrentPeriod(uint _demandId) 
        public 
        view 
        isInitialized
        returns (uint) 
    {
        uint tf = db.getTimeFrame(_demandId);
        if ( TimeFrame(tf) == TimeFrame.yearly) 
        {
            return ( now - db.getStartEpoche(_demandId) ) / (1 years);
        }
        if ( TimeFrame(tf) == TimeFrame.monthly) {
            return ( now - db.getStartEpoche(_demandId) ) / (30 days);
        }
        if ( TimeFrame(tf) == TimeFrame.daily) {
            return ( now - db.getStartEpoche(_demandId) ) / (1 days);
        }  
        if ( TimeFrame(tf) == TimeFrame.hourly) {
            return ( now - db.getStartEpoche(_demandId) ) / (1 hours);
        }  
    }

    /// @notice function to calculate the maximum amount of energy left for a demand and period
    /// @param _demandId the demand-id
    /// @param _whAmountPerPeriod the amount of Wh per Period
    /// @return the maximum ammount of energy left for a demand
    function getMaxEnergyCoupling(uint _demandId, uint _whAmountPerPeriod)
        public
        view
        returns(uint)
    { 
        // there is no coupling, so we don't have to go further
        if (!hasDemandPropertySet(DemandProperties.consuming, db.getDemandMask(_demandId))) return _whAmountPerPeriod;
        
        //we're getting the consuming Assets and its properties
        var (, consAsset ) = db.getDemandCoupling(_demandId);
        var (capacityWh, maxCapacitySet, certificatesUsedForWh) = AssetConsumingRegistryLogic(address(cooContract.assetConsumingRegistry())).getConsumingProperies(consAsset); 
        
        // the maxCapacitySet-flag was set
        if(maxCapacitySet){
            //we do not allow to let the capacity exceeds the amount of energy set in the demand
            if(capacityWh > _whAmountPerPeriod) 
                capacityWh = _whAmountPerPeriod;
            
            if(certificatesUsedForWh <= capacityWh)
                return (capacityWh-certificatesUsedForWh);
            else return 0;
        } 
        // there is no max capacity set, so only the demand-energy is counting
        else {
            if(certificatesUsedForWh <= _whAmountPerPeriod)
                return (_whAmountPerPeriod-certificatesUsedForWh);
            else return 0;
        }
        
        return _whAmountPerPeriod;

    }



    /// @notice function to check if a full demand is created and enabling him
    /// @param _demandId identifier
    function checkForFullDemand(uint _demandId)
        private
    {
        var (generalExists, priceDrivingExists, matcherExists) = getExistStatus(_demandId);

        if (generalExists && priceDrivingExists && matcherExists) {
            db.setEnabled(_demandId,true);
            db.addActiveDemand(_demandId);
            db.setDemandCreationTime(_demandId, now);
            LogDemandFullyCreated(_demandId);
        }
    }   

    /// @notice function to create the bitmask for a demand
    /// @param _demandArray the array with demand properties
    function createDemandBitmask (bool[] _demandArray)
        public
        pure
        returns (uint demandMask)
    {
         /** Bitmask: originator, assetType, compliance, country, region, minCO2, producing, consuming   */
        for(uint8 i = 0; i < 10; i++) {
            if(_demandArray[i]){
                demandMask += uint(2) ** uint(i);
            }
        }
    }

    /// @notice funciton for comparing the role and the needed rights of an user
    /// @param _props entry of the demandProperties-enum
    /// @param _demandMask the bitmask of the demand 
    /// @return the demand has the property set
    function hasDemandPropertySet(DemandProperties _props, uint _demandMask) public pure returns (bool) { 
        uint demandActive = uint(2) ** uint(_props);
        return (_demandMask & demandActive != 0);
    }

    /// @notice function to check the assetType
    /// @param _demandId the demand-id
    /// @param _prodAssetId the production-asset id
    /// @return the bool-flag for check and error-message
    function checkAssetType(uint _demandId, uint _prodAssetId)
        internal
        view returns (bool, string) 
    {
        if(hasDemandPropertySet(DemandProperties.assetType, db.getDemandMask(_demandId))){
            var (, , assettypeDemand, ,,,, ) = db.getDemandPriceDriving(_demandId);
            if(AssetProducingRegistryLogic.AssetType(assettypeDemand) != AssetProducingRegistryLogic(cooContract.assetProducingRegistry()).getAssetType( _prodAssetId))
                return (false, "wrong asset type");
        }
        return (true, "");
    }

    /// @notice internal helper function to check if the demand exists and the sender has the right role
    /// @param _demandId the demandid
    function checking(uint _demandId)
        internal
        view
    {
        require(!db.demandExists(_demandId));
        require(isRole(RoleManagement.Role.AgreementAdmin, msg.sender)); 
    }

    /// @notice function to check the location
    /// @param _demandId the demand-id
    /// @param _prodAssetId the production-asset id
    /// @return the bool-flag for check and error-message
    function checkLocation(uint _demandId, uint _prodAssetId)
        internal 
        view returns (bool, string)
    {
        if(hasDemandPropertySet(DemandProperties.country, db.getDemandMask(_demandId))){
            var (countryAsset, regionAsset, , , , , ) = AssetProducingRegistryLogic(cooContract.assetProducingRegistry()).getAssetLocation( _prodAssetId);
            var (locationCountryDemand, locationRegionDemand, , , , ) = db.getDemandPriceDriving(_demandId);
        
            if(locationCountryDemand != countryAsset)
                return (false, "wrong country");

            if(hasDemandPropertySet(DemandProperties.region, db.getDemandMask(_demandId))){
                if(locationRegionDemand != regionAsset)
                    return (false, "wrong region");
            }
        }
        return (true,"");
    }

    /// @notice internal helper function to check green attributes
    /// @param _demandId the demandId
    /// @param _prodAssetId the id of the producing asset
    /// @return true if the attributes are matching
    function checkGreenAttributes(uint _demandId, uint _prodAssetId)
        internal
        view
        returns(bool)
    {
        var ( , , , , , demandGreenAttribute, , ) = db.getDemandPriceDriving(_demandId);
        var ( , , , , , , assetGreenAttribute,) = AssetProducingRegistryLogic(cooContract.assetProducingRegistry()).getAssetProducingProperties(_prodAssetId);

        return(demandGreenAttribute == assetGreenAttribute );
    }

    /// @notice internal helper function to check the type of public support
    /// @param _demandId the id of the demand
    /// @param _prodAssetId the id of the producing asset
    /// @return true if the green attributes are matching
    function checkTypeOfPublicSupport(uint _demandId, uint _prodAssetId)
        internal
        view 
        returns (bool)
    {
        var ( , , , , , ,demandTypeOfPublicSupport , ) = db.getDemandPriceDriving(_demandId);

        var ( , , , , , , ,assetTypeOfPublicSupport) = AssetProducingRegistryLogic(cooContract.assetProducingRegistry()).getAssetProducingProperties(_prodAssetId);

        return(demandTypeOfPublicSupport == assetTypeOfPublicSupport);
    }

    /// @notice internal function to create a coupling
    /// @param _demandId demand-id
    /// @param _prodAsset production-AssetId, gets only checked if the flag in the demand-Bitmask is set
    /// @param _consAsset consuming-AssetId, gets only checked if the flag in the demand-Bitmask is set
    function createCouplingInternal(uint _demandId, uint _prodAsset, uint _consAsset, uint _demandMask)
        internal
    {
        if(hasDemandPropertySet(DemandProperties.producing, _demandMask)){
            require(AssetProducingRegistryLogic(address(cooContract.assetProducingRegistry())).getActive((_prodAsset)));
        }

        if(hasDemandPropertySet(DemandProperties.consuming, _demandMask)){
            require(AssetConsumingRegistryLogic(address(cooContract.assetConsumingRegistry())).getActive((_consAsset)));
        }
         db.createCoupling(_demandId, _prodAsset, _consAsset);
    }

    /// @notice internal function to create a demand
    /// @param _demandId the demand-Id
    /// @param _originator the originator (can be set)
    /// @param _buyer the buyer, has to bet set
    /// @param _startTime starttime of the demand
    /// @param _endTime endtime of the demand
    /// @param _tf timeframe 
    /// @param _pricePerCertifiedKWh price per certified KWh
    /// @param _currency used currency
    function createGeneralDemandInternal( 
        uint _demandId,
        address _originator,
        address _buyer,
        uint _startTime,   
        uint _endTime,
        TimeFrame _tf,     
        uint _pricePerCertifiedKWh,
        Currency _currency)
        internal
    {
        db.createGeneralDemand(_demandId, _originator, _buyer, _startTime, _endTime, uint(_tf), _pricePerCertifiedKWh, uint(_currency));
    }

    /// @notice function to match produced energy with the needed demand
    /// @param _demandId identifier of the demand
    /// @param _wCreated amount of Wh created
    /// @param _prodAssetId asset-Id that produced the energy
    function matchDemand(uint _demandId, uint _wCreated, uint _prodAssetId)
        external 
        isInitialized
    {   
        var (owner, currentWhPerPeriod, certInCurrentPeriod, currentPeriod) = matchInternal(_demandId, _wCreated, _prodAssetId, 0);
        // all the criteria are matched, so we can create the certificate 
        uint certId = CertificateLogic(address(cooContract.certificateRegistry())).createCertificate(_prodAssetId, owner, _wCreated);
         
        // at the end we have to update the matcher-properties 
        db.updateMatchProperties(_demandId, currentWhPerPeriod, certInCurrentPeriod, currentPeriod);
        LogMatcherPropertiesUpdate(_demandId, currentWhPerPeriod, certInCurrentPeriod, currentPeriod, certId);

        // there is a consuming activated, so we have to write the new amount of consumed energy into the asset information
        if(hasDemandPropertySet(DemandProperties.consuming, db.getDemandMask(_demandId))){
            writeConsumingEnergy(_demandId, _wCreated, currentPeriod);
        }
    }

    /// @notice function to write the consumed energy into the asset
    /// @param _demandId the demandId
    /// @param _wCreated the amount of energy created / consumed
    /// @param _currentPeriod the current period
    function writeConsumingEnergy(uint _demandId, uint _wCreated, uint _currentPeriod)
        internal
        isInitialized
    {
        var( , , , lastPeriod, ) = db.getDemandMatcherProperties(_demandId);
        var (, consAsset ) = db.getDemandCoupling(_demandId);

        if (_currentPeriod == lastPeriod) {     
            var(,,currentConsumption) = AssetConsumingRegistryLogic(address(cooContract.assetConsumingRegistry())).getConsumingProperies(consAsset);
            AssetConsumingRegistryLogic(address(cooContract.assetConsumingRegistry())).setConsumptionForPeriode(consAsset,_wCreated+currentConsumption);
        } else {
            AssetConsumingRegistryLogic(address(cooContract.assetConsumingRegistry())).setConsumptionForPeriode(consAsset,_wCreated);
        }
    }
    

}