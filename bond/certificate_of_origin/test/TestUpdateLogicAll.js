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

var UserLogic = artifacts.require("UserLogic");
var UserDB = artifacts.require("UserDB");

var AssetProducingRegistryLogic = artifacts.require("AssetProducingRegistryLogic")
var AssetProducingRegistryDB = artifacts.require("AssetProducingRegistryDB")

var AssetConsumingRegistryLogic = artifacts.require("AssetConsumingRegistryLogic")
var AssetConsumingRegistryDB = artifacts.require("AssetConsumingRegistryDB")

var CertificateLogic = artifacts.require("CertificateLogic");
var CertificateDB = artifacts.require("CertificateDB")

var DemandLogic = artifacts.require("DemandLogic");
var DemandDB = artifacts.require("DemandDB")


contract('CoO update all logic', function (accounts) {

    var coo,
        userDb,
        userLogic,
        assetProducingRegistryDB,
        assetProducingRegistryLogic,
        assetConsumingRegistryDB,
        certificateDb,
        certificateLogic,
        demandLogic,
        demandDb

    it("should get the instances", async function () {
        coo = await CoO.deployed();
        userDb = await UserDB.deployed()
        userLogic = await UserLogic.deployed()
        assetProducingRegistryDB = await AssetProducingRegistryDB.deployed()
        assetProducingRegistryLogic = await AssetProducingRegistryLogic.deployed()
        certificateDb = await CertificateDB.deployed()
        certificateLogic = await CertificateLogic.deployed()
        assetConsumingRegistryDB = await AssetConsumingRegistryDB.deployed()
        demandLogic = await DemandLogic.deployed()
        demandDb = await DemandDB.deployed()

        assert.isNotNull(coo)
        assert.isNotNull(userDb)
        assert.isNotNull(userLogic)
        assert.isNotNull(assetProducingRegistryDB)
        assert.isNotNull(assetProducingRegistryLogic)
        assert.isNotNull(certificateDb)
        assert.isNotNull(certificateLogic)
    })

    it("should be initilized successfully", async function () {
        assert.equal(await coo.userRegistry(), UserLogic.address)
        //   assert.equal(await coo.userDB(), UserDB.address)
        assert.equal(await coo.assetProducingRegistry(), AssetProducingRegistryLogic.address)
        assert.equal(await coo.certificateRegistry(), CertificateLogic.address)

    })

    it("should not allow other users to call the update-function", async function () {
        assert.equal(await userDb.owner(), UserLogic.address, 'userDB has wrong owner')
        assert.equal(await assetProducingRegistryDB.owner(), AssetProducingRegistryLogic.address, 'assetDB has wrong owner')
        assert.equal(await certificateDb.owner(), CertificateLogic.address, 'certificateDB has wrong owner')

        let failed = false
        try {
            await coo.update('0x0000000000000000000000000000000000000001', '0x0000000000000000000000000000000000000002', '0x0000000000000000000000000000000000000003', '0x0000000000000000000000000000000000000004', '0x0000000000000000000000000000000000000005', { from: accounts[1] })
            if (tx.receipt.status == '0x00') failed = true
        } catch (ex) {
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

    it("should not be possible for the TopAdmin to call the update-function of the logic-contracts", async function () {
        assert.equal(await userDb.owner(), UserLogic.address, 'userDB has wrong owner')
        let failed = false
        try {
            let tx = await userLogic.update('0x0000000000000000000000000000000000000001')
            if (tx.receipt.status == '0x00') failed = true
        } catch (ex) {
            failed = true
        }
        assert.isTrue(failed)
        assert.equal(await userDb.owner(), UserLogic.address, 'userDB has wrong owner')

        assert.equal(await assetProducingRegistryDB.owner(), AssetProducingRegistryLogic.address, 'AssetProducingRegistryDB has wrong owner before')

        failed = false
        try {
            let tx = await assetProducingRegistryLogic.update('0x0000000000000000000000000000000000000001')
            if (tx.receipt.status == '0x00') failed = true
        } catch (ex) {
            failed = true
        }
        assert.equal(await assetProducingRegistryDB.owner(), AssetProducingRegistryLogic.address, 'AssetProducingRegistryDB has wrong owner afterwards')

        assert.equal(await certificateDb.owner(), CertificateLogic.address, 'certificateDB has wrong owner')

        failed = false
        try {
            let tx = await certificateLogic.update('0x0000000000000000000000000000000000000001')
            if (tx.receipt.status == '0x00') failed = true
        } catch (ex) {
            failed = true
        }
        assert.equal(await certificateDb.owner(), CertificateLogic.address, 'certificateDB has wrong owner')
    })

    it("should update all contracts correctly", async function () {
        assert.equal(await userDb.owner(), UserLogic.address, 'userDB has wrong owner')
        assert.equal(await assetProducingRegistryDB.owner(), AssetProducingRegistryLogic.address, 'assetDB has wrong owner')
        assert.equal(await certificateDb.owner(), CertificateLogic.address, 'certificateDB has wrong owner')

        await coo.update('0x0000000000000000000000000000000000000001', '0x0000000000000000000000000000000000000002', '0x0000000000000000000000000000000000000003', '0x0000000000000000000000000000000000000004', '0x0000000000000000000000000000000000000005')
        assert.equal(await coo.userRegistry(), '0x0000000000000000000000000000000000000001')
        //  assert.equal(await coo.userDB(), UserDB.address)
        assert.equal(await coo.assetProducingRegistry(), '0x0000000000000000000000000000000000000002')
        assert.equal(await coo.certificateRegistry(), '0x0000000000000000000000000000000000000003')
        assert.equal(await coo.demandRegistry(), '0x0000000000000000000000000000000000000004')
        assert.equal(await coo.assetConsumingRegistry(), '0x0000000000000000000000000000000000000005')

        assert.equal(await userDb.owner(), '0x0000000000000000000000000000000000000001', 'userDB has wrong owner')
        assert.equal(await assetProducingRegistryDB.owner(), '0x0000000000000000000000000000000000000002', 'assetDB has wrong owner')
        assert.equal(await certificateDb.owner(), '0x0000000000000000000000000000000000000003', 'certificateDB has wrong owner')
        assert.equal(await demandDb.owner(), '0x0000000000000000000000000000000000000004', 'demandDB has wrong owner')
        assert.equal(await assetConsumingRegistryDB.owner(), '0x0000000000000000000000000000000000000005')
    })

})