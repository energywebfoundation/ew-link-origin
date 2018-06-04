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
// @authors: slock.it GmbH, Martin Kuechler, martin.kuechler@slock.it

pragma solidity ^0.4.18;

import "./Owned.sol";
import "./LocationDefinition.sol";
import "./AssetGeneralDefinition.sol";
import "./AssetDbInterface.sol";

/// @title The Database contract for the Asset Registration
/// @notice This contract only provides getter and setter methods
contract AssetConsumingRegistryDB is Owned, AssetGeneralDefinition, AssetDbInterface {

    struct ConsumingProperties {
        uint capacityWh;
        bool maxCapacitySet;
        uint certificatesUsedForWh;
    }

    struct Asset {
        GeneralInformation general;
        ConsumingProperties consumingProps;
        LocationDefinition.Location location;
        bool exists;
    }


    /// @notice An array containing all registerd assets
    Asset[] private assets;

    /// @dev empty structs for initializing, used to avoid compile warnings
    GeneralInformation generalEmpty;
    LocationDefinition.Location locationEmpty;
    ConsumingProperties consumingEmpty;

    /// @notice Constructor
    /// @param _owner The owner of the contract
    function AssetConsumingRegistryDB(address _owner) 
        public
        Owned(_owner) 
    {

    } 

    /// @notice functin to create a new empty asset
    /// @return returns the array-position and thus the index / identifier of this new asset
    function createAsset() 
        external
        onlyOwner
        returns (uint _assetId)
    {
        assets.push(AssetConsumingRegistryDB.Asset({
            general: generalEmpty,
            consumingProps: consumingEmpty,
            location: locationEmpty,
            exists: false
        }));
        _assetId = assets.length>0?assets.length-1:0;        

    }

    /// @notice Sets the general information for an asset
    /// @param _assetId The index / identifier for that asset
    /// @param _smartMeter The address of the smart meter
    /// @param _owner The address of the asset owner
    /// @param _operationalSince The timestamp since the asset is operational
    /// @param _capacityWh The capacity in Wh of the asset
    /// @param _lastSmartMeterReadWh The smart meter read in Wh
    /// @param _certificatesUsedForWh The amount of Wh used to issue certificates
    /// @param _active true if active
    /// @param _lastSmartMeterReadFileHash The last meter read file hash
    function initGeneral (       
            uint _assetId, 
            address _smartMeter,
            address _owner,
            uint _operationalSince,
            uint _capacityWh,
            bool _maxCapacitySet,
            uint _lastSmartMeterReadWh,
            uint _certificatesUsedForWh,
            bool _active,
            bytes32 _lastSmartMeterReadFileHash
        ) 
        onlyOwner
        external
    {
        Asset storage a = assets[_assetId];

        GeneralInformation storage gi = a.general; 
        ConsumingProperties storage cp = a.consumingProps;
        setGeneralInformationInternal(gi, _smartMeter, _owner, _operationalSince,_lastSmartMeterReadWh, _active, _lastSmartMeterReadFileHash);
   
        cp.certificatesUsedForWh = _certificatesUsedForWh;
        cp.capacityWh = _capacityWh;
        cp.maxCapacitySet = _maxCapacitySet;

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


    /// @notice Sets the capacity in Wh of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _capacityWh The capacity in Wh
    function setCapacityWh(uint _assetId, uint _capacityWh) 
        onlyOwner
        external
    {        
        assets[_assetId].consumingProps.capacityWh = _capacityWh;
    }

    /// @notice Sets amount of Wh used to issue certificates belonging to an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @param _certificatesUsedForWh The amount of Wh used to issue certificates
    function setCertificatesUsedForWh(uint _assetId, uint _certificatesUsedForWh) 
        onlyOwner
        external
    {
        assets[_assetId].consumingProps.certificatesUsedForWh = _certificatesUsedForWh;
    }

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

    /// @notice Gets the general information of an asset
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return general information of an asset
    function getAssetGeneral(uint _assetId) 
        onlyOwner
        external
        view
        returns(
            address _smartMeter,
            address _owner,
            uint _operationalSince,
            uint _capacityWh,
            bool _maxCapacitySet,
            uint _lastSmartMeterReadWh,
            uint _certificatesUsedForWh,
            bool _active,
            bytes32 _lastSmartMeterReadFileHash
            )
    {
        Asset storage asset = assets[_assetId];
        GeneralInformation storage gi = asset.general;
        ConsumingProperties storage cp = asset.consumingProps;

        _smartMeter = gi.smartMeter;
        _owner = gi.owner;
        _operationalSince = gi.operationalSince;
        _capacityWh = cp.capacityWh;
        _maxCapacitySet = cp.maxCapacitySet;
        _lastSmartMeterReadWh = gi.lastSmartMeterReadWh;
        _certificatesUsedForWh = cp.certificatesUsedForWh;
        _active = gi.active;
        _lastSmartMeterReadFileHash = gi.lastSmartMeterReadFileHash;
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

    /// @notice Gets the capacity in Wh of an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return the capacity in Wh
    function getCapacityWh(uint _assetId)
        onlyOwner
        external
        view
        returns(uint)
    {
        return assets[_assetId].consumingProps.capacityWh;
    }

    /// @notice Gets amount of Wh used to issue certificates belonging to an entry in the asset registry
    /// @param _assetId The id belonging to an entry in the asset registry
    /// @return the amount of Wh used to issue certificates
    function getCertificatesUsedForWh(uint _assetId)
        onlyOwner
        external
        view
        returns(uint)
    {
        return assets[_assetId].consumingProps.certificatesUsedForWh;
    }

    /// @notice gets the consuming properties of an asset
    /// @param _assetId the id belonging to an entry in the asset registry
    /// @return the consuming properteis
    function getConsumingProperies(uint _assetId) 
        onlyOwner
        external
        view
        returns (
            uint _capacityWh,
            bool _maxCapacitySet,
            uint _certificatesUsedForWh
        )
    {
        ConsumingProperties storage c = assets[_assetId].consumingProps;
        _capacityWh = c.capacityWh;
        _maxCapacitySet = c.maxCapacitySet;
        _certificatesUsedForWh = c.certificatesUsedForWh;
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
        return(a.general.exists, a.location.exists, a.exists);
    }

    /// @notice function to retrieve the last smartmeter-reading of an asset
    /// @param _assetId the asset-id
    /// @return the last smartmeter-reading
    function getLastSmartMeterRead(uint _assetId) 
        onlyOwner
        external 
        returns (uint)
    {
        return assets[_assetId].general.lastSmartMeterReadWh;
    }

    /// @notice function to retrieve the timestamp of the last smartmeter-reading
    /// @param _assetId the asset-id
    /// @return the timestamp of the last smartmeter-reading
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