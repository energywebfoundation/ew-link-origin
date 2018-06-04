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

/// @title this interface defines the functions that both consuming and producing assets are sharing
interface AssetDbInterface {
   
    function getActive(uint _assetId) external view returns(bool);
    function getExistStatus(uint _assetId) external view returns (bool general, bool location, bool asset);
    function createAsset() external returns (uint);
    function initLocation(uint _assetId, bytes32 _country, bytes32 _region, bytes32 _zip, bytes32 _city, bytes32 _street, bytes32 _houseNumber, bytes32 _gpsLatitude, bytes32 _gpsLongitude) external;
    function setActive(uint _assetId, bool _active) external;
    function setAssetExistStatus(uint _assetId, bool _exist) external;
    function setCapacityWh(uint _assetId, uint _capacityWh) external;
    function setLastSmartMeterReadDate(uint _assetId, uint _timestamp) external;
    function setLastSmartMeterReadFileHash(uint _assetId, bytes32 _lastSmartMeterReadFileHash) external;
    function setSmartMeter(uint _assetId, address _smartMeter) external;
    function getAssetListLength() external view returns (uint);
    function getAssetLocation(uint _assetId) external view returns(bytes32 country, bytes32 region, bytes32 zip, bytes32 city, bytes32 street, bytes32 houseNumber, bytes32 gpsLatitude, bytes32 gpsLongitude);
    function getLastSmartMeterRead(uint _assetId) external returns (uint);
    function getLastSmartMeterReadDate(uint _assetId) external returns(uint);
    function getLastSmartMeterReadFileHash(uint _assetId) external view returns(bytes32);
    }