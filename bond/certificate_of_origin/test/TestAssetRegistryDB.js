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
var CoO = artifacts.require("CoO")
contract('AssetProducingRegistryDB', function (accounts) {

  var assetLog,
    assetDb,
    coo

  it("should get the instances", async function () {
    assetLog = await AssetProducingRegistryLogic.deployed();
    assetDb = await AssetProducingRegistryDB.deployed();
    coo = await CoO.deployed()
  })


  it("should create an Asset for Testing", async function () {
    await assetLog.createAsset()
    await assetLog.initGeneral(
      0,
      accounts[9],
      accounts[0],
      1234567890,
      true,
      { from: accounts[2] })

    await assetLog.initProducingProperties(0,
      1,
      1000,
      1,
      web3.fromAscii("N.A."),
      web3.fromAscii("N.A."))

    await assetLog.initLocation(
      0,
      web3.fromAscii("Germany"),
      web3.fromAscii("Saxony"),
      web3.fromAscii("123412"),
      web3.fromAscii("Mittweida"),
      web3.fromAscii("Markt"),
      web3.fromAscii("16"),
      web3.fromAscii("0.1232423423"),
      web3.fromAscii("0.2342342445")
    )
  })

  it("change the owner for testing", async function () {
    await coo.update("0x0000000000000000000000000000000000000000", accounts[0], "0x0000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000000", "0x0000000000000000000000000000000000000000")

  })


  it("should not be able to set assetType as non-Owner", async function () {
    let assetBefore = await assetDb.getAssetProducingProperties(0)

    try {
      await assetDb.setAssetType(0, 1, { from: accounts[1] })
    } catch (ex) {

    }

    let assetAfter = await assetDb.getAssetProducingProperties(0)
    assert.deepEqual(assetBefore, assetAfter)

  })

  it("should be able to set assetType as Owner", async function () {
    let assetBefore = await assetDb.getAssetProducingProperties(0)

    await assetDb.setAssetType(0, 2)

    let assetAfter = await assetDb.getAssetProducingProperties(0)
    assert.equal(assetBefore[0].toNumber(), 1)
    assert.equal(assetAfter[0].toNumber(), 2)

  })

  it("should not be able to set capacity as non-Owner", async function () {
    let assetBefore = await assetDb.getAssetGeneral(0)

    try {
      await assetDb.setCapacityWh(0, 1, { from: accounts[1] })
    } catch (ex) {

    }

    let assetAfter = await assetDb.getAssetGeneral(0)
    assert.deepEqual(assetBefore, assetAfter)

  })

  it("should be able to set assetType as Owner", async function () {
    let assetBefore = await assetDb.getAssetProducingProperties(0)

    await assetDb.setCapacityWh(0, 99)

    let assetAfter = await assetDb.getAssetProducingProperties(0)
    assert.equal(assetBefore[1].toNumber(), 1000)
    assert.equal(assetAfter[1].toNumber(), 99)

  })

  it("should not be able to set location country as non-Owner", async function () {
    let assetBefore = await assetDb.getAssetLocation(0)

    try {
      await assetDb.setLocationCountry(0, "USA", { from: accounts[1] })
    } catch (ex) {

    }

    let assetAfter = await assetDb.getAssetLocation(0)
    assert.deepEqual(assetBefore, assetAfter)

  })


  it("should be able to set location country as Owner", async function () {
    let assetBefore = await assetDb.getAssetLocation(0)

    await assetDb.setLocationCountry(0, "USA")

    let assetAfter = await assetDb.getAssetLocation(0)
    assert.equal(web3.toAscii(assetBefore[0]).replace(/\0/g, ''), 'Germany')
    assert.equal(web3.toAscii(assetAfter[0]).replace(/\0/g, ''), 'USA')

  })

  it("should not be able to set location region as non-Owner", async function () {
    let assetBefore = await assetDb.getAssetLocation(0)

    try {
      await assetDb.setLocationRegion(0, "Berlin", { from: accounts[1] })
    } catch (ex) {

    }

    let assetAfter = await assetDb.getAssetLocation(0)
    assert.deepEqual(assetBefore, assetAfter)

  })


  it("should be able to set location region as Owner", async function () {
    let assetBefore = await assetDb.getAssetLocation(0)

    await assetDb.setLocationRegion(0, "Berlin")

    let assetAfter = await assetDb.getAssetLocation(0)
    assert.equal(web3.toAscii(assetBefore[1]).replace(/\0/g, ''), 'Saxony')
    assert.equal(web3.toAscii(assetAfter[1]).replace(/\0/g, ''), 'Berlin')

  })

  it("should not be able to set operationalSince as non-Owner", async function () {
    let assetBefore = await assetDb.getAssetGeneral(0)

    try {
      await assetDb.setOperationalSince(0, 54321, { from: accounts[1] })
    } catch (ex) {

    }

    let assetAfter = await assetDb.getAssetGeneral(0)
    assert.deepEqual(assetBefore, assetAfter)

  })


  it("should be able to set operationalSince as Owner", async function () {
    let assetBefore = await assetDb.getAssetGeneral(0)

    await assetDb.setOperationalSince(0, 54321)

    let assetAfter = await assetDb.getAssetGeneral(0)
    assert.equal(assetBefore[2].toNumber(), 1234567890)
    assert.equal(assetAfter[2].toNumber(), 54321)

  })

  it("should not be able to set assetOwner as non-Owner", async function () {
    let assetBefore = await assetDb.getAssetGeneral(0)

    try {
      await assetDb.setOwner(0, accounts[2], { from: accounts[1] })
    } catch (ex) {

    }

    let assetAfter = await assetDb.getAssetGeneral(0)
    assert.deepEqual(assetBefore, assetAfter)

  })


  it("should be able to set assetOwner as Owner", async function () {
    let assetBefore = await assetDb.getAssetGeneral(0)

    await assetDb.setOwner(0, accounts[2])

    let assetAfter = await assetDb.getAssetGeneral(0)
    assert.equal(assetBefore[1], accounts[0])
    assert.equal(assetAfter[1], accounts[2])
  })

  it("should not be able to set getAssetLength as non-Owner", async function () {
    let failed = false
    try {
      await assetDb.getAssetListLength({ from: accounts[1] })
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })

  it("should be able to set getAssetLength as Owner", async function () {
    assert.equal((await assetDb.getAssetListLength()).toNumber(), 1)
  })

  it("should not be able to set getCapacityWh as non-Owner", async function () {
    let failed = false
    try {
      await assetDb.getCapacityWh(0, { from: accounts[1] })
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })

  it("should be able to set getCapacityWh as Owner", async function () {
    assert.equal(await assetDb.getCapacityWh(0), 99)
  })

  it("should not be able to get location country as non owner", async function () {
    let failed = false
    try {
      await assetDb.getLocationCountry(0, { from: accounts[1] })
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })


  it("should be able to get location country as owner", async function () {

    let res = await assetDb.getLocationCountry(0)
    assert.equal(web3.toAscii(res).replace(/\0/g, ''), 'USA')
  })

  it("should not be able to get location region as non owner", async function () {
    let failed = false
    try {
      await assetDb.getLocationRegion(0, { from: accounts[1] })
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })


  it("should be able to get location region as owner", async function () {

    let res = await assetDb.getLocationRegion(0)
    assert.equal(web3.toAscii(res).replace(/\0/g, ''), 'Berlin')
  })
  it("should not be able to get operationalSince as non owner", async function () {
    let failed = false
    try {
      await assetDb.getOperationalSince(0, { from: accounts[1] })
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })


  it("should be able to get location operationalSince as owner", async function () {

    let res = await assetDb.getOperationalSince(0)
    assert.equal(res.toNumber(), 54321)
  })


  it("should not be able to get assetOwner as non owner", async function () {
    let failed = false
    try {
      await assetDb.getOwner(0, { from: accounts[1] })
    } catch (ex) {
      failed = true
    }
    assert.isTrue(failed)

  })


  it("should be able to get location assetOwner as owner", async function () {

    let res = await assetDb.getOwner(0)
    assert.equal(res, accounts[2])
  })


})