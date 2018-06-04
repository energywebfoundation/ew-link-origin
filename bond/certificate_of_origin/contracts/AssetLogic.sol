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

pragma solidity ^0.4.17;

import "./RoleManagement.sol";
import "./Updatable.sol";
import "./AssetDbInterface.sol";

/// @title Contract for storing the current logic-contracts-addresses for the certificate of origin
contract AssetLogic is RoleManagement, Updatable {

    event LogAssetCreated(address sender, uint indexed _assetId);
    event LogAssetFullyInitialized(uint indexed _assetId);
    event LogAssetSetActive(uint indexed _assetId);
    event LogAssetSetInactive(uint indexed _assetId);

    AssetDbInterface public db;

    modifier isInitialized {
        require(address(db) != 0x0);
        _;
    }

    /// @notice function to create a new empty asset, triggers event with created AssetID. To actually create an Asset the functions initGeneral and initLocations have to be called
    function createAsset() 
        external
        onlyRole(RoleManagement.Role.AssetAdmin)
     {
        uint assetId = db.createAsset();
        LogAssetCreated(msg.sender, assetId);
    }

    /// @notice function toinizialize the database, can only be called once
    /// @param _dbAddress address of the database contract
    function init(address _dbAddress) 
        public
        onlyRole(RoleManagement.Role.TopAdmin)
    {
        require(address(db) == 0x0);
        db = AssetDbInterface(_dbAddress);
    }

    /// @notice Sets the location information of an asset in the database
    /// @param _assetId the The index / identifier of an asset
    /// @param _country The country where the asset is located
    /// @param _region The region where the asset is located
    /// @param _zip The zip coe where the asset is located
    /// @param _city The city where the asset is located
    /// @param _street The street where the asset is located
    /// @param _houseNumber The house number where the asset is located
    /// @param _gpsLatitude The gps-latitude of the asset
    /// @param _gpsLongitude The gps-longitude of the asset 
    function initLocation (
        uint _assetId,
        bytes32 _country,
        bytes32 _region,
        bytes32 _zip,
        bytes32 _city,
        bytes32 _street,
        bytes32 _houseNumber,
        bytes32 _gpsLatitude,
        bytes32 _gpsLongitude
    )
        external 
        isInitialized
        onlyRole(RoleManagement.Role.AssetAdmin)
    {
        db.initLocation(_assetId, _country, _region, _zip, _city, _street, _houseNumber, _gpsLatitude, _gpsLongitude);
         checkForFullAsset(_assetId);
    }

    /// @notice Sets active to false
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _active flag if the asset is asset or not
    function setActive(uint _assetId, bool _active)
        external
        isInitialized
        onlyRole(RoleManagement.Role.AssetAdmin)
    {
       
        db.setActive(_assetId, _active);
        if (_active) {
            LogAssetSetActive(_assetId);
        } else {
            LogAssetSetInactive(_assetId);
        } 
    }

    /// @notice Updates the logic contract
    /// @param _newLogic Address of the new logic contract
    function update(address _newLogic) 
        external
        onlyAccount(address(cooContract))
    {
        Owned(db).changeOwner(_newLogic);
    }

    /// @notice gets the active flag on an asset
    /// @param _assetId the assetId
    /// @return the active flag
    function getActive(uint _assetId)
        external
        view
        returns (bool)
    {
        return db.getActive(_assetId);
    }

    /// @notice Gets the last filehash of the smart reader
    /// @param _assetId the assetId
    /// @return the alst smartmeterread-filehash
    function getLastSmartMeterReadFileHash(uint _assetId)
        external
        view
        returns (bytes32 datalog)
    {
        return db.getLastSmartMeterReadFileHash(_assetId);
    }

    /// @notice Function to get the amount of all assets
    /// @dev needed to iterate though all the asset
    /// @return the amount of all assets
    function getAssetListLength()
        external
        view 
        returns (uint)
    {
        return db.getAssetListLength();
    }

    /// @notice Funtion to get the informaiton of the location of an asset
    /// @param _assetId The identifier / index of the asset
    /// @return country, region, zip-code, city, street, houseNumber, gpsLatitude, gpsLongitude
    function getAssetLocation(uint _assetId)
        external
        view
        returns(
            bytes32 country,
            bytes32 region,
            bytes32 zip,
            bytes32 city,
            bytes32 street,
            bytes32 houseNumber,
            bytes32 gpsLatitude,
            bytes32 gpsLongitude
        )
    {
        return db.getAssetLocation(_assetId);
    }

    /// @notice Checks if a fully Asset-struct is created, enabled if asset all information are there
    /// @dev only for internal use
    /// @param _assetId the The index / identifier of an asset
    function checkForFullAsset(uint _assetId)
        internal
    {
        var (general, location, asset) = db.getExistStatus(_assetId);

        if(general && location && !asset) {
            db.setAssetExistStatus(_assetId,true);
            LogAssetFullyInitialized(_assetId);
            db.setLastSmartMeterReadDate(_assetId, now);
        }
    }

    /// @notice Changes the address of a smart meter belonging to an asset
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _newSmartMeter The address of the new smart meter
    function updateSmartMeter(uint _assetId, address _newSmartMeter)
        external
        isInitialized
        onlyRole(RoleManagement.Role.AssetAdmin)
    {
        db.setSmartMeter(_assetId, _newSmartMeter);
    }

}