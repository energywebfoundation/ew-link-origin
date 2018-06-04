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

var CoO = artifacts.require("CoO");
var AssetProducingRegistryLogic = artifacts.require("AssetProducingRegistryLogic")
var CertificateLogic = artifacts.require("CertificateLogic");
var UserDB = artifacts.require("UserDB");
var UserLogic = artifacts.require("UserLogic");

var UserLogicUpdate = artifacts.require("UserLogic")

contract('CoO', function (accounts) {

  var coo;

  it("should get the instances", async function () {
    coo = await CoO.deployed();
    assert.isNotNull(coo)
  })

  it("should have initialized userRegistry successfully", async function () {
    assert.equal(await coo.userRegistry(), UserLogic.address)
  })

  it("ashould have initialized ussetRegistry successfully", async function () {
    assert.equal(await coo.assetProducingRegistry(), AssetProducingRegistryLogic.address)
  })

  it("should have initialized u certificateRegistry successfully", async function () {
    assert.equal(await coo.certificateRegistry(), CertificateLogic.address)
  })

  it("should not be possible to change owner to 0x0", async function () {
    let ownerBefore = await coo.owner()
    try {
      await coo.changeOwner("0x0000000000000000000000000000000000000000")
    } catch (ex) {

    }
    assert.equal(ownerBefore, await coo.owner())
  })

})