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

/// @title The Database contract for the Certificate of Origin list
/// @notice This contract only provides getter and setter methods

import "./Owned.sol";

contract CertificateDB is Owned {

    /// @notice The structure of a certificate
    /// @param assetId The id of the certificate
    /// @param owner The owner of a certificate
    /// @oaram powerInW The amount of Watts the Certificate holds. Should never be changed after creation
    /// @param retired Shows if the certificate is retired
    struct Certificate {
        uint assetId;
        address owner;
        uint powerInW;
        bool retired;
        bytes32 dataLog;
        uint coSaved;
        address escrow;
        uint creationTime;
    }

    /// @notice An array containing all created certificates
    Certificate[] private certificateList;
    
    /// @notice Constructor
    /// @param _certificateLogic The address of the corresbonding logic contract
    function CertificateDB(address _certificateLogic) Owned(_certificateLogic) public {
    }

    /// @notice Creates a new certificate
    /// @param _assetId The id of the Certificate
    /// @param _owner The owner of the Certificate
    /// @param _powerInW The amount of Watts the Certificate holds
    /// @return The id of the certificate
    function createCertificate(uint _assetId, address _owner, uint _powerInW, bytes32 _dataLog, uint _coSaved, address _escrow) public onlyOwner returns (uint _certId) {
         certificateList.push(Certificate(_assetId, _owner, _powerInW, false, _dataLog, _coSaved, _escrow, now));
                _certId = certificateList.length>0?certificateList.length-1:0;        

        
    }

    /// @notice sets the escrow-address of a certificate
    /// @param _certificateId certificateId
    /// @param _escrow new escrow-address
    function setCertificateEscrow(uint _certificateId, address _escrow)
        public
        onlyOwner
    {
        certificateList[_certificateId].escrow = _escrow;
    }

    /// @notice Sets the owner of a certificate
    /// @param _certificateId The array position in which the certificate is stored
    /// @param _owner The address of the new owner
    function setCertificateOwner(uint _certificateId, address _owner) public onlyOwner {
        certificateList[_certificateId].owner = _owner;
    }

    /// @notice Sets a certificate to retired
    /// @param _certificateId The array position in which the certificate is stored
    function retireCertificate(uint _certificateId) public onlyOwner {
        certificateList[_certificateId].retired = true;
    }

    /// @notice Returns the certificate that corresponds to the given array id
    /// @param _certificateId The array position in which the certificate is stored
    /// @return all elements of the certificate
    function getCertificate(uint _certificateId) 
        public 
        view 
        returns (
            uint _assetId, 
            address _owner, 
            uint _powerInW, 
            bool _retired, 
            bytes32 _dataLog, 
            uint _coSaved, 
            address _escrow, 
            uint _creationTime
        ) 
    {
        Certificate storage c = certificateList[_certificateId];

        _assetId = c.assetId;
        _owner = c.owner;
        _powerInW = c.powerInW; 
        _retired = c.retired;
        _dataLog = c.dataLog; 
        _coSaved = c.coSaved;
        _escrow = c.escrow;
        _creationTime = c.creationTime;    
    }

    /// @notice Returns the certificate owner
    /// @param _certificateId The array position in which the certificate is stored
    /// @return address owner
    function getCertificateOwner(uint _certificateId) public onlyOwner view returns (address) {
        return certificateList[_certificateId].owner;
    }

    /// @notice Getter for state of retirement
    /// @param _certificateId The id of the requested certificate
    /// @return bool if it is retired
    function isRetired(uint _certificateId) public onlyOwner view returns (bool) {
        return certificateList[_certificateId].retired;
    }

    /// @notice function to get the amount of all certificates
    /// @return the amount of all certificates
    function getCertificateListLength() public onlyOwner view returns (uint) {
        return certificateList.length;
    }

    /// @notice function to get the escrow-address of a certificate
    /// @param _certificateId certificate-ID
    /// @return escrow-address
    function getCertificateEscrow(uint _certificateId) 
        public
        onlyOwner
        view 
        returns (address) 
    {
        return certificateList[_certificateId].escrow;
    } 
}