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
// @authors: slock.it GmbH, Heiko Burkhardt, heiko.burkhardt@slock.it; Martin Kuechler, martin.kuechler@slock.it

var AssetProducingRegistryLogic = artifacts.require("AssetProducingRegistryLogic");
var AssetProducingRegistryDB = artifacts.require("AssetProducingRegistryDB");
var CoO = artifacts.require("CoO");

contract('AssetProducingRegistryLogic', function (accounts) {

  var assetLog,
    assetDb,
    coo;

  it("should get the instances", async function () {
    assetLog = await AssetProducingRegistryLogic.deployed();
    assetDb = await AssetProducingRegistryDB.deployed();
    coo = await CoO.deployed()

    assert.isNotNull(assetLog)
    assert.isNotNull(assetDb)
    assert.isNotNull(coo)
  })

  it("should execute the constructor successfully", async function () { })

  it("should be initialized successfully", async function () {
    assert.equal(await assetLog.db.call(), AssetProducingRegistryDB.address)
  })

  it("should have 0 assets in the assetList", async function () {
    assert.equal((await assetLog.getAssetListLength()).toNumber(), 0)
  })


  it("should create an new empty asset and get an event", async function () {
    let tx = await assetLog.createAsset()
    let event = (tx.logs[0])
    assert.equal(event.event, "LogAssetCreated")
    assert.equal(event.args.sender, accounts[0])
    assert.equal(event.args._assetId.toNumber(), 0)
  })

  it("should have 1 asset in the assetList", async function () {
    assert.equal((await assetLog.getAssetListLength()).toNumber(), 1)
  })

  it("should register general information of an asset with an existing owner", async function () {

    await assetLog.initGeneral(
      0,
      accounts[9],
      accounts[0],
      1234567890,
      true,
      { from: accounts[2] }
    )

    const asset = await assetLog.getAssetGeneral(0)
    assert.equal(asset[0], accounts[9])
    assert.equal(asset[1], accounts[0])
    assert.equal(asset[2], 1234567890)
    assert.equal(asset[3], 0)
    assert.equal(asset[4], true)
    assert.equal(asset[5], "0x0000000000000000000000000000000000000000000000000000000000000000")


  })

  it("should register location information of an asset with an existing owner", async function () {
    await assetLog.initLocation(
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

    const assetLocation = await assetLog.getAssetLocation(0)
    assert.equal(web3.toAscii(assetLocation[0]).replace(/\0/g, ''), 'Germany')
    assert.equal(web3.toAscii(assetLocation[1]).replace(/\0/g, ''), 'Saxony')
    assert.equal(web3.toAscii(assetLocation[2]).replace(/\0/g, ''), '123412')
    assert.equal(web3.toAscii(assetLocation[3]).replace(/\0/g, ''), 'Mittweida')
    assert.equal(web3.toAscii(assetLocation[4]).replace(/\0/g, ''), 'Markt')
    assert.equal(web3.toAscii(assetLocation[5]).replace(/\0/g, ''), '16a')
    assert.equal(web3.toAscii(assetLocation[6]).replace(/\0/g, ''), '0.1232423423')
    assert.equal(web3.toAscii(assetLocation[7]).replace(/\0/g, ''), '0.2342342445')

  })

  it("should not register an asset with a non existing owner", async function () {
    let failed = false

    try {
      await assetLog.registerAsset(accounts[9], accounts[2], 0, 0, 1234567890, 100000, 1, 0, true, { from: accounts[2] })
      if (tx.receipt.status == '0x00') failed = true

    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)
  })


  it("should store producing properties", async function () {
    let tx = await assetLog.initProducingProperties(0,
      1,
      1000,
      1,
      web3.fromAscii("N.A."),
      web3.fromAscii("N.A."))

    let pp = await assetLog.getAssetProducingProperties(0)
    assert.equal(pp[0].toNumber(), 1)
    assert.equal(pp[1].toNumber(), 1000)
    assert.equal(pp[2].toNumber(), 0)
    assert.equal(pp[3].toNumber(), 0)
    assert.equal(pp[4].toNumber(), 0)
    assert.equal(pp[5].toNumber(), 1)
    assert.equal(web3.toAscii(pp[6]).replace(/\0/g, ''), 'N.A.')
    assert.equal(web3.toAscii(pp[7]).replace(/\0/g, ''), 'N.A.')

  })

  it("should return 0 when calling getCoSaved wth 0 wh", async function () {
    assert.equal((await assetLog.getCoSaved(0, 0)).toNumber(), 0)
  })

  it("should log data", async function () {
    const tx = await assetLog.saveSmartMeterRead(
      0,
      201,
      false,
      '0x0000000000000000000000000000000000000000000000000000000000000001',
      401,
      true,
      { from: accounts[9] }
    )

    console.log(tx.logs[0])

    let event = tx.logs[0]
    assert.equal(event.event, "LogNewMeterRead")
    assert.equal(event.args._assetId.toNumber(), 0)
    assert.equal(event.args._fileHash, "0x0000000000000000000000000000000000000000000000000000000000000001")
    assert.equal(event.args._oldMeterRead.toNumber(), 0)
    assert.equal(event.args._newMeterRead.toNumber(), 201)
    assert.isFalse(event.args._smartMeterDown)
    assert.equal(event.args._certificatesCreatedForWh.toNumber(), 0)
    assert.equal(event.args._oldCO2OffsetReading.toNumber(), 0)
    assert.equal(event.args._newCO2OffsetReading.toNumber(), 401)
    assert.isTrue(event.args._serviceDown)

  })

  it("should return 0 when calling getCoSaved wth 0 wh", async function () {
    assert.equal((await assetLog.getCoSaved(0, 0)).toNumber(), 0)
  })

  it("other account than smart meter should not log data", async function () {
    let failed = false
    try {
      const tx = await assetLog.saveSmartMeterRead(0, 201, '0x0000000000000000000000000000000000000000000000000000000000000001', { from: accounts[8] })
      if (tx.receipt.status == '0x00') failed = true

    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })


  it("should retire an asset", async function () {
    await assetLog.setActive(0, false, { from: accounts[2] })
    assert.isFalse(await assetLog.getActive(0))

    // assert.isFalse(asset[8])
  })

  it("should re-retire an asset", async function () {
    await assetLog.setActive(0, true, { from: accounts[2] })
    const asset = await assetLog.getAssetGeneral.call(0)
    assert.isTrue(await assetLog.getActive(0))

  })

  it("smart meter should not be able to log data for a retired asset ", async function () {
    let failed = false
    try {
      const tx = await assetLog.saveSmartMeterRead(0, 401, '0x0000000000000000000000000000000000000000000000000000000000000001', { from: accounts[9] })
      if (tx.receipt.status == '0x00') failed = true

    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })

  it("should update correctly", async function () { })

})