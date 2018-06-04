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

var CoO = artifacts.require("CoO");
var AssetProducingRegistryLogic = artifacts.require("AssetProducingRegistryLogic")
var CertificateLogic = artifacts.require("CertificateLogic");
var UserLogic = artifacts.require("UserLogic");

var UserDB = artifacts.require("UserDB");
var AssetProducingRegistryDB = artifacts.require("AssetProducingRegistryDB")
var CertificateDB = artifacts.require("CertificateDB")

contract('CoO update one logic', function (accounts) {

    var coo,
        userDb,
        userLogic,
        assetProducingRegistryDB,
        certificateDb;

    it("should get the instances", async function () {
        coo = await CoO.deployed();
        userDb = await UserDB.deployed()
        assetProducingRegistryDB = await AssetProducingRegistryDB.deployed()
        certificateDb = await CertificateDB.deployed()
        userLogic = await UserLogic.deployed()
        assert.isNotNull(coo)
        assert.isNotNull(userDb)
        assert.isNotNull(userLogic)
        assert.isNotNull(assetProducingRegistryDB)
        assert.isNotNull(certificateDb)
    })

    it("should be initilized successfully", async function () {
        assert.equal(await coo.userRegistry(), UserLogic.address)
        //     assert.equal(await coo.userDB(), UserDB.address)
        assert.equal(await coo.assetProducingRegistry(), AssetProducingRegistryLogic.address)
        assert.equal(await coo.certificateRegistry(), CertificateLogic.address)

    })

    it("should not allow other users to call the update-function", async function () {
        assert.equal(await userDb.owner(), UserLogic.address, 'userDB has wrong owner')
        assert.equal(await assetProducingRegistryDB.owner(), AssetProducingRegistryLogic.address, 'assetDB has wrong owner')
        assert.equal(await certificateDb.owner(), CertificateLogic.address, 'certificateDB has wrong owner')
        let failed = false
        try {
            let tx = await coo.update('0x0000000000000000000000000000000000000001', '0x0000000000000000000000000000000000000000', '0x0000000000000000000000000000000000000001', '0x0000000000000000000000000000000000000001', '0x0000000000000000000000000000000000000001', { from: accounts[1] })
            if (tx.receipt.status == '0x00') failed = true
        }
        catch (ex) {
            failed = true
        }
        assert.isTrue(failed)
        assert.equal(await coo.userRegistry(), UserLogic.address)
        //   assert.equal(await coo.userDB(), UserDB.address)
        assert.equal(await coo.assetProducingRegistry(), AssetProducingRegistryLogic.address)
        assert.equal(await coo.certificateRegistry(), CertificateLogic.address)

        assert.equal(await userDb.owner(), UserLogic.address, 'userDB has wrong owner')
        assert.equal(await assetProducingRegistryDB.owner(), AssetProducingRegistryLogic.address, 'assetDB has wrong owner')
        assert.equal(await certificateDb.owner(), CertificateLogic.address, 'certificateDB has wrong owner')
    })

    it("should not be possible for the TopAdmin to call the update-function of a logic-contract", async function () {
        assert.equal(await userDb.owner(), UserLogic.address, 'userDB has wrong owner')
        let failed = false
        try {
            let tx = await userLogic.update('0x0000000000000000000000000000000000000001')
            if (tx.receipt.status == '0x00') failed = true
        }
        catch (ex) {
            failed = true
        }
        assert.isTrue(failed)
        assert.equal(await userDb.owner(), UserLogic.address, 'userDB has wrong owner')

    })

    it("should update userlogic correctly", async function () {
        assert.equal(await userDb.owner(), UserLogic.address, 'userDB has wrong owner')
        assert.equal(await assetProducingRegistryDB.owner(), AssetProducingRegistryLogic.address, 'assetDB has wrong owner')
        assert.equal(await certificateDb.owner(), CertificateLogic.address, 'certificateDB has wrong owner')

        await coo.update('0x0000000000000000000000000000000000000001', '0x0000000000000000000000000000000000000000', '0x0000000000000000000000000000000000000000', '0x0000000000000000000000000000000000000000', '0x0000000000000000000000000000000000000000')

        assert.equal(await coo.userRegistry(), '0x0000000000000000000000000000000000000001')
        //     assert.equal(await coo.userDB(), UserDB.address)
        assert.equal(await coo.assetProducingRegistry(), AssetProducingRegistryLogic.address)
        assert.equal(await coo.certificateRegistry(), CertificateLogic.address)

        assert.equal(await userDb.owner(), '0x0000000000000000000000000000000000000001', 'userDB has wrong owner')
        assert.equal(await assetProducingRegistryDB.owner(), AssetProducingRegistryLogic.address, 'assetDB has wrong owner')
        assert.equal(await certificateDb.owner(), CertificateLogic.address, 'certificateDB has wrong owner')


    })

})