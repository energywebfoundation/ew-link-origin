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
// @authors: slock.it GmbH, Jonas Bentke, jonas.bentke@slock.it

pragma solidity ^0.4.18;

import "./AssetProducingRegistryDB.sol";
import "./UserLogic.sol";
import "./CoO.sol";
import "./RoleManagement.sol";
import "./CertificateLogic.sol";
import "./Updatable.sol";
import "./AssetLogic.sol";


/// @title The logic contract for the asset registration
/// @notice This contract provides the logic that determines how the data is stored
/// @dev Needs a valid AssetProducingRegistryDB contract to function correctly
contract AssetProducingRegistryLogic is AssetLogic {

    event LogNewMeterRead(uint indexed _assetId, bytes32 indexed _fileHash, uint _oldMeterRead, uint _newMeterRead, bool _smartMeterDown, uint _certificatesCreatedForWh, uint _oldCO2OffsetReading, uint _newCO2OffsetReading, bool _serviceDown);
    
    enum AssetType {
        Wind,
        Solar,
        RunRiverHydro,
        BiomassGas
    }

    enum Compliance{
        none,
        IREC,
        EEC,
        TIGR
    }

    /// @notice Constructor
    /// @param _cooContract The address of the coo contract
    function AssetProducingRegistryLogic(CoO _cooContract) 
        public
        RoleManagement(_cooContract) 
    {
  
    }

    /// @notice Sets the general information of an asset in the database
    /// @param _assetId the The index / identifier of an asset
    /// @param _smartMeter The address of the smart meter
    /// @param _owner The address of the asset owner
    /// @param _operationalSince the timestamp of when the asset was activated for production
    /// @param _active true if active
    function initGeneral(
        uint _assetId, 
        address _smartMeter,
        address _owner,
        uint _operationalSince,
        bool _active
    ) 
        external
        isInitialized
        userHasRole(RoleManagement.Role.AssetManager, _owner)
        onlyRole(RoleManagement.Role.AssetAdmin)
    {  
        AssetProducingRegistryDB((db)).initGeneral(_assetId, _smartMeter, _owner, _operationalSince,0, _active, 0x0);
        checkForFullAsset(_assetId);
    }
    
    /// @notice sets the producing properties of an asset
    /// @param _assetId the id belonging to an asset
    /// @param _assetType the asset-type
    /// @param _capacityWh the capacity of the asset
    /// @param _registryCompliance the compliance
    /// @param _otherGreenAttributes other green attributes
    /// @param _typeOfPublicSupport type of public support
    function initProducingProperties(
        uint _assetId,
        AssetType _assetType,
        uint _capacityWh,
        Compliance _registryCompliance,
        bytes32 _otherGreenAttributes,
        bytes32 _typeOfPublicSupport
    )
        external
        isInitialized
        onlyRole(RoleManagement.Role.AssetAdmin)
    {
        AssetProducingRegistryDB((db)).initProducing(_assetId, uint(_assetType), 0, 0, _capacityWh, 0, uint(_registryCompliance), _otherGreenAttributes, _typeOfPublicSupport);
        checkForFullAsset(_assetId);

    }

    /// @notice Logs meter read
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _newMeterRead The current meter read of the asset
    /// @param _smartMeterDown flag if there was an error with the smart meter
    /// @param _lastSmartMeterReadFileHash Last meter read file hash
    /// @param _CO2OffsetServiceDown flag if there was an error with the co2-offset-server
    /// @dev The client needs to check if the blockgas limit could be reached and if so the log should be splitted 
    function saveSmartMeterRead(
        uint _assetId, 
        uint _newMeterRead, 
        bool _smartMeterDown, 
        bytes32 _lastSmartMeterReadFileHash, 
        uint _CO2OffsetMeterRead, 
        bool _CO2OffsetServiceDown 
    ) 
        external
        isInitialized
        onlyAccount(AssetProducingRegistryDB(db).getSmartMeter(_assetId))
    {
        require(db.getActive(_assetId));

     
        LogNewMeterRead(_assetId, _lastSmartMeterReadFileHash, AssetProducingRegistryDB(db).getLastSmartMeterReadWh(_assetId), _newMeterRead, _smartMeterDown, AssetProducingRegistryDB(db).getCertificatesCreatedForWh(_assetId), AssetProducingRegistryDB(db).getlastSmartMeterCO2OffsetRead(_assetId), _CO2OffsetMeterRead, _CO2OffsetServiceDown);
        /// @dev need to check if new meter read is higher then the old one
        AssetProducingRegistryDB(db).setLastSmartMeterReadFileHash(_assetId, _lastSmartMeterReadFileHash);
        AssetProducingRegistryDB(db).setLastSmartMeterReadWh(_assetId, _newMeterRead);
        AssetProducingRegistryDB(db).setLastCO2OffsetReading(_assetId,_CO2OffsetMeterRead);
        db.setLastSmartMeterReadDate(_assetId,now);
    }

    /// @notice function to set the amount of CO2 used for certificates
    /// @param _assetId the assetId
    /// @param _co2 the amount of CO2 saved
    function setCO2UsedForCertificate(uint _assetId, uint _co2)
        external 
        isInitialized
        onlyAccount(address(cooContract.certificateRegistry()))
    {
        uint currentCO = AssetProducingRegistryDB(address(db)).getCo2UsedForCertificate(_assetId);
        uint fullCO = AssetProducingRegistryDB(address(db)).getlastSmartMeterCO2OffsetRead(_assetId);
        uint temp = currentCO + _co2;
        
        // we have to check that we can only account that amount of CO2 that was actually saved
        require(temp <= fullCO);
        AssetProducingRegistryDB(address(db)).setCO2UsedForCertificate(_assetId, temp);
    }

   
    /// @notice increases the amount of wh used for the creation of certificates
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _whUsed The amount of wh that is about to be used for a new certificate
    function useWhForCertificate(uint _assetId, uint _whUsed) 
        external
        isInitialized 
        onlyAccount(address(cooContract.certificateRegistry()))
        returns(bool)
    {
        uint temp = AssetProducingRegistryDB(address(db)).getCertificatesCreatedForWh(_assetId) + _whUsed;
        require(AssetProducingRegistryDB(address(db)).getLastSmartMeterReadWh(_assetId) >= temp);
        AssetProducingRegistryDB(address(db)).setCertificatesCreatedForWh(_assetId, temp);
        return true;
    }

    /// @notice Gets the general information of an asset
    /// @param _assetId the id belonging to an entry in the asset registry
    /// @return the general information of an asset
    function getAssetGeneral(uint _assetId) 
        external
        constant
        returns(
            address _smartMeter,
            address _owner,
            uint _operationalSince,
            uint _lastSmartMeterReadWh,
            bool _active,
            bytes32 _lastSmartMeterReadFileHash
            )
    {
        return AssetProducingRegistryDB(address(db)).getAssetGeneral(_assetId);
    }

    /// @notice get the producing properties of an asset
    /// @param _assetId the id belonging to an entry in the asset registry
    /// @return the producing properties
    function getAssetProducingProperties(uint _assetId)
        external 
        view 
        returns(
            uint assetType,
            uint capacityWh,
            uint certificatesCreatedForWh,
            uint lastSmartMeterCO2OffsetRead,
            uint cO2UsedForCertificate,
            uint registryCompliance,
            bytes32 otherGreenAttributes,
            bytes32 typeOfPublicSupport
        )
    {
        return AssetProducingRegistryDB(address(db)).getAssetProducingProperties(_assetId);
    }
    /// @notice Function to get the Asset-Type
    /// @dev The asset-type gets converted from unsigned integer to an Asset-type enum, can still be accessed as uint
    /// @param _assetId The identifier / index of an asset
    /// @return AssetType as enum 
    function getAssetType(uint _assetId)
        external
        constant
        returns(
            AssetType 
        )
    {
        return AssetType(AssetProducingRegistryDB(address(db)).getAssetType(_assetId));
    }

    /// @notice function to get the compliance
    /// @param _assetId the assetId
    /// @return the compliance
    function getCompliance(uint _assetId)
        external
        constant 
        returns (Compliance c)
    {
        var ( , , , , , ctemp, , ) = AssetProducingRegistryDB(address(db)).getAssetProducingProperties(_assetId);
        c = Compliance(ctemp); 
    }

    /// @notice Function to get the amount of already used CO2 for creating certificates
    /// @param _assetId The identifier / index of an asset
    /// @return the amount of already used CO2 for creating certificates
    function getCo2UsedForCertificate(uint _assetId) 
        external 
        view 
        returns (uint) 
    {
        return AssetProducingRegistryDB(address(db)).getCo2UsedForCertificate(_assetId);
    }

    /// @notice function to calculated how much CO2-offset can be used for a certificate
    /// @param _assetId The identifier / index of an asset
    /// @param _wh The amount of wh produced
    /// @return amount of CO2-offset used for a certificate
    function getCoSaved(uint _assetId, uint _wh) external view returns(uint) {
        uint lastRead = AssetProducingRegistryDB(address(db)).getLastSmartMeterReadWh(_assetId);
        uint lastUsedWh = AssetProducingRegistryDB(address(db)).getCertificatesCreatedForWh(_assetId);
        uint availableWh = lastRead - lastUsedWh;
       
        // we have to check for an underflow and if there are even availale Wh
        assert(lastUsedWh <= lastRead);
        if(availableWh == 0) return 0;

        uint coRead = AssetProducingRegistryDB(address(db)).getlastSmartMeterCO2OffsetRead(_assetId);
        uint coUsed = AssetProducingRegistryDB(address(db)).getCo2UsedForCertificate(_assetId);
        uint availableCo = coRead - coUsed;
        assert(coUsed <= coRead);
        return (availableCo*((_wh*1000000)/availableWh))/1000000;
    }
}