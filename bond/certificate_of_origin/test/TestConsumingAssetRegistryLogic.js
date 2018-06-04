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
// @authors: slock.it GmbH, Martin Kuechler, martin.kuechler@slock.it

var ConsumingLogic = artifacts.require("AssetConsumingRegistryLogic");
var ConsumingDB = artifacts.require("AssetConsumingRegistryDB");
var CoO = artifacts.require("CoO");


contract('AssetConsumingLogic', function (accounts) {

    var consumingLogic,
        consumingDB;


    it("should get the instances", async function () {
        consumingLogic = await ConsumingLogic.deployed();
        consumingDB = await ConsumingDB.deployed();
        coo = await CoO.deployed()

        assert.isNotNull(consumingLogic)
        assert.isNotNull(consumingDB)
        assert.isNotNull(coo)
    })

    it("should initialized correctly", async function () {
        assert.equal(await consumingLogic.db(), ConsumingDB.address)
    })

    it("should only be possible to call init be call once", async function () {

        let failed = false
        try {
            let tx = await consumingLogic.init('0x0000000000000000000000000000000000000001')
            if (tx.receipt.status == '0x00') failed = true
        } catch (ex) {
            failed = true
        }
        assert.isTrue(failed)
        assert.equal(await consumingLogic.db(), ConsumingDB.address)
    })

    it("should not have any conuming assets yet", async function () {
        assert.equal(await consumingLogic.getAssetListLength(), 0)
    })

    it("should trigger an event when calling createAsset", async function () {
        let tx = await consumingLogic.createAsset()
        let event = tx.logs[0]

        assert.equal(event.event, "LogAssetCreated")
        assert.equal(event.args._assetId.toNumber(), 0)
    })

    it("should have 1 conuming assets yet", async function () {
        assert.equal(await consumingLogic.getAssetListLength(), 1)
    })

    it("should not be an active asset", async function () {
        assert.isFalse(await consumingLogic.getActive(0))
    })

    it("should be possible to set the generalInformation of the newly created asset", async function () {
        await consumingLogic.initGeneral(0,
            accounts[9], accounts[0],
            1234567890,
            0,
            false, true)
    })

    it("should correctly return the generalInformation", async function () {
        let assetGeneral = (await consumingLogic.getAssetGeneral(0))
        assert.equal(assetGeneral[0], accounts[9])
        assert.equal(assetGeneral[1], accounts[0])
        assert.equal(assetGeneral[2].toNumber(), 1234567890)
        assert.equal(assetGeneral[3].toNumber(), 0)
        assert.isFalse(assetGeneral[4])
        assert.equal(assetGeneral[5].toNumber(), 0)
        assert.equal(assetGeneral[6].toNumber(), 0)
        assert.isTrue(assetGeneral[7])
        assert.equal(web3.toAscii(assetGeneral[8]).replace(/\0/g, ''), '')


    })

    it("should register location information of an asset with an existing owner", async function () {
        let tx = await consumingLogic.initLocation(
            0,
            web3.fromAscii("Germany"),
            web3.fromAscii("Saxony"),
            web3.fromAscii("123412"),
            web3.fromAscii("Mittweida"),
            web3.fromAscii("Markt"),
            web3.fromAscii("16a"),
            web3.fromAscii("0.1232423423"),
            web3.fromAscii("0.2342342445")
        )

        let event = (tx.logs[0])
        assert.equal(event.event, "LogAssetFullyInitialized")

    })

    it("should correctly return the locationInformation", async function () {
        let assetLocation = (await consumingLogic.getAssetLocation(0))

        assert.equal(web3.toAscii(assetLocation[0]).replace(/\0/g, ''), 'Germany')
        assert.equal(web3.toAscii(assetLocation[1]).replace(/\0/g, ''), 'Saxony')
        assert.equal(web3.toAscii(assetLocation[2]).replace(/\0/g, ''), '123412')
        assert.equal(web3.toAscii(assetLocation[3]).replace(/\0/g, ''), 'Mittweida')
        assert.equal(web3.toAscii(assetLocation[4]).replace(/\0/g, ''), 'Markt')
        assert.equal(web3.toAscii(assetLocation[5]).replace(/\0/g, ''), '16a')
        assert.equal(web3.toAscii(assetLocation[6]).replace(/\0/g, ''), '0.1232423423')
        assert.equal(web3.toAscii(assetLocation[7]).replace(/\0/g, ''), '0.2342342445')

    })

    it("should have set the asset to active", async function () {
        assert.isTrue(await consumingLogic.getActive(0))
    })

    it("should be possible to log a meterreading", async function () {
        await consumingLogic.saveSmartMeterRead(0, 10000, web3.fromAscii("newMeterRead"), false, { from: accounts[9] })
    })

    it("should return the right filehash", async function () {
        let log = await consumingLogic.getLastSmartMeterReadFileHash(0)

        assert.equal(web3.toAscii(log).replace(/\0/g, ''), 'newMeterRead')

    })

    it("should be possible update a smartMeter", async function () {
        await consumingLogic.updateSmartMeter(0, accounts[8])
    })

    it("should be possible deactivate an asset", async function () {
        await consumingLogic.setActive(0, false)
    })


})