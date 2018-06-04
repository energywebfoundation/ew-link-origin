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

import "./UserDB.sol";
import "./RoleManagement.sol";
import "./CoO.sol";
import "./Updatable.sol";
import "./RolesInterface.sol";

/// @title The logic-contract for the user-data
/// @notice this contract will not directly store any data, instead it will store them into the userDB-contract
contract UserLogic is RoleManagement, Updatable, RolesInterface {
    /// @notice db user-db for storing the contract
    UserDB public db;

    modifier isInitialized {
        require(address(db) != 0x0);
        _;
    }

    /// @notice constructor 
    /// @param _coo address of the Certificate Registry contract (CoO.sol)
    /// @dev it will also call the RoleManagement-constructor 
    function UserLogic(CoO _coo) RoleManagement(_coo) public {
    }

    /// @notice grant a user a an admin-right
    /// @param _user user that should get rights
    /// @param role admin-right to be granted
    function addAdminRole(address _user, RoleManagement.Role role)
        external 
        userExists(_user)
        onlyRole(RoleManagement.Role.TopAdmin) 
    {
        if ((role == RoleManagement.Role.TopAdmin || role == RoleManagement.Role.UserAdmin 
        || role == RoleManagement.Role.AssetAdmin || role == RoleManagement.Role.Trader)
     //   && role != RoleManagement.Role.Trader && role != RoleManagement.Role.AssetManager
        ) {
           
            if (!isRole(role,_user)) {
                uint roles = db.getRolesRights(_user);
                db.setRoles(_user, roles + uint(2) ** uint(role));
            }
        }
    }

    /// @notice grants a user the role AssetManager
    /// @param _user user 
    function addAssetManagerRole(address _user)
        external
        userExists(_user)
        onlyRole(RoleManagement.Role.AssetAdmin) 
    {
        if (!isRole(RoleManagement.Role.AssetManager,_user)) {
            uint roles = db.getRolesRights(_user);
            db.setRoles(_user, roles + uint(2) ** uint(RoleManagement.Role.AssetManager));
        }
    }

    /// @notice grants an ethereum-account the matcher-rights
    /// @param _user ethereum-account
    function addMatcherRole(address _user)
        external
        onlyRole(RoleManagement.Role.TopAdmin)
    {
            if (!isRole(RoleManagement.Role.Matcher,_user)) {
            uint roles = db.getRolesRights(_user);
            db.setRoles(_user, roles + uint(2) ** uint(RoleManagement.Role.Matcher));
        }
    }

    /// @notice grants a user the trader-Role
    /// @param _user user
    function addTraderRole(address _user)
        external
        userExists(_user)
        onlyRole(RoleManagement.Role.AgreementAdmin) 
    {
        if (!isRole(RoleManagement.Role.Trader,_user)) {
            uint roles = db.getRolesRights(_user);
            db.setRoles(_user, roles + uint(2) ** uint(RoleManagement.Role.Trader));
        }
    }
    /// @notice Initialises the contract by binding it to a logic contract
    /// @param _database Sets the logic contract
    function init(address _database) external {
        require(db == UserDB(0x0) && cooContract.owner() == msg.sender);
        db = UserDB(_database);
    }

    /// @notice function to deactive an use, only executable for user-admins
    /// @param _user the user that should be deactivated
    function deactivateUser(address _user)
        external
        onlyRole(RoleManagement.Role.UserAdmin)
        isInitialized
    {
        require(!isRole(RoleManagement.Role.TopAdmin,_user) 
            && !isRole(RoleManagement.Role.UserAdmin,_user) 
            && !isRole(RoleManagement.Role.AssetAdmin,_user)
            && !isRole(RoleManagement.Role.AgreementAdmin,_user)
        );

        db.setUserActive(_user, false);
    }

    /// @notice function to remove an admin-right from a user
    /// @param _user user
    /// @param role role to be removed
    function removeAdminRole(address _user, RoleManagement.Role role)
        external 
        userExists(_user)
        onlyRole(RoleManagement.Role.TopAdmin) 
    {
        if ((role == RoleManagement.Role.TopAdmin || role == RoleManagement.Role.UserAdmin 
        || role == RoleManagement.Role.AssetAdmin || role == RoleManagement.Role.AgreementAdmin)
      ) {
            if (isRole(role,_user)) {
                uint roles = db.getRolesRights(_user);
                db.setRoles(_user, roles - uint(2) ** uint(role));
            }
        }
    }

    /// @notice removes the assetManagerRole from a user
    /// @param _user user
    function removeAssetManagerRole(address _user)
        external
        userExists(_user)
        onlyRole(RoleManagement.Role.AssetAdmin) 
    {
        if (isRole(RoleManagement.Role.AssetManager,_user)) {
            uint roles = db.getRolesRights(_user);
            db.setRoles(_user, roles - uint(2) ** uint(RoleManagement.Role.AssetManager));
        }
    }

    /// @notice removes the traderRole from a user
    /// @param _user user
    function removeTraderRole(address _user)
        external
        userExists(_user)
        onlyRole(RoleManagement.Role.AgreementAdmin) 
    {
        if (isRole(RoleManagement.Role.Trader,_user)) {
            uint roles = db.getRolesRights(_user);
            db.setRoles(_user, roles - uint(2) ** uint(RoleManagement.Role.Trader));
        }
    }

    /// @notice function set change the name of an organization
    /// @param _user ethereum-address of an user / organization
    function setOrganization(address _user, bytes32 _organization) 
        external 
        onlyRole(RoleManagement.Role.UserAdmin) 

    {
        require(_organization != 0x0);
        db.setOrganization(_user,_organization);
    }

    /// @notice function to set a new address for an existing organization 
    /// @param _user ethereum-address of the organization
    /// @param _street new streetname
    /// @param _number new number
    /// @param _zip new zip-code
    /// @param _city new city
    /// @param _country new country
    /// @param _state new state
    function setOrganizationAddress(address _user, bytes32 _street, bytes32 _number, bytes32 _zip, bytes32 _city, bytes32 _country, bytes32 _state)
        external
        onlyRole(RoleManagement.Role.UserAdmin) 
    {
        require(_city != 0x0 && _street != 0x0 && _number > 0 && _zip != 0x0 && _country != 0x0);
        db.setAddress(_user, _street, _number, _zip, _city, _country, _state);
    }

    /// @notice funciton that can be called to create a new user in the storage-contract, only executable for user-admins!
    /// @notice if the user does not exists yet it will be creates, otherwise the older userdata will be overwritten
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
        onlyRole(RoleManagement.Role.UserAdmin) 
        isInitialized
    {  
        require(_user != address(0x0)
            && _firstName != 0x0 && _surname != 0x0 
            && _organization != 0x0 
            && _city != 0x0 && _street != 0x0 && _number > 0 && _zip != 0x0 && _country != 0x0
        );    
        db.setUser( _user, _firstName, _surname, _organization, _street, _number, _zip, _city, _country, _state);   

    }

    /// @notice function to change the name of an user
    /// @param _user ethereum-account of that user
    /// @param _firstName new first name
    /// @param _surname new surname
    function setUserName(address _user, bytes32 _firstName, bytes32 _surname) 
        external
        onlyRole(RoleManagement.Role.UserAdmin) 
    {   
        require(_firstName != 0x0 && _surname != 0x0);
        db.setUserName(_user, _firstName, _surname);
    }
    
    /// @notice function to set / edit the rights of an user / account, only executable for Top-Admins!
    /// @param _user user that rights will change
    /// beware: if the only TopAdmin revokes its own rights noone will be able to get TopAdmin-rights back, making it impossible to set any new admin-rights
    /// @param _rights rights encoded as bitmask
    function setRoles(address _user, uint _rights) 
        external 
        onlyRole(RoleManagement.Role.UserAdmin)
        isInitialized
       userExists(_user)
    {
        db.setRoles(_user, _rights);
    }


    /// @notice function to update the logic of a smart contract
    /// @param _newLogic contract-address of the new smart contract, replacing the currently active one
    function update(address _newLogic) 
        external
        onlyAccount(address(cooContract))
        isInitialized
    {
        db.changeOwner(_newLogic);
    }

    /// @notice function that checks if there is an user for the provided ethereum-address
    /// @param _user ethereum-address of that user
    /// @return bool if the user exists
    function doesUserExist(address _user) 
        external 
        view 
        returns (bool) 
    {
        return db.doesUserExist(_user);
    }

    /// @notice function to return all the data of an user
    /// @param _user user 
    /// @return returns firstName, surname, organization, street, number, zip, city, country, state, roles and the active-flag
    function getFullUser(address _user)
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
        return db.getFullUser(_user);
    }

    /// @notice function to retrieve the rights of an user
    /// @dev if the user does not exist in the mapping it will return 0x0 thus preventing them from accidently getting any rights
    /// @param _user user someone wants to know its rights
    /// @return bitmask with the rights of the user
    function getRolesRights(address _user) 
        external 
        view 
        returns (uint) 
    {
        return db.getRolesRights(_user);
    }


   
    

}