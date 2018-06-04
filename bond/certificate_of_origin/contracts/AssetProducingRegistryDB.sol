// Copyright 2018 Energy Web Foundation
//
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
// @authors: slock.it GmbH, Heiko Burkhardt, heiko.burkhardt@slock.it

pragma solidity ^0.4.18;

import "./LocationDefinition.sol";
import "./AssetGeneralDefinition.sol";
import "./AssetDbInterface.sol";

/// @title The Database contract for the Asset Registration
/// @notice This contract only provides getter and setter methods
contract AssetProducingRegistryDB is AssetGeneralDefinition, AssetDbInterface {

    struct ProducingProperties {
        uint assetType;
        uint capacityWh;
        uint certificatesCreatedForWh;
        uint lastSmartMeterCO2OffsetRead;
        uint cO2UsedForCertificate;
        uint registryCompliance;
        bytes32 otherGreenAttributes;
        bytes32 typeOfPublicSupport;
    }

    struct Asset {
        AssetGeneralDefinition.GeneralInformation general;
        ProducingProperties producingProps;
        LocationDefinition.Location location;
        bool exists;
    }


    /// @notice An array containing all registerd assets
    Asset[] private assets;

    /// @dev empty structs for initializing, used to avoid compile warnings
    AssetGeneralDefinition.GeneralInformation generalEmpty;
    LocationDefinition.Location locationEmpty;
    ProducingProperties producingEmpty;

    /// @notice Constructor
    /// @param _owner The owner of the contract
    function AssetProducingRegistryDB(address _owner) 
        public
        Owned(_owner) 
    {

    } 

    /// @notice function to create a new empty asset
    /// @return returns the array-position and thus the index / identifier of this new asset
    function createAsset() 
        external
        onlyOwner
        returns (uint _assetId)
    {
        assets.push(AssetProducingRegistryDB.Asset({
            general: generalEmpty,
            producingProps: producingEmpty,
            location: locationEmpty,
            exists: false
        }));
       _assetId = assets.length>0?assets.length-1:0;        
    }

    /// @notice function to set the general information for an asset
    /// @param _assetId the ID belonging to the asset
    /// @param _smartMeter the smart-meter address
    /// @param _owner the owner of the asset
    /// @param _operationalSince timestamp of when the asset started producing energy
    /// @param _lastSmartMeterReadWh the last reading of the smartmeter
    /// @param _active active-flag
    /// @param _lastSmartMeterReadFileHash the last filehash of the smartmeter-readings
    function initGeneral(       
            uint _assetId, 
            address _smartMeter,
            address _owner,
            uint _operationalSince,
            uint _lastSmartMeterReadWh,
            bool _active,
            bytes32 _lastSmartMeterReadFileHash
        ) 
        onlyOwner
        external
    {
        Asset storage a = assets[_assetId];

        setGeneralInformationInternal(a.general, _smartMeter, _owner, _operationalSince,_lastSmartMeterReadWh, _active, _lastSmartMeterReadFileHash);

    }

    /// @notice function to set the producing-properties of an asset
    /// @param _assetId the ID belonging to the asset
    /// @param _assetType the assetType of the asset 
    /// @param _lastSmartMeterCO2OffsetRead the last CO2-Offsetreading of the smartmeter
    /// @param _capacityWh the capacity of the asset in Wh
    /// @param _certificatesCreatedForWh the amount of Wh already certificated
    /// @param _registryCompliance the registry-compliance
    /// @param _otherGreenAttributes other green attributes
    /// @param _typeOfPublicSupport type of public support
    function initProducing(
        uint _assetId,
        uint _assetType, 
        uint _lastSmartMeterCO2OffsetRead,
        uint _cO2UsedForCertificate,
        uint _capacityWh,
        uint _certificatesCreatedForWh,
        uint _registryCompliance,
        bytes32 _otherGreenAttributes,
        bytes32 _typeOfPublicSupport
        )
    onlyOwner
    external
    {
        Asset storage a = assets[_assetId];
        a.producingProps.assetType = _assetType;
        a.producingProps.lastSmartMeterCO2OffsetRead = _lastSmartMeterCO2OffsetRead;
        a.producingProps.cO2UsedForCertificate = _cO2UsedForCertificate;
        a.producingProps.certificatesCreatedForWh = _certificatesCreatedForWh;
        a.producingProps.capacityWh = _capacityWh;
        a.producingProps.registryCompliance = _registryCompliance;       
        a.producingProps.otherGreenAttributes = _otherGreenAttributes;
        a.producingProps.typeOfPublicSupport = _typeOfPublicSupport; 
    }

    /// @notice function to set all the location Informations for an asset
    /// @param _assetId The identifier / index of an asset
    /// @param _country The country where the asset is located
    /// @param _region The region / state where the asset is located
    /// @param _zip The zip-code of the region where the asset is located
    /// @param _city The city where the asset is located
    /// @param _street The streetname where the asset is located
    /// @param _houseNumber the housenumber where the asset is located
    /// @param _gpsLatitude The gps-latitude
    /// @param _gpsLongitude The gps-longitude
    function initLocation(
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
        onlyOwner
        external
    {
        LocationDefinition.Location storage loc = assets[_assetId].location;
        initLocationInternal(loc,_country,_region,_zip,_city,_street,_houseNumber,_gpsLatitude,_gpsLongitude);
    }

    /// @notice Sets if an entry in the asset registry is active
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _active true if active
    function setActive(uint _assetId, bool _active) 
        onlyOwner
        external
    {
        assets[_assetId].general.active = _active;
    }

    /// @notice function to set the existing status of an asset
    /// @param _assetId The index position / identifier of an asset
    /// @param _exist flag if the asset should exist
    function setAssetExistStatus(uint _assetId, bool _exist)
        external
        onlyOwner
    {
        Asset storage a = assets[_assetId];
        a.exists = _exist;
    }

    /// @notice Sets the fuel type belonging to an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _assetType The new fuel type
    function setAssetType(uint _assetId, uint _assetType) 
        onlyOwner
        external
    {
        assets[_assetId].producingProps.assetType = _assetType;
    }

    /// @notice Sets the capacity in Wh of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _capacityWh The capacity in Wh
    function setCapacityWh(uint _assetId, uint _capacityWh) 
        onlyOwner
        external
    {
        assets[_assetId].producingProps.capacityWh = _capacityWh;
    }

    /// @notice Sets amount of Wh used to issue certificates belonging to an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _certificatesCreatedForWh The amount of Wh used to issue certificates
    function setCertificatesCreatedForWh(uint _assetId, uint _certificatesCreatedForWh) 
        onlyOwner
        external
    {
        assets[_assetId].producingProps.certificatesCreatedForWh = _certificatesCreatedForWh;
    }

    /// @notice Sets amount of saved CO2 used to issue certificates belonging to an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _used The amount of saved CO2 used to issue certificates
    function setCO2UsedForCertificate(uint _assetId, uint _used) 
        onlyOwner 
        external 
    {
        assets[_assetId].producingProps.cO2UsedForCertificate = _used;
    }
    
    /// @notice Sets the last smart meter read in saved CO2 of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _lastCO2OffsetReading The new amount of saved CO2
    function setLastCO2OffsetReading(uint _assetId, uint _lastCO2OffsetReading)
        onlyOwner
        external
    {
        assets[_assetId].producingProps.lastSmartMeterCO2OffsetRead = _lastCO2OffsetReading;
    }

    /// @notice Sets the timestamp of the last smartmeter-reading
    /// @param _assetId the id belonging to the asset 
    /// @param _timestamp the new timestamp of reading
    function setLastSmartMeterReadDate(uint _assetId, uint _timestamp)
        onlyOwner
        external
    {
        assets[_assetId].general.lastMeterReadReceived = _timestamp;
    }

    /// @notice Sets last meter read file hash
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _lastSmartMeterReadFileHash Last meter read file hash
    function setLastSmartMeterReadFileHash(uint _assetId, bytes32 _lastSmartMeterReadFileHash)
        onlyOwner
        external
    {
        assets[_assetId].general.lastSmartMeterReadFileHash = _lastSmartMeterReadFileHash;
    }

    /// @notice Sets the last smart meter read in Wh of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _lastSmartMeterReadWh The smart meter read in Wh
    function setLastSmartMeterReadWh(uint _assetId, uint _lastSmartMeterReadWh) 
        onlyOwner
        external
    {
        assets[_assetId].general.lastSmartMeterReadWh = _lastSmartMeterReadWh;
    }

    /// @notice Sets the location-country of an asset
    /// @param _assetId the id belonging to an entry in the asset registry
    /// @param _country the new country
    function setLocationCountry(uint _assetId, bytes32 _country)
        onlyOwner
        external
    {
        assets[_assetId].location.country = _country;
    }

    /// @notice Sets the location-region of an asset
    /// @param _assetId the id belonging to an entry in the asset registry
    /// @param _region the new region
    function setLocationRegion(uint _assetId, bytes32 _region)
        onlyOwner
        external
    {
        assets[_assetId].location.region = _region;
    }
    
    /// @notice Sets the operational since field of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _operationalSince The timestamp since the asset is operational
    function setOperationalSince(uint _assetId, uint _operationalSince) 
        onlyOwner
        external
    {
        assets[_assetId].general.operationalSince = _operationalSince;
    }

    /// @notice Sets the owner of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _owner The new owner
    function setOwner(uint _assetId, address _owner) 
        onlyOwner
        external
    {
        assets[_assetId].general.owner = _owner;
    }

    /// @notice Sets the smart meter address belonging to an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _smartMeter The new smart meter address
    function setSmartMeter(uint _assetId, address _smartMeter) 
        onlyOwner
        external
    {
        assets[_assetId].general.smartMeter = _smartMeter;
    }
    
    /// @notice Gets if an entry in the asset registry is active
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return true if asset is active
    function getActive(uint _assetId) 
        onlyOwner
        external
        view
        returns(bool)
    {
        return assets[_assetId].general.active;
    }

    /// @notice Returns the general information of an asset
    /// @param _assetId the id belonging to an entry in the asset registry
    /// @return smartmeter-address, owner-address, operationalSince, lastSmartMeterReading in Wh, active flag and the filehash of the last reading
    function getAssetGeneral(uint _assetId)
        onlyOwner
        external
        view 
        returns
        (
            address _smartMeter,
            address _owner,
            uint _operationalSince,
            uint _lastSmartMeterReadWh,
            bool _active,
            bytes32 _lastSmartMeterReadFileHash
        )
    {
       Asset storage asset = assets[_assetId];
         _smartMeter = asset.general.smartMeter;
        _owner = asset.general.owner;
        _operationalSince = asset.general.operationalSince;
        _lastSmartMeterReadWh = asset.general.lastSmartMeterReadWh;
        _active = asset.general.active;
        _lastSmartMeterReadFileHash = asset.general.lastSmartMeterReadFileHash;
    }

    /// @notice function to get the amount of assets
    /// @return amount of assets
    function getAssetListLength()
        external
        view
        onlyOwner 
        returns (uint)
    {
        return assets.length;
    }

    /// @notice function to get the informations about the location of a struct
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return country, region, zip, city, street, houseNumber, gpsLatitude, gpsLongitude
    function getAssetLocation(uint _assetId)
        onlyOwner
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
        LocationDefinition.Location storage loc = assets[_assetId].location;
        return getAssetLocationInternal(loc);

    }

    /// @notice function to get the producing-properties of an asset
    /// @param _assetId the id belonging to the asset
    /// @return returns the producing-properties of an asset
    function getAssetProducingProperties(uint _assetId)
        onlyOwner
        external
        view
        returns (
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
        Asset storage a = assets[_assetId];
        ProducingProperties storage pp = a.producingProps;

        assetType = pp.assetType;
        capacityWh = pp.capacityWh;
        certificatesCreatedForWh = pp.certificatesCreatedForWh;
        lastSmartMeterCO2OffsetRead = pp.lastSmartMeterCO2OffsetRead;
        cO2UsedForCertificate = pp.cO2UsedForCertificate;
        registryCompliance = pp.registryCompliance;
        otherGreenAttributes = pp.otherGreenAttributes;
        typeOfPublicSupport = pp.typeOfPublicSupport;
    }


    /// @notice Gets the asset type belonging to an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return the type of asset
    function getAssetType(uint _assetId)
        onlyOwner
        external
        view
        returns(uint)
    {
        return assets[_assetId].producingProps.assetType;
    }

    /// @notice Gets the capacity in Wh of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return the capacity in Wh
    function getCapacityWh(uint _assetId)
        onlyOwner
        external
        view
        returns(uint)
    {
        return assets[_assetId].producingProps.capacityWh;
    }

    /// @notice Gets amount of Wh used to issue certificates belonging to an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return the amount of Wh used to issue certificates
    function getCertificatesCreatedForWh(uint _assetId)
        onlyOwner
        external
        view
        returns(uint)
    {
        return assets[_assetId].producingProps.certificatesCreatedForWh;
    }


    /// @notice Gets the amount of already used CO2-offset for creating certificates
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return the aount of already used CO2-offset
    function getCo2UsedForCertificate(uint _assetId) 
        onlyOwner 
        external 
        view 
        returns (uint) 
    {
        return assets[_assetId].producingProps.cO2UsedForCertificate;
    }

    /// @notice function the retrieve the existing status of the general information, the location information and the asset itself
    /// @param _assetId The index position / identifier of the asset
    /// @return existing status of the general informaiton, existing status of the location informaiton and where the asset-structs exists
    function getExistStatus(uint _assetId)
        onlyOwner
        external 
        view
        returns (bool general, bool location, bool asset)
    {
        Asset storage a = assets[_assetId];
        return(a.general.exists && a.producingProps.capacityWh > 0, a.location.exists, a.exists);
    }

    /// @notice function to get the last smartmeter-reading of an asset
    /// @param _assetId the id belonging to the asset
    /// @return the last smartmeter-reading
    function getLastSmartMeterRead(uint _assetId) 
        onlyOwner
        external 
        returns (uint)
    {
        return assets[_assetId].general.lastSmartMeterReadWh;
    }

    /// @notice Gets the last CO2-offset read of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return the last logged CO2-offset read tru
    function getlastSmartMeterCO2OffsetRead(uint _assetId)
        onlyOwner
        external 
        view 
        returns (uint)
    {
        return assets[_assetId].producingProps.lastSmartMeterCO2OffsetRead;
    }
    
    /// @notice gets the timestamp of the last reading
    /// @param _assetId the Id belonging to an entry in the asset registry
    /// @return the timestamp of the last reading
    function getLastSmartMeterReadDate(uint _assetId)
        onlyOwner
        external
        returns(uint)
    {
        return assets[_assetId].general.lastMeterReadReceived;
    }

    /// @notice Gets last smart merter read file hash
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return last smart merter read file hash
    function getLastSmartMeterReadFileHash(uint _assetId)
        onlyOwner
        external
        view
        returns(bytes32)
    {
        return assets[_assetId].general.lastSmartMeterReadFileHash;
    }
    
    /// @notice Gets the last smart merter read in Wh of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return the last loged smart meter read in Wh
    function getLastSmartMeterReadWh(uint _assetId)
        onlyOwner
        external
        view
        returns(uint)
    {
        return assets[_assetId].general.lastSmartMeterReadWh;
    }

    /// @notice Gets the location country of an asset
    /// @param _assetId the id belonging to an entry in the asset registry
    /// @return country where the asset is based
    function getLocationCountry(uint _assetId)
        onlyOwner
        external
        view 
        returns(bytes32)
    {
        return assets[_assetId].location.country;
    }

    /// @notice Gets the location region of an asset
    /// @param _assetId the id belonging to an entry in the asset registry
    /// @return region of the country where the asset is based
    function getLocationRegion(uint _assetId)
        onlyOwner
        external
        constant
        returns(bytes32)
    {
        return assets[_assetId].location.region;
    }

    /// @notice Gets the operational since field of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    function getOperationalSince(uint _assetId)
        onlyOwner
        external
        constant
        returns(uint)
    {
        return assets[_assetId].general.operationalSince;
    }

    /// @notice Gets the owner of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return the owner address
    function getOwner(uint _assetId) 
        onlyOwner
        external
        constant
        returns(address)
    {
        return assets[_assetId].general.owner;
    }

    /// @notice Gets the smart meter address belonging to an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return the smart meter address
    function getSmartMeter(uint _assetId)
        onlyOwner
        external
        constant
        returns(address)
    {
        return assets[_assetId].general.smartMeter;
    }
    
}