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
pragma solidity ^0.4.18;

import "./Owned.sol";
import "./LocationDefinition.sol";

/// @title The database contract for the users, traders and admins of the certificate of origin
/// @notice This contract only provides getter and setter methods that are only callable by the corresponging owner-contract
contract UserDB is Owned {
    
    /// @notice The structure of an user / admin / trader
    /// @dev as it's for now impossible to return a struct, there is a special get-function for this struct. 
    /// @dev keep in mind to update that function aswell when changing the user-struct
    struct User {
        bytes32 firstName;
        bytes32 surname;
        bytes32 organization;
        LocationDefinition.Location location;
        uint roles;
        bool active;
       
    }

    /// @notice mapping for addresses to users
    mapping(address => User) private userList;  

    modifier userExists(address _user) {
        require(userList[_user].firstName != 0x0 && userList[_user].surname != 0x0);
        _;
    }

    /// @notice The constructor of the UserDB
    /// @dev the deployer of this contract will get full adminrights!
    function UserDB(address _logic) Owned(_logic) public {
    }

    /// @notice function to set a new address for an existing organization 
    /// @dev the onlyOwner-modifier is used, so that only the logic-contract is allowed to write into the storage
    /// @param _user ethereum-address of the organization
    /// @param _street new streetname
    /// @param _number new number
    /// @param _zip new zip-code
    /// @param _city new city
    /// @param _country new country
    /// @param _state new state
    function setAddress(address _user, bytes32 _street, bytes32 _number, bytes32 _zip, bytes32 _city, bytes32 _country, bytes32 _state)
        external
        onlyOwner
        userExists(_user)
    {
        User storage u = userList[_user];
        u.location.street = _street;
        u.location.houseNumber = _number;
        u.location.zip = _zip;
        u.location.city = _city;
        u.location.country = _country;
        u.location.region = _state;
        u.active = true;
    }
    /// @notice function to change the name of an existing organization, can only be used when the user already exists
    /// @dev the onlyOwner-modifier is used, so that only the logic-contract is allowed to write into the storage
    /// @param _user ethereum-address of an user
    /// @param _organization new name of the organization
    function setOrganization(address _user, bytes32 _organization) external onlyOwner userExists(_user){
        User storage u = userList[_user];
        u.organization = _organization;
        u.active = true;
    }

    /// @notice function for creating, editing an user, it cannot be used to set a Role of an user
    /// @notice if the user does not exists yet it will be creates, otherwise the older userdata will be overwritten
    /// @dev the onlyOwner-modifier is used, so that only the logic-contract is allowed to write into the storage
    /// @param _user address of the user
    /// @param _firstName first name of the user
    /// @param _surname surname of the user
    /// @param _organization organization the user is representing
    /// @param _street streetname 
    /// @param _number housenumber
    /// @param _zip zip-code
    /// @param _city city-name
    /// @param _country country-name
    /// @param _state state
    function setUser(
        address _user, 
        bytes32 _firstName, 
        bytes32 _surname, 
        bytes32 _organization,
        bytes32 _street,
        bytes32 _number,
        bytes32 _zip,
        bytes32 _city,
        bytes32 _country,
        bytes32 _state
    ) 
        external 
        onlyOwner 
    {
        User storage u = userList[_user];

        LocationDefinition.Location storage loc = u.location;

        u.firstName = _firstName;
        u.surname = _surname;
        u.organization = _organization;
        u.location = loc;

        loc = u.location;
        loc.country = _country;
        loc.region = _state;
        loc.city = _city;
        loc.street = _street;
        loc.zip = _zip;
        loc.houseNumber = _number;
        loc.gpsLatitude = 0x0;
        loc.gpsLongitude = 0x0;
        loc.exists = true;
        u.active = true;
    }
 
    /// @notice function to (de-)active a user, dan only be used when the user already exists
    /// @dev the onlyOwner-modifier is used, so that only the logic-contract is allowed to write into the storage
    /// @param _user ethereum-address of an user
    /// @param _active flag if the account should be active
    function setUserActive(address _user, bool _active) external onlyOwner {
        User storage u = userList[_user];
        u.active = _active;
    }

    /// @notice function to change the username, can only be used when the user already exists
    /// @dev the onlyOwner-modifier is used, so that only the logic-contract is allowed to write into the storage
    /// @param _user ethereum-address of an user
    /// @param _firstName new first name
    /// @param _surname new surname
    function setUserName(address _user, bytes32 _firstName, bytes32 _surname) 
        external 
        onlyOwner 
        userExists(_user) 
    {   
        User storage u = userList[_user];
        u.firstName = _firstName;
        u.surname = _surname;
        u.active = true;
    }

    /// @notice function for editing the rights of an user
    /// @dev the onlyOwner-modifier is used, so that only the logic-contract is allowed to write into the storage
    /// @param _user address of the user
    /// @param _roles first name of the user
    function setRoles(address _user, uint _roles) external onlyOwner {
        User storage u = userList[_user];
        u.roles = _roles;
    }
    
    /// @notice function that checks if there is an user for the provided ethereum-address
    /// @dev the onlyOwner-modifier is used, so that only the logic-contract is allowed to read directly from the contract
    /// @param _user ethereum-address of that user
    /// @return bool if the user exists
    function doesUserExist(address _user) 
        onlyOwner
        external 
        view 
    returns (bool) {
        return userList[_user].active;
    }

    /// @notice function to return all the data of an user
    /// @dev the onlyOwner-modifier is used, so that only the logic-contract is allowed to read directly from the contract
    /// @param _user user 
    /// @return returns firstName, surname, organization, street, number, zip, city, country, state, roles and the active-flag
    function getFullUser(address _user)
        onlyOwner
        external
        view 
        returns (
            bytes32 firstName,
            bytes32 surname,
            bytes32 organization,
            bytes32 street,
            bytes32 number,
            bytes32 zip,
            bytes32 city,
            bytes32 country,
            bytes32 state,
            uint roles,
            bool active
        )
    {
        User storage u = userList[_user];
        return (u.firstName, u.surname, u.organization, u.location.street, u.location.houseNumber, u.location.zip, u.location.city, u.location.country, u.location.region, u.roles, u.active);
    }  

    /// @notice function to retrieve the rights of an user
    /// @dev the onlyOwner-modifier is used, so that only the logic-contract is allowed to read directly from the contract
    /// @dev if the user does not exist in the mapping it will return 0x0 thus preventing them from accidently getting any rights
    /// @param _user user someone wants to know its rights
    /// @return bitmask with the rights of the user
    function getRolesRights(address _user) 
        onlyOwner
        external 
        view 
        returns (uint) 
    {
        return userList[_user].roles;
    }

}