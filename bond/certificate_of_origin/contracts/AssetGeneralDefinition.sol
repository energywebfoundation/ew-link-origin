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

import "./Owned.sol";
import "./LocationDefinition.sol";

/// @title this contracts provides those functions that both consuming and producing assets share
contract AssetGeneralDefinition is Owned {

   struct GeneralInformation {
        address smartMeter;
        address owner;
        uint operationalSince;
        uint lastSmartMeterReadWh;
        bool active;
        bytes32 lastSmartMeterReadFileHash;
        uint lastMeterReadReceived;
        bool exists;
    }

    /// @notice function to set all the location Informations for an asset, gets called internally
    /// @param _loc the storage location of the location informations
    /// @param _country The country where the asset is located
    /// @param _region The region / state where the asset is located
    /// @param _zip The zip-code of the region where the asset is located
    /// @param _city The city where the asset is located
    /// @param _street The streetname where the asset is located
    /// @param _houseNumber the housenumber where the asset is located
    /// @param _gpsLatitude The gps-latitude
    /// @param _gpsLongitude The gps-longitude
    function initLocationInternal(
        LocationDefinition.Location storage _loc,
        bytes32 _country,
        bytes32 _region,
        bytes32 _zip,
        bytes32 _city,
        bytes32 _street,
        bytes32 _houseNumber,
        bytes32 _gpsLatitude,
        bytes32 _gpsLongitude
    )
        internal
    {
        _loc.country = _country;
        _loc.region = _region;
        _loc.zip = _zip;
        _loc.city = _city;
        _loc.street = _street;
        _loc.houseNumber = _houseNumber;
        _loc.gpsLatitude = _gpsLatitude;
        _loc.gpsLongitude = _gpsLongitude;
        _loc.exists = true;
    }

    /// @notice internal function to set the general information
    /// @param _gi storage location of the general information
    /// @param _smartMeter smartMeter-address
    /// @param _owner owner-of the asset
    /// @param _operationalSince operatinal since that timestamp
    /// @param _lastSmartMeterReadWh the last meterreading in Wh
    /// @param _active flag if the asset is active
    /// @param _lastSmartMeterReadFileHash the last filehash 
    function setGeneralInformationInternal(
        GeneralInformation storage _gi,
        address _smartMeter,
        address _owner,
        uint _operationalSince,
        uint _lastSmartMeterReadWh,
        bool _active,
        bytes32 _lastSmartMeterReadFileHash
    )
    internal 
    {
        _gi.smartMeter = _smartMeter;
        _gi.owner = _owner;
        _gi.operationalSince = _operationalSince;
        _gi.lastSmartMeterReadWh = _lastSmartMeterReadWh;
        _gi.active = _active;
        _gi.lastSmartMeterReadFileHash = _lastSmartMeterReadFileHash;
        _gi.lastMeterReadReceived = 0;
        _gi.exists = true;
    }

    /// @notice function to get the informations about the location of a struct
    /// @param _loc storage location of the locationInformations
    /// @return country, region, zip, city, street, houseNumber, gpsLatitude, gpsLongitude
    function getAssetLocationInternal(LocationDefinition.Location storage _loc)
        internal
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
        country = _loc.country;
        region = _loc.region;
        zip = _loc.zip;
        city = _loc.city;
        street = _loc.street;
        houseNumber = _loc.houseNumber;
        gpsLatitude = _loc.gpsLatitude;
        gpsLongitude = _loc.gpsLongitude;

        return (country, region, zip, city, street, houseNumber, gpsLatitude, gpsLongitude);
    }

}