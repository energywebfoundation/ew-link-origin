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

var CertificateLogic = artifacts.require("CertificateLogic");
var CertificateDB = artifacts.require("CertificateDB");
var AssetProducingRegistryLogic = artifacts.require("AssetProducingRegistryLogic");
var CoO = artifacts.require("CoO")

contract('CertificateLogic', function (accounts) {

  var certLog,
    certDb,
    assetLogic;

  it("should get the instances", async function () {
    assetLogic = await AssetProducingRegistryLogic.deployed();
    certLog = await CertificateLogic.deployed();
    certDb = await CertificateDB.deployed();
  })

  it("should have executed the constructor successfully", async function () {
    //coo contract in this contract should be the same as the deployed one
    assert.equal(await certLog.cooContract.call(), CoO.address, "should be equal")
  })

  it("should have been initialized successfully", async function () {
    assert.equal(await certLog.certificateDb.call(), CertificateDB.address, "should be equal")
  })

  it("should create a certificate and change the owner owner", async function () {
    //called by asset admin
    //new owner needs to be a user
    await assetLogic.createAsset()
    await assetLogic.initGeneral(
      0,
      accounts[9],
      accounts[0],
      1234567890,
      true,
      { from: accounts[2] })

    await assetLogic.initProducingProperties(0,
      1,
      1000,
      1,
      web3.fromAscii("N.A."),
      web3.fromAscii("N.A."))

    await assetLogic.initLocation(
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


    //log some data and create wh
    await assetLogic.saveSmartMeterRead(0, 10000, false, 0, 10000, false, {
      from: accounts[9]
    })
    //certificate erstellen
    await certLog.createCertificateForAssetOwner(0, 10000, {
      from: accounts[8]
    })

    //get the old owner (for reset)

    let owner = await certLog.getCertificateOwner(0);
    await certLog.changeCertificateOwner(0, accounts[1], {
    });

    let owner2 = await certLog.getCertificateOwner(0);

    assert.notEqual(owner, owner2, "should have changed the owner successfully")

    await certLog.changeCertificateOwner(0, owner, {
      from: accounts[1]
    });

    owner2 = await certLog.getCertificateOwner(0);

    assert.equal(owner, owner2, "should have changed the owner back successfully")

  })

  it("should retire a certificate", async function () {
    var retiredStatusOld = await certLog.isRetired(0)
    assert.isFalse(retiredStatusOld, "should not have been retired")

    await certLog.retireCertificate(0, {
      from: accounts[0]
    })

    var retiredStatusNew = await certLog.isRetired(0)
    assert.isTrue(retiredStatusNew, "should have retired the certificate")
  })

  it("should throw if it is already initialised", async function () {
    var res = false
    try {
      await certLog.init('0x0')
    } catch (ex) {
      res = true
    }
    assert.isTrue(res, "should have thrown an exception because already initialized")
  })

  it("should throw the retirement if it is not the certificate owner who is calling", async function () {
    var res = false
    try {
      await certLog.retireCertificate(0, {
        from: accounts[5]
      })
    } catch (ex) {
      res = true
    }
    assert.isTrue(res, "should have thrown an exception because the wrong caller")
  })

  /// @dev done by asset
  it.skip("should set the asset contract correctly", async function () { })

})