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

pragma solidity ^0.4.17;

/// @title The logic contract for the Certificate of Origin list
/// @notice This contract provides the logic that determines how the data is stored
/// @dev Needs a valid CertificateDB contract to function correctly

import "./Owned.sol";
import "./RoleManagement.sol";
import "./UserDB.sol";
import "./CoO.sol";
import "./CertificateDB.sol";
import "./Updatable.sol";
import "./AssetProducingRegistryLogic.sol";

contract CertificateLogic is RoleManagement, Updatable {

    ///@notice The address of a CertificateDB contract
    CertificateDB public certificateDb;

    /// @notice Logs the creation of an event
    event LogCreatedCertificate(uint indexed _certificateId, uint powerInW, address owner, address escrow);
    /// @notice Logs the request of an retirement of a certificate
    event LogRetireRequest(uint indexed _certificateId, bool _retire);

    event LogCertificateOwnerChanged(uint indexed _certificateId, address _oldOwner, address _newOwner, address _oldEscrow, address _newEscrow);
    
    /// @notice Checks if the contract is initialized
    modifier isInitialized() {
        require(certificateDb != CertificateDB(0x0));
        _;
    }
    
    /// @notice Constructor
    /// @param _coo The Master contract
    function CertificateLogic(CoO _coo) RoleManagement(_coo) public {

    }

    /// @notice Initialises the contract by binding it to a logic contract
    /// @param _database Sets the logic contract
    function init(address _database) public onlyRole(RoleManagement.Role.TopAdmin) {
        require(certificateDb == CertificateDB(0x0));
        certificateDb = CertificateDB(_database);
    }

    /// @notice Creates a certificate of origin. Checks in the AssetRegistry if requested wh are available.
    /// @param _assetId The id of the Certificate
    /// @param _owner The owner of the Certificate
    /// @param _powerInW The amount of Watts the Certificate holds
    function createCertificate(uint _assetId, address _owner, uint _powerInW) 
        public 
        isInitialized
        onlyAccount(address(cooContract.demandRegistry()) )  
        returns (uint) 
    {
        return createCertificateIntern(_assetId, _owner, _powerInW, 0x0);
    }

    /// @notice Creates a certificate of origin. Checks in the AssetRegistry if requested wh are available.
    /// @param _assetId The id of the Certificate
    /// @param _owner The owner of the Certificate
    /// @param _powerInW The amount of Watts the Certificate holds
    function createCertificateIntern(uint _assetId, address _owner, uint _powerInW, address _escrow) 
        internal 
        isInitialized  
        returns (uint) 
    {
        uint co = AssetProducingRegistryLogic(address(cooContract.assetProducingRegistry())).getCoSaved(_assetId, _powerInW);
        require(AssetProducingRegistryLogic(address(cooContract.assetProducingRegistry())).useWhForCertificate(_assetId, _powerInW));
        bytes32 dataLog = AssetProducingRegistryLogic(address(cooContract.assetProducingRegistry())).getLastSmartMeterReadFileHash(_assetId);
        uint certId = certificateDb.createCertificate(_assetId, _owner, _powerInW, dataLog, co, _escrow);
        LogCreatedCertificate(certId, _powerInW, _owner, _escrow);
        AssetProducingRegistryLogic(address(cooContract.assetProducingRegistry())).setCO2UsedForCertificate(_assetId,co);
        return certId;
    }

    /// @notice Creates a certificate of origin for the asset owner. Checks in the AssetRegistry if requested wh are available. 
    /// @dev the msg.sender (a matcher) will become the escrow-of that certificate and is allowed to change the change the ownership
    /// @param _assetId The id of the Certificate
    /// @param _powerInW The amount of Watts the Certificate holds
    function createCertificateForAssetOwner(uint _assetId, uint _powerInW) 
        public 
        onlyRole(RoleManagement.Role.Matcher)
        isInitialized  
        returns (uint) 
    {
        var ( , ownerAddress, , , , ) = AssetProducingRegistryLogic(address(cooContract.assetProducingRegistry())).getAssetGeneral(_assetId);
        return createCertificateIntern(_assetId, ownerAddress, _powerInW, msg.sender);
    }

    /// @notice Request a certificate to retire. Only Certificate owner can retire
    /// @param _id The id of the certificate
    function retireCertificate(uint _id) public isInitialized() {
       var (, owner, , retired,, ,,) = certificateDb.getCertificate(_id);
        require(owner == msg.sender);
        if (!retired) {
            certificateDb.setCertificateEscrow(_id, 0x0);
            certificateDb.retireCertificate(_id);
            LogRetireRequest(_id, true);
        }
    }

    /// @notice function to allow an escrow-address to change the ownership of a certificate
    /// @dev this function can only be called by the demandLogic
    /// @param _id the certificate-id
    /// @param _newOwner the new owner of the certificate
    function transferOwnershipByEscrow(uint _id, address _newOwner) 
        public 
        isInitialized 
        onlyAccount(address(cooContract.demandRegistry()) )  
    {   
           
        address oldOwner;
        bool retired;
        address oldEscrow; 
        
        ( ,oldOwner,,retired,,,oldEscrow,) = certificateDb.getCertificate(_id); 

        require(!retired);
        certificateDb.setCertificateOwner(_id, _newOwner);
        certificateDb.setCertificateEscrow(_id, 0x0);
        LogCertificateOwnerChanged(_id, oldOwner, _newOwner, oldEscrow, 0x0);
    }

    /// @notice Sets a new owner for the certificate
    /// @param _id The id of the certificate
    /// @param _newOwner The address of the new owner of the certificate
    function changeCertificateOwner(uint _id, address _newOwner) 
        public 
        isInitialized() 
        userExists(_newOwner) 
    {
        require(msg.sender == certificateDb.getCertificateOwner(_id) && !(certificateDb.isRetired(_id)));
        certificateDb.setCertificateOwner(_id, _newOwner);
        
        address oldOwner = certificateDb.getCertificateOwner(_id); 
        address oldEscrow = certificateDb.getCertificateEscrow(_id);

        LogCertificateOwnerChanged(_id, oldOwner, _newOwner, oldEscrow, oldEscrow);

    }

    /// @notice Getter for a specific Certificate
    /// @param _certificateId The id of the requested certificate
    /// @return the certificate as single values
    function getCertificate(uint _certificateId) public view returns (  uint _assetId, 
            address _owner, 
            uint _powerInW, 
            bool _retired, 
            bytes32 _dataLog, 
            uint _coSaved, 
            address _escrow, 
            uint _creationTime) 
    {
        return certificateDb.getCertificate(_certificateId);
    }

    /// @notice Getter for a specific Certificate
    /// @param _certificateId The id of the requested certificate
    /// @return the certificate as single values
    function getCertificateOwner(uint _certificateId) public view returns (address) {
        return certificateDb.getCertificateOwner(_certificateId);
    }

    /// @notice Getter for a specific Certificate
    /// @param _certificateId The id of the requested certificate
    /// @return the certificate as single values
    function isRetired(uint _certificateId) public view returns (bool) {
        return certificateDb.isRetired(_certificateId);
    }

    /// @notice Getter for the length of the list of certificates
    /// @return the length of the array
    function getCertificateListLength() public view returns (uint) {
        return certificateDb.getCertificateListLength();
    }

    /// @notice Updates the logic contract
    /// @param _newLogic Address of the new logic contract
    function update(address _newLogic) 
        external
        onlyAccount(address(cooContract))
    {
        certificateDb.changeOwner(_newLogic);
    }
}